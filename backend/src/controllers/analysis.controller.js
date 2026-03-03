const path    = require('path');
const fs      = require('fs');
const axios   = require('axios');
const { Submission, AnalysisResult, ClonePair } = require('../models');
const AnalysisService = require('../services/analysisService');

const ANALYSIS_ENGINE_URL = process.env.ANALYSIS_ENGINE_URL || 'http://localhost:5000';

class AnalysisController {

  // ── Generic file upload analysis (no assignment) ──────────────────────────
  // Called by CodeAnalysis.jsx via POST /api/analysis/files
  // Forwards uploaded files to the analysis engine and returns results directly.
  static async analyzeFiles(req, res) {
    const uploadedPaths = [];
    try {
      if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'No files uploaded' });
      }
      if (req.files.length < 2) {
        return res.status(400).json({ error: 'At least 2 files required for comparison' });
      }

      req.files.forEach(f => uploadedPaths.push(f.path));

      // Parse detector toggles sent from the frontend
      let types = {};
      try { types = JSON.parse(req.body.types || '{}'); } catch (_) {}

      const mode = req.body.mode || 'detailed';

      // Forward files to the Python analysis engine as multipart
      const FormData = require('form-data');
      const form = new FormData();

      req.files.forEach(f => {
        form.append('files', fs.createReadStream(f.path), f.originalname);
      });
      form.append('types', JSON.stringify(types));
      form.append('mode',  mode);

      const response = await axios.post(
        `${ANALYSIS_ENGINE_URL}/api/analyze/detailed`,
        form,
        {
          headers: form.getHeaders(),
          timeout: 300_000, // 5 min for large batches
        }
      );

      // Return engine response directly to frontend
      return res.json(response.data);

    } catch (error) {
      console.error('[AnalysisController.analyzeFiles]', error.message);

      if (error.response) {
        // Engine returned an error — pass it through
        return res.status(error.response.status).json(
          error.response.data || { error: 'Analysis engine error' }
        );
      }
      if (error.code === 'ECONNREFUSED') {
        return res.status(503).json({ error: 'Analysis engine is not running. Start it with: python main.py' });
      }
      return res.status(500).json({ error: 'File analysis failed', details: error.message });

    } finally {
      // Clean up temp files regardless of success/failure
      uploadedPaths.forEach(p => {
        try { fs.unlinkSync(p); } catch (_) {}
      });
    }
  }

  // ── Single submission analysis ────────────────────────────────────────────
  static async analyzeSubmission(req, res) {
    try {
      const { submissionId } = req.params;
      const submission = await Submission.findById(submissionId);
      if (!submission) {
        return res.status(404).json({ error: 'Submission not found' });
      }
      const files = await Submission.getFiles(submissionId);
      if (files.length === 0) {
        return res.status(400).json({ error: 'No files to analyze' });
      }
      AnalysisService.analyzeSubmission(submissionId, files)
        .catch(err => console.error('Analysis error:', err));
      res.json({ message: 'Analysis started', submissionId, status: 'processing' });
    } catch (error) {
      console.error('analyzeSubmission error:', error);
      res.status(500).json({ error: 'Failed to start analysis', details: error.message });
    }
  }

  // ── Batch assignment analysis ─────────────────────────────────────────────
  static async analyzeAssignment(req, res) {
    try {
      const { assignmentId } = req.params;
      AnalysisService.analyzeAssignment(assignmentId)
        .catch(err => console.error('Batch analysis error:', err));
      res.json({ message: 'Batch analysis started', assignmentId });
    } catch (error) {
      console.error('analyzeAssignment error:', error);
      res.status(500).json({ error: 'Failed to start analysis', details: error.message });
    }
  }

  // ── Get results for single submission ─────────────────────────────────────
  static async getSubmissionResults(req, res) {
    try {
      const { submissionId } = req.params;
      const result = await AnalysisResult.findBySubmission(submissionId);
      if (!result) {
        return res.status(404).json({ error: 'Analysis results not found' });
      }
      const clonePairs = await ClonePair.findByResult(result.result_id);
      res.json({ ...result, clonePairs });
    } catch (error) {
      console.error('getSubmissionResults error:', error);
      res.status(500).json({ error: 'Failed to get results', details: error.message });
    }
  }

  // ── Get results for assignment ────────────────────────────────────────────
  static async getAssignmentResults(req, res) {
    try {
      const { assignmentId } = req.params;
      const { threshold }    = req.query;
      const results          = await AnalysisResult.findByAssignment(assignmentId);
      let highSimilarityPairs = [];
      if (threshold) {
        highSimilarityPairs = await ClonePair.findByAssignment(
          assignmentId,
          parseFloat(threshold)
        );
      }
      res.json({ results, highSimilarityPairs });
    } catch (error) {
      console.error('getAssignmentResults error:', error);
      res.status(500).json({ error: 'Failed to get results', details: error.message });
    }
  }

  // ── Health check ──────────────────────────────────────────────────────────
  static async checkHealth(req, res) {
    try {
      const health = await AnalysisService.checkHealth();
      res.json(health);
    } catch (error) {
      res.status(500).json({ error: 'Health check failed', details: error.message });
    }
  }
}

module.exports = AnalysisController;