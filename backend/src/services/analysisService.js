const axios = require("axios");
const pool  = require("../config/database");
const path  = require("path");

const ENGINE            = process.env.ANALYSIS_ENGINE_URL || "http://localhost:5000";
const POLL_INTERVAL_MS  = 3000;
const MAX_POLL_ATTEMPTS = 100;

// Simple in-process lock so we don't kick off two analysis runs for the
// same assignment at the same time (e.g. instructor double-clicks Analyze).
const _runningJobs = new Map();

class AnalysisService {

  static async analyzeAssignment(assignmentId) {
    const key = String(assignmentId);

    if (_runningJobs.has(key)) {
      const elapsed = Math.round((Date.now() - _runningJobs.get(key)) / 1000);
      console.log(`[Analysis] Already running for assignment ${assignmentId} (${elapsed}s ago) — skipping`);
      return { status: "already_running" };
    }

    _runningJobs.set(key, Date.now());
    console.log(`[Analysis] Starting — assignment ${assignmentId}`);

    try {
      return await AnalysisService._doAnalyze(assignmentId);
    } finally {
      _runningJobs.delete(key);
      console.log(`[Analysis] Done — assignment ${assignmentId}`);
    }
  }

  static async _doAnalyze(assignmentId) {
    const { rows: [assignment] } = await pool.query(
      "SELECT * FROM assignments WHERE assignment_id = $1", [assignmentId]
    );
    if (!assignment) throw new Error(`Assignment ${assignmentId} not found`);

    const enabledTypes = {
      type1: assignment.enable_type1 !== false,
      type2: assignment.enable_type2 !== false,
      type3: assignment.enable_type3 !== false,
      type4: assignment.enable_type4 !== false,
    };

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

    console.log(`[Analysis] ${valid.length} students queued`);

    await pool.query(
      "UPDATE submissions SET analysis_status='processing' WHERE submission_id = ANY($1)",
      [valid.map(r => r.submission_id)]
    );

    // Path translation for Docker setups:
    // When the analysis engine runs in a container it sees /app/uploads/... but the
    // backend's upload directory is somewhere on the host. ANALYSIS_ENGINE_UPLOADS_BASE
    // lets us remap the paths before sending them to the engine.
    // If both services run locally (no Docker), just leave ANALYSIS_ENGINE_UPLOADS_BASE unset.
    const uploadsBase     = path.join(__dirname, "../../uploads");
    const engineUploadsBase = process.env.ANALYSIS_ENGINE_UPLOADS_BASE;

    const toEngine = (hostPath) => {
      if (engineUploadsBase) {
        const rel = hostPath
          .replace(uploadsBase + path.sep, "")
          .replace(uploadsBase + "/", "")
          .replace(/\\/g, "/");
        return `${engineUploadsBase}/${rel}`;
      }
      return hostPath;
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

    console.log(`[Analysis] Job ${job.job_id} submitted`);
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

    const rawPairs = results.clone_pairs || results.results || [];
    console.log(`[Analysis] Engine returned ${rawPairs.length} pairs`);

    // Drop pairs whose clone type the instructor didn't enable,
    // and also drop anything classified as 'none'.
    const clonePairs = rawPairs.filter(pair => {
      const ct = pair.primary_clone_type || 'none';
      if (ct === 'none')                          return false;
      if (ct === 'type1' && !enabledTypes.type1)  return false;
      if (ct === 'type2' && !enabledTypes.type2)  return false;
      if (ct === 'type3' && !enabledTypes.type3)  return false;
      if (ct === 'type4' && !enabledTypes.type4)  return false;
      return true;
    });
    console.log(`[Analysis] ${clonePairs.length}/${rawPairs.length} pairs kept after type filter`);

    // Wipe old results first so we don't accumulate duplicates across re-runs.
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

    console.log(`[Analysis] ${saved}/${clonePairs.length} pairs saved`);
    return { status: "completed", clone_pairs: saved };
  }

  static async _pollUntilDone(jobId) {
    for (let i = 0; i < MAX_POLL_ATTEMPTS; i++) {
      await new Promise(r => setTimeout(r, POLL_INTERVAL_MS));
      try {
        const { data } = await axios.get(`${ENGINE}/api/analyze/results/${jobId}`, { timeout: 10000 });
        console.log(`[Analysis] ${jobId} — ${data.status} ${data.progress?.toFixed(1)}%`);
        if (data.status === "completed" || data.status === "partial") return data;
        if (data.status === "failed") {
          console.error(`[Analysis] Job failed: ${data.error}`);
          return null;
        }
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

      // Always store pairs with the lower ID first — some queries rely on this ordering.
      const [loId, hiId] = subAId < subBId ? [subAId, subBId] : [subBId, subAId];

      const t1 = pair.type1_score      ?? 0;
      const t2 = pair.type2_score      ?? 0;
      const t3 = pair.structural_score ?? 0;
      const t4 = pair.semantic_score   ?? 0;

      // effective_score comes from the engine's own weighting and takes precedence.
      // Fall back to the highest confident individual score when it's absent.
      let score;
      if (pair.effective_score != null && pair.effective_score > 0) {
        score = pair.effective_score;
      } else if (t1 >= 0.95) {
        score = t1;
      } else if (t2 >= 0.65) {
        score = t2;
      } else {
        score = pair.combined_score ?? t3 ?? 0;
      }

      const similarityPct = parseFloat((score * 100).toFixed(2));
      const cloneType = pair.primary_clone_type || AnalysisService._inferCloneType(pair);

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
        parseFloat((t1 * 100).toFixed(2)),
        parseFloat((t2 * 100).toFixed(2)),
        parseFloat((t3 * 100).toFixed(2)),
        parseFloat((t4 * 100).toFixed(2)),
        similarityPct,
        JSON.stringify({ file_a: pair.file_a, file_b: pair.file_b }),
      ]);

      const matchingBlocks = {
        confidence:         pair.confidence         ?? "UNKNOWN",
        primary_clone_type: cloneType,
        structural_score:   t3,
        semantic_score:     t4,
        type1_score:        t1,
        type2_score:        t2,
        combined_score:     score,
        file_a:             pair.file_a             ?? null,
        file_b:             pair.file_b             ?? null,
        student_a_id:       pair.student_a_id       ?? null,
        student_b_id:       pair.student_b_id       ?? null,
        student_a_name:     subMap[subAId]?.student_name ?? null,
        student_b_name:     subMap[subBId]?.student_name ?? null,
        details:            pair.details            ?? {},
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

  // Infer the most specific clone type when the engine doesn't provide one.
  // Based on Roy & Cordy 2007: Type-1 is the most specific (exact copy),
  // Type-4 is the most general (semantic similarity only).
  // We report the most specific type that clears its threshold.
  static _inferCloneType(pair) {
    const t1 = pair.type1_score      ?? 0;
    const t2 = pair.type2_score      ?? 0;
    const t3 = pair.structural_score ?? 0;
    const t4 = pair.semantic_score   ?? 0;

    if (t1 >= 0.95) return "type1";
    if (t2 >= 0.80) return "type2";
    if (t3 >= 0.50) return "type3";
    if (t4 >= 0.60) return "type4";
    return "none";
  }

  static async analyzeSubmission(submissionId, files) {
    const FormData = require("form-data");
    const fs = require("fs");
    const form = new FormData();
    for (const file of files) {
      form.append("files", fs.createReadStream(file.file_path), file.filename);
    }
    const { data } = await axios.post(`${ENGINE}/api/analyze/detailed`, form,
      { headers: form.getHeaders(), timeout: 120000 });
    return data;
  }

  static async checkHealth() {
    try {
      const { data } = await axios.get(`${ENGINE}/health`, { timeout: 5000 });
      return data;
    } catch (err) {
      return { status: "unavailable", error: err.message };
    }
  }
}

module.exports = AnalysisService;
