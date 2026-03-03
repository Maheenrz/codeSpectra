// backend/src/controllers/submission.controller.js
// ── FIXED v2.1 ──
//   1. On re-submission (UPSERT), reset analysis_status → 'pending'
//      so the student appears in the next analysis run
//   2. Delete old code_files on re-submission to avoid stale data
//   3. Added getSubmissionWithAnalysis for the frontend detail view

const { Submission, CodeFile, Assignment, AnalysisResult } = require('../models');
const crypto = require('crypto');
const fs = require('fs').promises;
const fsSync = require('fs');
const path = require('path');
const AdmZip = require('adm-zip');

const CODE_EXTENSIONS = new Set([
  '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
  '.java', '.py',
  '.js', '.jsx', '.ts', '.tsx'
]);

// ─────────────────────────────────────────────────────────────────
// Zip extraction helper
// Extracts a zip into a subfolder next to it, returns all code paths
// ─────────────────────────────────────────────────────────────────
async function extractZip(zipPath) {
  const extractDir = zipPath.replace('.zip', '_extracted');
  fsSync.mkdirSync(extractDir, { recursive: true });

  const zip = new AdmZip(zipPath);
  zip.extractAllTo(extractDir, true);

  // Collect all code files recursively
  const codeFiles = [];
  function walk(dir) {
    const entries = fsSync.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      // Skip macOS junk
      if (entry.name === '__MACOSX' || entry.name === '.DS_Store') continue;
      if (entry.isDirectory()) {
        walk(full);
      } else if (CODE_EXTENSIONS.has(path.extname(entry.name).toLowerCase())) {
        codeFiles.push(full);
      }
    }
  }
  walk(extractDir);
  return codeFiles;
}

class SubmissionController {

  static async createSubmission(req, res) {
    try {
      const { assignmentId } = req.body;
      const studentId = req.user.userId;
      const uploadedFiles = req.files;

      if (!assignmentId) {
        return res.status(400).json({ error: 'Assignment ID is required' });
      }
      if (!uploadedFiles || uploadedFiles.length === 0) {
        return res.status(400).json({ error: 'No files uploaded' });
      }

      const assignment = await Assignment.findById(assignmentId);
      if (!assignment) {
        return res.status(404).json({ error: 'Assignment not found' });
      }

      // ── FIX #1: Check for existing submission ────────────────────────
      // If the student already submitted, we need to:
      //   a) Delete old code_files from disk and DB
      //   b) Reset analysis_status to 'pending' so re-analysis picks it up
      const existingSubmission = await Submission.findByAssignmentAndStudent(assignmentId, studentId);
      if (existingSubmission) {
        // Delete old files from disk
        const oldFiles = await Submission.getFiles(existingSubmission.submission_id);
        for (const file of oldFiles) {
          try { await fs.unlink(file.file_path); } catch (_) {}
          // Also try to clean up extracted directories
          const extractedDir = file.file_path.replace(path.extname(file.file_path), '_extracted');
          try { await fs.rm(extractedDir, { recursive: true, force: true }); } catch (_) {}
        }
        // Delete old code_files from DB
        await CodeFile.deleteBySubmission(existingSubmission.submission_id);
      }

      // Create or update submission record
      // The Submission.create UPSERT already handles re-submission, but we need
      // to ensure analysis_status resets to 'pending'
      const submission = await Submission.create(assignmentId, studentId);

      // ── FIX #2: Explicitly reset analysis_status on re-submission ────
      // The UPSERT in Submission.create doesn't reset analysis_status, so we do it here
      if (existingSubmission) {
        await Submission.updateStatus(submission.submission_id, 'pending');
      }

      // ── Resolve final list of code files ────────────────────────────
      // multer gives us the uploaded files. Each may be:
      //   a) a code file (.cpp, .java, etc.) → use directly
      //   b) a zip file (.zip) → extract, use the code files inside
      const allCodePaths = [];

      for (const file of uploadedFiles) {
        const ext = path.extname(file.originalname).toLowerCase();
        if (ext === '.zip') {
          try {
            const extracted = await extractZip(file.path);
            if (extracted.length === 0) {
              return res.status(400).json({
                error: `Zip file "${file.originalname}" contains no supported code files (.cpp, .java, .py, etc.)`
              });
            }
            allCodePaths.push(...extracted);
          } catch (err) {
            return res.status(400).json({
              error: `Failed to extract zip "${file.originalname}": ${err.message}`
            });
          }
        } else {
          allCodePaths.push(file.path);
        }
      }

      // ── Save each code file to DB ────────────────────────────────────
      const savedFiles = [];
      for (const filePath of allCodePaths) {
        const fileBuffer = await fs.readFile(filePath);
        const fileHash = crypto.createHash('sha256').update(fileBuffer).digest('hex');
        const filename = path.basename(filePath);

        const codeFile = await CodeFile.create({
          submissionId: submission.submission_id,
          filename:     filename,
          filePath:     filePath,
          fileHash:     fileHash,
          fileSize:     fileBuffer.length,
        });
        savedFiles.push(codeFile);
      }

      res.status(201).json({
        message:          existingSubmission ? 'Submission updated successfully' : 'Submission created successfully',
        submission,
        files:            savedFiles,
        total_files:      savedFiles.length,
        submission_type:  uploadedFiles.some(f => f.originalname.endsWith('.zip'))
                          ? 'zip' : 'files',
        is_resubmission:  !!existingSubmission,
      });

    } catch (error) {
      console.error('Create submission error:', error);
      res.status(500).json({ error: 'Failed to create submission', details: error.message });
    }
  }

