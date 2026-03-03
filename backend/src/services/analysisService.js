// backend/src/services/analysisService.js
const axios = require("axios");
const pool  = require("../config/database");
const path  = require("path");

const ENGINE            = process.env.ANALYSIS_ENGINE_URL || "http://localhost:8000";
const POLL_INTERVAL_MS  = 3000;
const MAX_POLL_ATTEMPTS = 100;

// ─── IN-PROCESS LOCK ──────────────────────────────────────────────────────────
// Prevents duplicate runs when user clicks "Analyze" multiple times.
// Key = assignmentId string, value = timestamp when run started.
const _runningJobs = new Map();

class AnalysisService {

  static async analyzeAssignment(assignmentId) {
    const key = String(assignmentId);

    if (_runningJobs.has(key)) {
      const elapsed = Math.round((Date.now() - _runningJobs.get(key)) / 1000);
      console.log(`[Analysis] ⚠️  Already running for assignment ${assignmentId} (${elapsed}s ago) — ignoring duplicate`);
      return { status: "already_running" };
    }

    _runningJobs.set(key, Date.now());
    console.log(`[Analysis] 🔒 Lock acquired — assignment ${assignmentId}`);

    try {
      return await AnalysisService._doAnalyze(assignmentId);
    } finally {
      _runningJobs.delete(key);
      console.log(`[Analysis] 🔓 Lock released — assignment ${assignmentId}`);
    }
  }

  static async _doAnalyze(assignmentId) {
    console.log(`[Analysis] Starting assignment ${assignmentId}`);

    const { rows: [assignment] } = await pool.query(
      "SELECT * FROM assignments WHERE assignment_id = $1", [assignmentId]
    );
    if (!assignment) throw new Error(`Assignment ${assignmentId} not found`);

    const { rows } = await pool.query(`
      SELECT
        s.submission_id,
        s.student_id,
        u.first_name || ' ' || u.last_name AS student_name,
        array_agg(cf.file_path ORDER BY cf.uploaded_at ASC)
          FILTER (WHERE cf.file_path IS NOT NULL) AS file_paths
      FROM submissions s
      JOIN users u ON s.student_id = u.user_id
      LEFT JOIN code_files cf ON s.submission_id = cf.submission_id
      WHERE s.assignment_id = $1
        AND s.analysis_status IN ('pending','failed','processing')
      GROUP BY s.submission_id, s.student_id, u.first_name, u.last_name
      ORDER BY s.student_id
    `, [assignmentId]);

    if (!rows.length) {
      console.log("[Analysis] No pending submissions");
      return { status: "skipped", reason: "no_pending_submissions" };
    }

    const valid = rows.filter(r => r.file_paths?.length > 0);
    if (valid.length < 2) {
      console.log("[Analysis] Need at least 2 submissions with files");
      return { status: "skipped", reason: "insufficient_submissions" };
    }

    console.log(`[Analysis] ${valid.length} students — pooling all files`);

    await pool.query(
      "UPDATE submissions SET analysis_status='processing' WHERE submission_id = ANY($1)",
      [valid.map(r => r.submission_id)]
    );

    const uploadsBase = path.join(__dirname, "../../uploads");
    const toEngine = (hostPath) => {
      const rel = hostPath
        .replace(uploadsBase + path.sep, "")
        .replace(uploadsBase + "/", "")
        .replace(/\\/g, "/");
      return `/app/uploads/${rel}`;
    };

    const submissions = valid.map(r => ({
      student_id:    r.student_id,
      submission_id: r.submission_id,
      student_name:  r.student_name,
      files:         r.file_paths.map(toEngine),
    }));

    const { data: job } = await axios.post(
      `${ENGINE}/api/analyze/assignment`,
      { assignment_id: parseInt(assignmentId), language: assignment.primary_language || "cpp", submissions },
      { timeout: 15000 }
    );

    console.log(`[Analysis] Job ${job.job_id} submitted — polling…`);
    const results = await AnalysisService._pollUntilDone(job.job_id);

    if (!results) {
      await pool.query(
        "UPDATE submissions SET analysis_status='failed' WHERE submission_id = ANY($1)",
        [valid.map(r => r.submission_id)]
      );
      throw new Error("Analysis job timed out or failed");
    }

    const subMap = {};
    valid.forEach(r => { subMap[r.submission_id] = r; });

    const clonePairs = results.clone_pairs || results.results || [];
    console.log(`[Analysis] Engine returned ${clonePairs.length} pairs`);

    // ── WIPE OLD RESULTS before saving fresh ones (prevents 3x duplicates) ─
    await pool.query(`
      DELETE FROM clone_pairs WHERE pair_id IN (
        SELECT cp.pair_id FROM clone_pairs cp
        JOIN analysis_results ar ON cp.result_id = ar.result_id
        JOIN submissions s ON ar.submission_id = s.submission_id
        WHERE s.assignment_id = $1
      )
    `, [assignmentId]);

    await pool.query(`
      DELETE FROM analysis_results
      WHERE submission_id IN (
        SELECT submission_id FROM submissions WHERE assignment_id = $1
      )
    `, [assignmentId]);

    let saved = 0;
    for (const pair of clonePairs) {
      const ok = await AnalysisService._saveClonePair(pair, subMap);
      if (ok) saved++;
    }

    await pool.query(
      "UPDATE submissions SET analysis_status='completed', analyzed_at=NOW() WHERE submission_id = ANY($1)",
      [valid.map(r => r.submission_id)]
    );

    console.log(`[Analysis] ✅ Done — ${saved}/${clonePairs.length} pairs saved`);
    return { status: "completed", clone_pairs: saved };
  }

