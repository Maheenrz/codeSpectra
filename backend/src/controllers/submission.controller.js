const { Submission, CodeFile, Assignment, AnalysisResult } = require('../models');
const crypto  = require('crypto');
const fs      = require('fs').promises;
const fsSync  = require('fs');
const path    = require('path');
const AdmZip  = require('adm-zip');

const CODE_EXTENSIONS = new Set([
  '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
  '.java', '.py',
  '.js', '.jsx', '.ts', '.tsx'
]);

// Extracts a ZIP into a sibling directory and returns all code file paths found inside.
// Skips macOS __MACOSX metadata directories and .DS_Store files.
async function extractZip(zipPath) {
  const extractDir = zipPath.replace('.zip', '_extracted');
  fsSync.mkdirSync(extractDir, { recursive: true });

  const zip = new AdmZip(zipPath);
  zip.extractAllTo(extractDir, true);

  const codeFiles = [];
  function walk(dir) {
    const entries = fsSync.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
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

      // If the student is re-submitting, clean up their old files from disk and DB
      // so we're not comparing stale code. Also reset analysis_status to 'pending'
      // so the next analysis run picks them up again.
      const existingSubmission = await Submission.findByAssignmentAndStudent(assignmentId, studentId);
      if (existingSubmission) {
        const oldFiles = await Submission.getFiles(existingSubmission.submission_id);
        for (const file of oldFiles) {
          try { await fs.unlink(file.file_path); } catch (_) {}
          const extractedDir = file.file_path.replace(path.extname(file.file_path), '_extracted');
          try { await fs.rm(extractedDir, { recursive: true, force: true }); } catch (_) {}
        }
        await CodeFile.deleteBySubmission(existingSubmission.submission_id);
      }

      const submission = await Submission.create(assignmentId, studentId);

      if (existingSubmission) {
        await Submission.updateStatus(submission.submission_id, 'pending');
      }

      // Resolve the final list of code files — uploaded files might be
      // individual source files or a ZIP, or a mix of both.
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

      const savedFiles = [];
      for (const filePath of allCodePaths) {
        const fileBuffer = await fs.readFile(filePath);
        const fileHash   = crypto.createHash('sha256').update(fileBuffer).digest('hex');
        const filename   = path.basename(filePath);

        const codeFile = await CodeFile.create({
          submissionId: submission.submission_id,
          filename,
          filePath,
          fileHash,
          fileSize: fileBuffer.length,
        });
        savedFiles.push(codeFile);
      }

      res.status(201).json({
        message:         existingSubmission ? 'Submission updated successfully' : 'Submission created successfully',
        submission,
        files:           savedFiles,
        total_files:     savedFiles.length,
        submission_type: uploadedFiles.some(f => f.originalname.endsWith('.zip')) ? 'zip' : 'files',
        is_resubmission: !!existingSubmission,
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

  // Returns submission data alongside its analysis results when available.
  // Used by the submission detail page so it can show similarity scores inline.
  static async getSubmissionWithAnalysis(req, res) {
    try {
      const { submissionId } = req.params;
      const submission = await Submission.findById(submissionId);
      if (!submission) {
        return res.status(404).json({ error: 'Submission not found' });
      }
      const files = await Submission.getFiles(submissionId);

      let analysisResult = null;
      try {
        analysisResult = await AnalysisResult.findBySubmission(submissionId);
      } catch (_) {}

      res.json({
        ...submission,
        files,
        analysis:           analysisResult || null,
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
