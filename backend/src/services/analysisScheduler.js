// backend/src/services/analysisScheduler.js
const cron        = require('node-cron');
const axios       = require('axios');
const pool        = require('../config/database');
const fileCleanup = require('./fileCleanup');

const ANALYSIS_ENGINE_URL = process.env.ANALYSIS_ENGINE_URL || 'http://localhost:5000';

// Max time (ms) to poll a job before giving up for this run
// (scheduler will pick it up again on next 5-minute tick if still partial)
const MAX_POLL_MS      = 15 * 60 * 1000;  // 15 minutes
const POLL_INTERVAL_MS = 10 * 1000;        // 10 seconds

class AnalysisScheduler {
  constructor() {
    // assignmentId → { jobIds: string[], startedAt: Date }
    this.runningJobs = new Map();
  }

  start() {
    console.log('✅ Analysis Scheduler started');

    // Every 5 minutes: check for assignments past deadline
    cron.schedule('*/5 * * * *', async () => {
      await this._checkPendingAnalyses();
    });

    // Daily at 2 AM: delete files older than 7 days
    cron.schedule('0 2 * * *', async () => {
      await fileCleanup.cleanupOldFiles();
    });
  }

  // ─────────────────────────────────────────────────────────────────────
  // Scheduler tick
  // ─────────────────────────────────────────────────────────────────────

  async _checkPendingAnalyses() {
    try {
      const query = `
        SELECT DISTINCT a.assignment_id, a.primary_language
        FROM assignments a
        JOIN submissions s ON a.assignment_id = s.assignment_id
        WHERE a.analysis_mode = 'after_deadline'
          AND a.due_date < NOW()
          AND s.analysis_status IN ('pending', 'failed')
        LIMIT 10
      `;
      const { rows } = await pool.query(query);

      for (const row of rows) {
        if (!this.runningJobs.has(row.assignment_id)) {
          await this._triggerAssignmentAnalysis(row.assignment_id);
        }
      }
    } catch (err) {
      console.error('[Scheduler] tick error:', err.message);
    }
  }

  // ─────────────────────────────────────────────────────────────────────
  // Trigger + poll
  // ─────────────────────────────────────────────────────────────────────

  async _triggerAssignmentAnalysis(assignmentId) {
    console.log(`[Scheduler] Triggering analysis for assignment ${assignmentId}`);
    this.runningJobs.set(assignmentId, { jobIds: [], startedAt: new Date() });

    try {
      // Group submissions by question
      const groups = await this._groupSubmissionsByQuestion(assignmentId);
      const assignmentRow = await pool.query(
        'SELECT primary_language FROM assignments WHERE assignment_id = $1',
        [assignmentId]
      );
      const language = assignmentRow.rows[0]?.primary_language || 'cpp';

      for (const [questionId, submissions] of Object.entries(groups)) {
        const valid = submissions.filter(s => (s.file_paths || []).length > 0);
        if (valid.length < 2) continue;

        const payload = {
          assignment_id:     assignmentId,
          language,
          extension_weights: null,
          submissions:       valid.map(s => ({
            student_id:    s.student_id,
            submission_id: s.submission_id,
            question_id:   s.question_id ?? null,
            files:         s.file_paths,
          })),
        };

        try {
          const resp = await axios.post(
            `${ANALYSIS_ENGINE_URL}/api/analyze/assignment`,
            payload,
            { timeout: 15000 }
          );
          const jobId = resp.data.job_id;
          this.runningJobs.get(assignmentId).jobIds.push({ jobId, questionId });
          console.log(`[Scheduler] Q${questionId} → job ${jobId}`);

          // Poll this job in the background
          this._pollJob(assignmentId, jobId, questionId);
        } catch (err) {
          console.error(`[Scheduler] Q${questionId} submit error: ${err.message}`);
        }
      }

    } catch (err) {
      console.error(`[Scheduler] trigger error for ${assignmentId}: ${err.message}`);
      this.runningJobs.delete(assignmentId);
    }
  }

  async _pollJob(assignmentId, jobId, questionId) {
    const deadline = Date.now() + MAX_POLL_MS;

    const tick = async () => {
      if (Date.now() > deadline) {
        console.warn(`[Scheduler] job ${jobId} polling timeout — will retry next scheduler tick`);
        this._maybeCloseAssignment(assignmentId);
        return;
      }

      try {
        const resp = await axios.get(
          `${ANALYSIS_ENGINE_URL}/api/analyze/results/${jobId}`,
          { timeout: 5000 }
        );
        const data = resp.data;

        // Save whatever results arrived
        if (data.results && data.results.length > 0) {
          await this._saveResults(assignmentId, questionId, data.results);
        }

        console.log(
          `[Scheduler] job ${jobId} — ${data.status} `
          + `(${data.analyzed_count}/${data.total_pairs}, ${data.progress}%)`
        );

        if (data.status === 'completed' || data.status === 'failed') {
          this._maybeCloseAssignment(assignmentId);
          return;
        }

        // Partial: keep polling
        setTimeout(tick, POLL_INTERVAL_MS);

      } catch (err) {
        console.error(`[Scheduler] poll error for job ${jobId}: ${err.message}`);
        setTimeout(tick, POLL_INTERVAL_MS * 3);  // back off on error
      }
    };

    setTimeout(tick, POLL_INTERVAL_MS);
  }

