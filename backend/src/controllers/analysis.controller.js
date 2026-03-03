// backend/src/controllers/analysis.controller.js
// ── FIXED v2.1 ──
//   1. getPairDetail: Fixed double-multiplication on type scores
//   2. getPairDetail: Added primary_clone_type from matchingBlocks
//   3. getPairDetail: Null-safe access to meta fields

const path    = require('path');
const fs      = require('fs');
const axios   = require('axios');
const pool    = require('../config/database');
const { Submission, AnalysisResult, ClonePair } = require('../models');
const AnalysisService = require('../services/analysisService');

const ANALYSIS_ENGINE_URL = process.env.ANALYSIS_ENGINE_URL || 'http://localhost:8000';

// /app/uploads/foo/bar.cpp  →  /Users/.../backend/uploads/foo/bar.cpp
const toHostPath = (enginePath) => {
  if (!enginePath) return null;
  const uploadsDir = path.join(__dirname, '../../uploads');
  const rel = enginePath.replace(/^\/app\/uploads\/?/, '').replace(/\\/g, '/');
  return path.join(uploadsDir, rel);
};

class AnalysisController {

  // ── Generic file upload analysis ──────────────────────────────────────────
  static async analyzeFiles(req, res) {
    const uploadedPaths = [];
    try {
      if (!req.files || req.files.length === 0) return res.status(400).json({ error: 'No files uploaded' });
      if (req.files.length < 2) return res.status(400).json({ error: 'At least 2 files required' });
      req.files.forEach(f => uploadedPaths.push(f.path));
      let types = {};
      try { types = JSON.parse(req.body.types || '{}'); } catch (_) {}
      const FormData = require('form-data');
      const form = new FormData();
      req.files.forEach(f => form.append('files', fs.createReadStream(f.path), f.originalname));
      form.append('types', JSON.stringify(types));
      form.append('mode', req.body.mode || 'detailed');
      const response = await axios.post(`${ANALYSIS_ENGINE_URL}/api/analyze/detailed`, form,
        { headers: form.getHeaders(), timeout: 300_000 });
      return res.json(response.data);
    } catch (error) {
      if (error.response) return res.status(error.response.status).json(error.response.data || { error: 'Engine error' });
      if (error.code === 'ECONNREFUSED') return res.status(503).json({ error: 'Analysis engine not running' });
      return res.status(500).json({ error: 'File analysis failed', details: error.message });
    } finally {
      uploadedPaths.forEach(p => { try { fs.unlinkSync(p); } catch (_) {} });
    }
  }

  // ── Single submission ────────────────────��────────────────────────────────
  static async analyzeSubmission(req, res) {
    try {
      const { submissionId } = req.params;
      const submission = await Submission.findById(submissionId);
      if (!submission) return res.status(404).json({ error: 'Submission not found' });
      const files = await Submission.getFiles(submissionId);
      if (!files.length) return res.status(400).json({ error: 'No files to analyze' });
      AnalysisService.analyzeSubmission(submissionId, files).catch(console.error);
      res.json({ message: 'Analysis started', submissionId, status: 'processing' });
    } catch (error) {
      res.status(500).json({ error: 'Failed to start analysis', details: error.message });
    }
  }

  // ── Batch assignment — fire and forget, lock inside service ──────────────
  static async analyzeAssignment(req, res) {
    try {
      const { assignmentId } = req.params;
      res.json({ message: 'Analysis started', assignmentId });
      AnalysisService.analyzeAssignment(assignmentId)
        .catch(err => console.error('[Controller] Batch analysis error:', err.message));
    } catch (error) {
      res.status(500).json({ error: 'Failed to start analysis', details: error.message });
    }
  }

  // ── Assignment results ────────────────────────────────────────────────────
  static async getAssignmentResults(req, res) {
    try {
      const { assignmentId } = req.params;
      const threshold = parseFloat(req.query.threshold) || 50;
      const results   = await AnalysisResult.findByAssignment(assignmentId);
      const highSimilarityPairs = await ClonePair.findByAssignment(assignmentId, threshold);
      res.json({ results, highSimilarityPairs });
    } catch (error) {
      res.status(500).json({ error: 'Failed to get results', details: error.message });
    }
  }

  // ── Single submission results ─────────────────────────────────────────────
  static async getSubmissionResults(req, res) {
    try {
      const { submissionId } = req.params;
      const result = await AnalysisResult.findBySubmission(submissionId);
      if (!result) return res.status(404).json({ error: 'Analysis results not found' });
      const clonePairs = await ClonePair.findByResult(result.result_id);
      res.json({ ...result, clonePairs });
    } catch (error) {
      res.status(500).json({ error: 'Failed to get results', details: error.message });
    }
  }