  static async getSubmissionById(req, res) {
    try {
      const { submissionId } = req.params;
      const submission = await Submission.findById(submissionId);
      if (!submission) {
        return res.status(404).json({ error: 'Submission not found' });
      }
      const files = await Submission.getFiles(submissionId);
      res.json({ ...submission, files });
    } catch (error) {
      res.status(500).json({ error: 'Failed to get submission', details: error.message });
    }
  }

  // ── NEW: Get submission with its analysis results ──────────────────────
  static async getSubmissionWithAnalysis(req, res) {
    try {
      const { submissionId } = req.params;
      const submission = await Submission.findById(submissionId);
      if (!submission) {
        return res.status(404).json({ error: 'Submission not found' });
      }
      const files = await Submission.getFiles(submissionId);

      // Try to get analysis results if they exist
      let analysisResult = null;
      try {
        analysisResult = await AnalysisResult.findBySubmission(submissionId);
      } catch (_) {}

      res.json({
        ...submission,
        files,
        analysis: analysisResult || null,
        analysis_available: !!analysisResult,
      });
    } catch (error) {
      res.status(500).json({ error: 'Failed to get submission', details: error.message });
    }
  }

  static async getAssignmentSubmissions(req, res) {
    try {
      const { assignmentId } = req.params;
      const submissions = await Submission.findByAssignment(assignmentId);
      res.json(submissions);
    } catch (error) {
      res.status(500).json({ error: 'Failed to get submissions', details: error.message });
    }
  }

  static async getStudentSubmissions(req, res) {
    try {
      const studentId = req.user.userId;
      const submissions = await Submission.findByStudent(studentId);
      res.json(submissions);
    } catch (error) {
      res.status(500).json({ error: 'Failed to get submissions', details: error.message });
    }
  }

  static async deleteSubmission(req, res) {
    try {
      const { submissionId } = req.params;
      const files = await Submission.getFiles(submissionId);
      for (const file of files) {
        try { await fs.unlink(file.file_path); } catch (_) {}
      }
      const submission = await Submission.delete(submissionId);
      if (!submission) {
        return res.status(404).json({ error: 'Submission not found' });
      }
      res.json({ message: 'Submission deleted successfully' });
    } catch (error) {
      res.status(500).json({ error: 'Failed to delete submission', details: error.message });
    }
  }
}

module.exports = SubmissionController;