  _maybeCloseAssignment(assignmentId) {
    const entry = this.runningJobs.get(assignmentId);
    if (!entry) return;

    // Only remove from running map — next scheduler tick will re-check
    // if any submissions are still pending
    this.runningJobs.delete(assignmentId);
    console.log(`[Scheduler] Assignment ${assignmentId} job cycle complete`);
  }

  // ─────────────────────────────────────────────────────────────────────
  // Group submissions by question
  // ─────────────────────────────────────────────────────────────────────

  async _groupSubmissionsByQuestion(assignmentId) {
    const query = `
      SELECT
        s.submission_id,
        s.student_id,
        s.question_id,
        array_agg(cf.file_path ORDER BY cf.uploaded_at ASC)
          FILTER (WHERE cf.file_path IS NOT NULL) AS file_paths
      FROM submissions s
      LEFT JOIN code_files cf ON s.submission_id = cf.submission_id
      WHERE s.assignment_id = $1
      GROUP BY s.submission_id, s.student_id, s.question_id
      ORDER BY s.question_id, s.student_id
    `;
    const { rows } = await pool.query(query, [assignmentId]);

    const groups = {};
    for (const row of rows) {
      const key = row.question_id ?? 'no_question';
      if (!groups[key]) groups[key] = [];
      groups[key].push(row);
    }
    return groups;
  }

  // ─────────────────────────────────────────────────────────────────────
  // Save results to DB
  // ─────────────────────────────────────────────────────────────────────

  async _saveResults(assignmentId, questionId, results) {
    for (const r of results) {
      // r shape from engine:
      // { student_a_id, submission_a_id, student_b_id, submission_b_id,
      //   structural_score, semantic_score, combined_score,
      //   confidence, is_clone, file_a, file_b, details }

      if (!r.is_clone && r.confidence === 'UNLIKELY') continue;

      const client = await pool.connect();
      try {
        await client.query('BEGIN');

        // Upsert analysis_result for submission_a (highest similarity seen)
        const upsertResult = await client.query(
          `INSERT INTO analysis_results
             (submission_id, overall_similarity, type3_score, type4_score,
              hybrid_score, details)
           VALUES ($1, $2, $3, $4, $5, $6)
           ON CONFLICT (submission_id) DO UPDATE
             SET overall_similarity = GREATEST(
                   analysis_results.overall_similarity,
                   EXCLUDED.overall_similarity
                 ),
                 type3_score  = GREATEST(analysis_results.type3_score,  EXCLUDED.type3_score),
                 type4_score  = GREATEST(analysis_results.type4_score,  EXCLUDED.type4_score),
                 hybrid_score = GREATEST(analysis_results.hybrid_score, EXCLUDED.hybrid_score),
                 analyzed_at  = CURRENT_TIMESTAMP
           RETURNING result_id`,
          [
            r.submission_a_id,
            Math.round((r.combined_score    || 0) * 100),
            Math.round((r.structural_score  || 0) * 100),
            Math.round((r.semantic_score    || 0) * 100),
            Math.round((r.combined_score    || 0) * 100),
            JSON.stringify(r.details || {}),
          ]
        );

        const resultId = upsertResult.rows[0].result_id;

        // Ensure submission_a_id < submission_b_id for the DB CHECK constraint
        const [subA, subB] = r.submission_a_id < r.submission_b_id
          ? [r.submission_a_id, r.submission_b_id]
          : [r.submission_b_id, r.submission_a_id];

        // Upsert clone_pair
        await client.query(
          `INSERT INTO clone_pairs
             (result_id, submission_a_id, submission_b_id,
              similarity, clone_type, matching_blocks)
           VALUES ($1, $2, $3, $4, $5, $6)
           ON CONFLICT DO NOTHING`,
          [
            resultId,
            subA,
            subB,
            Math.round((r.combined_score || 0) * 100),
            r.confidence === 'HIGH' ? 'type3' : 'hybrid',
            JSON.stringify({
              file_a:           r.file_a,
              file_b:           r.file_b,
              confidence:       r.confidence,
              structural_score: r.structural_score,
              semantic_score:   r.semantic_score,
              question_id:      questionId,
              ...(r.details || {}),
            }),
          ]
        );

        // Mark submission as completed
        await client.query(
          `UPDATE submissions SET analysis_status = 'completed', analyzed_at = NOW()
           WHERE submission_id = $1`,
          [r.submission_a_id]
        );

        await client.query('COMMIT');
      } catch (err) {
        await client.query('ROLLBACK');
        console.error(`[Scheduler] saveResult error: ${err.message}`);
      } finally {
        client.release();
      }
    }
  }
}

const scheduler = new AnalysisScheduler();
module.exports = scheduler;