  // ── GET /api/analysis/pair/:pairId — full detail WITH file content ────────
  static async getPairDetail(req, res) {
    try {
      const { pairId } = req.params;

      const { rows } = await pool.query(`
        SELECT
          cp.*,
          ua.first_name || ' ' || ua.last_name AS student_a_name,
          ub.first_name || ' ' || ub.last_name AS student_b_name,
          sa.student_id AS student_a_id,
          sb.student_id AS student_b_id
        FROM clone_pairs cp
        JOIN submissions sa ON cp.submission_a_id = sa.submission_id
        JOIN submissions sb ON cp.submission_b_id = sb.submission_id
        JOIN users ua ON sa.student_id = ua.user_id
        JOIN users ub ON sb.student_id = ub.user_id
        WHERE cp.pair_id = $1
      `, [pairId]);

      if (!rows.length) return res.status(404).json({ error: 'Pair not found' });
      const pair = rows[0];

      let meta = {};
      try {
        meta = typeof pair.matching_blocks === 'string'
          ? JSON.parse(pair.matching_blocks)
          : (pair.matching_blocks || {});
      } catch (_) {}

      // Read actual source files from disk
      const readFile = (enginePath) => {
        try {
          const hostPath = toHostPath(enginePath);
          if (hostPath && fs.existsSync(hostPath)) return fs.readFileSync(hostPath, 'utf-8');
        } catch (_) {}
        return null;
      };

      const sourceA = readFile(meta.file_a);
      const sourceB = readFile(meta.file_b);

      // Build fragments
      let fragments = [];
      if (meta.fragments && Array.isArray(meta.fragments) && meta.fragments.length > 0) {
        fragments = meta.fragments;
      } else if (sourceA !== null || sourceB !== null) {
        fragments = [{
          file_a:       meta.file_a ? path.basename(meta.file_a) : 'File A',
          file_b:       meta.file_b ? path.basename(meta.file_b) : 'File B',
          func_a:       null,
          func_b:       null,
          start_a:      1,
          end_a:        sourceA ? sourceA.split('\n').length : 0,
          start_b:      1,
          end_b:        sourceB ? sourceB.split('\n').length : 0,
          source_a:     sourceA || '// File not found',
          source_b:     sourceB || '// File not found',
          similarity:   pair.similarity / 100,
          similar_lines: [],
        }];
      }

      // ── FIX #1: Normalise scores correctly ──────────────────────────────
      // DB stores similarity as 0-100 (percentage).
      // meta stores scores as 0.0-1.0 (floats from engine).
      // Frontend expects 0.0-1.0.
      //
      // OLD BUG: n(meta.type1_score * 100) → double-converted!
      //   meta.type1_score is already 0.0-1.0
      //   Multiplying by 100 then dividing by 100 = same value BUT
      //   n() does toFixed(4) which truncates precision
      //
      // WORSE: if meta.type1_score is undefined, undefined * 100 = NaN
      //
      // NEW: Read directly from meta (already 0-1), with safe fallback
      const safeScore = (v) => {
        if (v == null || isNaN(v)) return 0;
        // If the value is > 1, it's stored as percentage, convert to 0-1
        if (v > 1) return parseFloat((v / 100).toFixed(4));
        return parseFloat(v.toFixed(4));
      };

      res.json({
        pair_id:            pair.pair_id,
        similarity:         parseFloat((pair.similarity / 100).toFixed(4)),
        clone_type:         pair.clone_type,
        primary_clone_type: meta.primary_clone_type || pair.clone_type,  // ← NEW
        detected_at:        pair.detected_at,
        submission_a_id:    pair.submission_a_id,
        submission_b_id:    pair.submission_b_id,
        student_a_name:     pair.student_a_name,
        student_b_name:     pair.student_b_name,
        student_a_id:       pair.student_a_id,
        student_b_id:       pair.student_b_id,
        type1_score:        safeScore(meta.type1_score),       // ← FIXED
        type2_score:        safeScore(meta.type2_score),       // ← FIXED
        structural_score:   safeScore(meta.structural_score),  // ← FIXED
        semantic_score:     safeScore(meta.semantic_score),    // ← FIXED
        confidence:         meta.confidence ?? 'UNKNOWN',
        file_a:             meta.file_a ? path.basename(meta.file_a) : null,
        file_b:             meta.file_b ? path.basename(meta.file_b) : null,
        fragments,
        matching_blocks:    meta,
      });

    } catch (error) {
      console.error('getPairDetail error:', error);
      res.status(500).json({ error: 'Failed to get pair detail', details: error.message });
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