  static async _pollUntilDone(jobId) {
    for (let i = 0; i < MAX_POLL_ATTEMPTS; i++) {
      await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
      try {
        const { data } = await axios.get(`${ENGINE}/api/analyze/results/${jobId}`, { timeout: 10000 });
        console.log(`[Analysis] ${jobId} — ${data.status} ${data.progress?.toFixed(1)}% (${data.analyzed_count}/${data.total_pairs})`);
        if (data.status === "completed" || data.status === "partial") return data;
        if (data.status === "failed") { console.error(`[Analysis] Job failed: ${data.error}`); return null; }
      } catch (err) {
        console.warn(`[Analysis] Poll ${i + 1} error: ${err.message}`);
      }
    }
    return null;
  }

  static async _saveClonePair(pair, subMap) {
    try {
      const subAId = pair.submission_a_id;
      const subBId = pair.submission_b_id;
      if (!subAId || !subBId) return false;

      const [loId, hiId] = subAId < subBId ? [subAId, subBId] : [subBId, subAId];
      const score = pair.combined_score ?? ((pair.structural_score ?? 0) * 0.5 + (pair.semantic_score ?? 0) * 0.5);
      const similarityPct = parseFloat((score * 100).toFixed(2));
      const cloneType     = AnalysisService._inferCloneType(pair);

      const { rows: [result] } = await pool.query(`
        INSERT INTO analysis_results (
          submission_id, overall_similarity,
          type1_score, type2_score, type3_score, type4_score,
          hybrid_score, details
        ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
        ON CONFLICT (submission_id) DO UPDATE SET
          overall_similarity = GREATEST(analysis_results.overall_similarity, EXCLUDED.overall_similarity),
          analyzed_at = CURRENT_TIMESTAMP
        RETURNING result_id
      `, [
        loId, similarityPct,
        parseFloat(((pair.type1_score      ?? 0) * 100).toFixed(2)),
        parseFloat(((pair.type2_score      ?? 0) * 100).toFixed(2)),
        parseFloat(((pair.structural_score ?? 0) * 100).toFixed(2)),
        parseFloat(((pair.semantic_score   ?? 0) * 100).toFixed(2)),
        similarityPct,
        JSON.stringify({ file_a: pair.file_a, file_b: pair.file_b }),
      ]);

      const matchingBlocks = {
        confidence:       pair.confidence       ?? "UNKNOWN",
        structural_score: pair.structural_score ?? 0,
        semantic_score:   pair.semantic_score   ?? 0,
        type1_score:      pair.type1_score      ?? 0,
        type2_score:      pair.type2_score      ?? 0,
        combined_score:   score,
        file_a:           pair.file_a ?? null,   // full /app/uploads/... path
        file_b:           pair.file_b ?? null,
        student_a_id:     pair.student_a_id ?? null,
        student_b_id:     pair.student_b_id ?? null,
        student_a_name:   subMap[subAId]?.student_name ?? null,
        student_b_name:   subMap[subBId]?.student_name ?? null,
        details:          pair.details ?? {},
      };

      await pool.query(`
        INSERT INTO clone_pairs (
          result_id, submission_a_id, submission_b_id,
          similarity, clone_type, matching_blocks
        ) VALUES ($1,$2,$3,$4,$5,$6)
        ON CONFLICT DO NOTHING
      `, [result.result_id, loId, hiId, similarityPct, cloneType, JSON.stringify(matchingBlocks)]);

      return true;
    } catch (err) {
      console.warn(`[Analysis] Failed to save pair: ${err.message}`);
      return false;
    }
  }

  static _inferCloneType(pair) {
    const t1 = pair.type1_score ?? 0, t2 = pair.type2_score ?? 0;
    const t3 = pair.structural_score ?? 0, t4 = pair.semantic_score ?? 0;
    const mx = Math.max(t1, t2, t3, t4);
    if (mx === 0) return "hybrid";
    if (mx === t1) return "type1"; if (mx === t2) return "type2";
    if (mx === t3) return "type3"; return "type4";
  }

  static async analyzeSubmission(submissionId, files) {
    const FormData = require("form-data");
    const fs = require("fs");
    const form = new FormData();
    for (const file of files) form.append("files", fs.createReadStream(file.file_path), file.filename);
    const { data } = await axios.post(`${ENGINE}/api/analyze/detailed`, form,
      { headers: form.getHeaders(), timeout: 120000 });
    return data;
  }

  static async checkHealth() {
    try {
      const { data } = await axios.get(`${ENGINE}/health`, { timeout: 5000 });
      return data;
    } catch (err) { return { status: "unavailable", error: err.message }; }
  }
}

module.exports = AnalysisService;
