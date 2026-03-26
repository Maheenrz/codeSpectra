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
  // Accepts any mix of .cpp/.java/.py/.js/.ts + .zip files.
  // ZIPs are extracted in-process (adm-zip) before forwarding to the engine.
  // Result is normalised so the frontend always gets a consistent shape.
  // The `types` form field (JSON) controls which clone types are returned.
  static async analyzeFiles(req, res) {
    // Parse the detection-type toggles sent by the frontend
    // { t1: bool, t2: bool, t3: bool, t4: bool }
    // Map to canonical type names so we can filter the engine's results.
    let enabledTypes = { type1: true, type2: true, type3: true, type4: false };
    try {
      const raw = req.body?.types ? JSON.parse(req.body.types) : {};
      enabledTypes = {
        type1: raw.t1 !== false,
        type2: raw.t2 !== false,
        type3: raw.t3 !== false,
        type4: raw.t4 !== false,
      };
    } catch (_) { /* use defaults */ }
    const uploadedPaths = [];
    const extractedPaths = [];
    const tempDir = path.join(__dirname, '../../uploads/temp');

    try {
      // Ensure temp dir exists
      if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });

      if (!req.files || req.files.length === 0)
        return res.status(400).json({ error: 'No files uploaded' });

      req.files.forEach(f => uploadedPaths.push(f.path));

      // ── Extract any ZIPs ─────────────────────────────────────────────
      const AdmZip  = require('adm-zip');
      const CODE_EXT = new Set(['.cpp','.c','.h','.hpp','.cc','.cxx','.java','.py','.js','.jsx','.ts','.tsx']);
      const allCodePaths = [];

      for (const f of req.files) {
        const ext = path.extname(f.originalname).toLowerCase();
        if (ext === '.zip') {
          // Extract into a sub-folder alongside the zip
          const extractDir = f.path + '_extracted';
          fs.mkdirSync(extractDir, { recursive: true });
          extractedPaths.push(extractDir);
          try {
            const zip = new AdmZip(f.path);
            zip.extractAllTo(extractDir, true);

            // Walk extracted files — recursively extract nested ZIPs too.
            // This handles the "class ZIP" pattern:
            //   class.zip
            //   ├── student1.zip   ← extracted here
            //   ├── student2.zip
            //   └── student3/      ← or plain folders
            const walk = (dir) => {
              for (const entry of fs.readdirSync(dir)) {
                const full = path.join(dir, entry);
                const stat = fs.statSync(full);
                if (stat.isDirectory()) {
                  walk(full);
                } else if (path.extname(entry).toLowerCase() === '.zip') {
                  // Nested student ZIP — extract it in place
                  const nestedDir = full + '_nested';
                  fs.mkdirSync(nestedDir, { recursive: true });
                  extractedPaths.push(nestedDir);
                  try {
                    const nestedZip = new AdmZip(full);
                    nestedZip.extractAllTo(nestedDir, true);
                    walk(nestedDir);   // collect code files from student's zip
                  } catch (nestedErr) {
                    console.warn(`[Analysis] Nested ZIP extraction failed for ${entry}: ${nestedErr.message}`);
                  }
                } else if (CODE_EXT.has(path.extname(entry).toLowerCase())) {
                  allCodePaths.push(full);
                }
              }
            };
            walk(extractDir);
          } catch (zipErr) {
            console.warn(`[Analysis] ZIP extraction failed for ${f.originalname}: ${zipErr.message}`);
          }
        } else if (CODE_EXT.has(ext)) {
          allCodePaths.push(f.path);
        }
      }

      if (allCodePaths.length < 2)
        return res.status(400).json({ error: 'At least 2 code files required (after ZIP extraction)' });

      // ── Forward code files to the engine ─────────────────────────────
      const FormData = require('form-data');
      const form = new FormData();
      allCodePaths.forEach(p => {
        form.append('files', fs.createReadStream(p), path.basename(p));
      });

      const response = await axios.post(
        `${ANALYSIS_ENGINE_URL}/api/analyze/detailed`,
        form,
        { headers: form.getHeaders(), timeout: 300_000 }
      );

      // ── Filter by enabled detection types ─────────────────────────────
      // Engine returns all_pairs with primary_clone_type on each pair.
      // Only return pairs whose clone type was enabled by the user's toggles.
      const engineData = response.data;
      if (engineData.all_pairs && Array.isArray(engineData.all_pairs)) {
        engineData.all_pairs = engineData.all_pairs.filter(pair => {
          const ct = pair.primary_clone_type || 'none';
          if (ct === 'none') return false;
          if (ct === 'type1' && !enabledTypes.type1) return false;
          if (ct === 'type2' && !enabledTypes.type2) return false;
          if (ct === 'type3' && !enabledTypes.type3) return false;
          if (ct === 'type4' && !enabledTypes.type4) return false;
          return true;
        });
        // Re-compute statistics over filtered pairs so the frontend
        // stats cards (Total Pairs, Critical, High, Avg) are accurate.
        const fp = engineData.all_pairs;
        if (engineData.statistics) {
          const scoreOf = p => p.combined_score ?? p.structural_score ?? 0;
          engineData.statistics.total_pairs_after_filter = fp.length;
          engineData.statistics.enabled_types = enabledTypes;
        }
      }
      return res.json(engineData);

    } catch (error) {
      if (error.response)
        return res.status(error.response.status).json(error.response.data || { error: 'Engine error' });
      if (error.code === 'ECONNREFUSED')
        return res.status(503).json({ error: 'Analysis engine not running. Make sure Docker containers are up.' });
      return res.status(500).json({ error: 'File analysis failed', details: error.message });
    } finally {
      // Clean up all uploaded files
      uploadedPaths.forEach(p => { try { fs.unlinkSync(p); } catch (_) {} });
      // Clean up extracted ZIP directories
      extractedPaths.forEach(dir => {
        try { fs.rmSync(dir, { recursive: true, force: true }); } catch (_) {}
      });
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
      // Return detection settings so the frontend can display which
      // types were enabled when analysis was run for this assignment.
      let assignment_settings = null;
      try {
        const { rows: [asgn] } = await pool.query(
          `SELECT enable_type1, enable_type2, enable_type3, enable_type4,
                  high_similarity_threshold, medium_similarity_threshold
           FROM assignments WHERE assignment_id = $1`,
          [assignmentId]
        );
        if (asgn) {
          assignment_settings = {
            type1:            asgn.enable_type1,
            type2:            asgn.enable_type2,
            type3:            asgn.enable_type3,
            type4:            asgn.enable_type4,
            high_threshold:   asgn.high_similarity_threshold,
            medium_threshold: asgn.medium_similarity_threshold,
          };
        }
      } catch (_) {}

      res.json({ results, highSimilarityPairs, assignment_settings });
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

  // ── CSV report: upload files → engine runs analysis + generates report ────
  // Proxies to POST /api/report/csv on the Python engine.
  // Extracts ZIPs (same as analyzeFiles), then streams the CSV back.
  static async proxyReportCsv(req, res) {
    const uploadedPaths  = [];
    const extractedDirs  = [];
    const tempDir = path.join(__dirname, '../../uploads/temp');

    try {
      if (!fs.existsSync(tempDir)) fs.mkdirSync(tempDir, { recursive: true });
      if (!req.files || req.files.length === 0)
        return res.status(400).json({ error: 'No files uploaded' });

      req.files.forEach(f => uploadedPaths.push(f.path));

      // ── Extract ZIPs (same logic as analyzeFiles) ───────────────────
      const AdmZip   = require('adm-zip');
      const CODE_EXT = new Set(['.cpp','.c','.h','.hpp','.cc','.cxx','.java','.py','.js','.jsx','.ts','.tsx']);
      const allCodePaths = [];

      for (const f of req.files) {
        const ext = path.extname(f.originalname).toLowerCase();
        if (ext === '.zip') {
          const extractDir = f.path + '_extracted';
          fs.mkdirSync(extractDir, { recursive: true });
          extractedDirs.push(extractDir);
          try {
            const zip = new AdmZip(f.path);
            zip.extractAllTo(extractDir, true);
            const walk = (dir) => {
              for (const entry of fs.readdirSync(dir)) {
                const full = path.join(dir, entry);
                if (fs.statSync(full).isDirectory()) walk(full);
                else if (CODE_EXT.has(path.extname(entry).toLowerCase())) allCodePaths.push(full);
              }
            };
            walk(extractDir);
          } catch (zipErr) {
            console.warn(`[CSV] ZIP extraction failed: ${zipErr.message}`);
          }
        } else if (CODE_EXT.has(ext)) {
          allCodePaths.push(f.path);
        }
      }

      if (allCodePaths.length < 2)
        return res.status(400).json({ error: 'At least 2 code files required for CSV report' });

      // ── Forward to engine /api/report/csv ─────────────────────────
      const { assignment_id = '', language = 'cpp', detailed = 'true' } = req.query;
      const FormData = require('form-data');
      const form = new FormData();
      allCodePaths.forEach(p => form.append('files', fs.createReadStream(p), path.basename(p)));

      const engineUrl = `${ANALYSIS_ENGINE_URL}/api/report/csv?assignment_id=${assignment_id}&language=${language}&detailed=${detailed}`;
      const response  = await axios.post(engineUrl, form, {
        headers:      form.getHeaders(),
        responseType: 'stream',
        timeout:      300_000,
      });

      const filename = `codespectra_report_${assignment_id || 'analysis'}_${Date.now()}.csv`;
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
      response.data.pipe(res);

    } catch (error) {
      if (error.code === 'ECONNREFUSED')
        return res.status(503).json({ error: 'Analysis engine not running' });
      return res.status(500).json({ error: 'CSV report failed', details: error.message });
    } finally {
      uploadedPaths.forEach(p => { try { fs.unlinkSync(p); } catch (_) {} });
      extractedDirs.forEach(d => { try { fs.rmSync(d, { recursive: true, force: true }); } catch (_) {} });
    }
  }

  // ── CSV from a completed async assignment job ──────────────────────
  static async proxyJobCsv(req, res) {
    try {
      const { jobId } = req.params;
      const { assignment_id = '', language = 'cpp' } = req.query;
      const engineUrl = `${ANALYSIS_ENGINE_URL}/api/report/csv/${jobId}?assignment_id=${assignment_id}&language=${language}`;
      const response  = await axios.get(engineUrl, { responseType: 'stream', timeout: 30_000 });
      const filename  = `codespectra_assignment_${assignment_id || jobId}_${Date.now()}.csv`;
      res.setHeader('Content-Type', 'text/csv');
      res.setHeader('Content-Disposition', `attachment; filename="${filename}"`);
      response.data.pipe(res);
    } catch (error) {
      return res.status(500).json({ error: 'CSV job export failed', details: error.message });
    }
  }

  // ── Class ZIP: upload zip → engine kicks off async job → return job_id ──
  // The engine's /api/analyze/zip endpoint handles:
  //   - class.zip → {student1.zip, student2.zip, ...}  (Structure A)
  //   - class.zip → {student1/, student2/, ...}         (Structure B)
  //   - project.zip (flat files)                          (Structure C)
  static async analyzeClassZip(req, res) {
    const uploadedPath = req.file?.path;
    try {
      if (!req.file) return res.status(400).json({ error: 'No ZIP file uploaded' });
      if (!req.file.originalname.toLowerCase().endsWith('.zip'))
        return res.status(400).json({ error: 'Only .zip files accepted on this endpoint' });

      // Proxy the zip directly to the engine
      const FormData = require('form-data');
      const form = new FormData();
      form.append('file', fs.createReadStream(uploadedPath), req.file.originalname);

      const response = await axios.post(
        `${ANALYSIS_ENGINE_URL}/api/analyze/zip`,
        form,
        { headers: form.getHeaders(), timeout: 60_000 },
      );

      return res.json(response.data);
    } catch (error) {
      console.error('[analyzeClassZip]', error.message);
      if (error.code === 'ECONNREFUSED')
        return res.status(503).json({ error: 'Analysis engine not running' });
      const detail = error.response?.data || error.message;
      return res.status(500).json({ error: 'Class ZIP analysis failed', details: detail });
    } finally {
      if (uploadedPath) { try { fs.unlinkSync(uploadedPath); } catch (_) {} }
    }
  }

  // ── Poll class ZIP job results from the engine ————————————————
  static async getZipResults(req, res) {
    try {
      const { jobId } = req.params;
      const response = await axios.get(
        `${ANALYSIS_ENGINE_URL}/api/analyze/results/${jobId}`,
        { timeout: 10_000 },
      );
      return res.json(response.data);
    } catch (error) {
      if (error.response?.status === 404)
        return res.status(404).json({ error: `Job ${req.params.jobId} not found` });
      if (error.code === 'ECONNREFUSED')
        return res.status(503).json({ error: 'Analysis engine not running' });
      return res.status(500).json({ error: 'Failed to poll job results', details: error.message });
    }
  }
}

module.exports = AnalysisController;