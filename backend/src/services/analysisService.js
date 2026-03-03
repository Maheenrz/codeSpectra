// backend/src/services/analysisService.js
const axios = require('axios');
const pool = require('../config/database');
const { Submission, AnalysisResult, ClonePair } = require('../models');

const ANALYSIS_ENGINE_URL = process.env.ANALYSIS_ENGINE_URL || 'http://localhost:5000';

class AnalysisService {

  /**
   * Trigger cross-student analysis for a whole assignment.
   *
   * FLAT-POOL APPROACH (no question grouping):
   * All files from ALL students are pooled together as one batch.
   * The engine's language-aware grouping (build_same_language_pairs)
   * ensures only same-language files are compared.
   * A fragment in Student A's linked-list.cpp is compared against
   * ALL other students' .cpp files — detector finds similarities
   * regardless of which "question" the file belonged to.
   */
  static async analyzeAssignment(assignmentId) {
    try {
      console.log('[AnalysisService] Starting flat-pool analysis for assignment ' + assignmentId);

      const assignmentQuery = 'SELECT * FROM assignments WHERE assignment_id = $1';
      const assignmentResult = await pool.query(assignmentQuery, [assignmentId]);
      if (!assignmentResult.rows.length) throw new Error('Assignment ' + assignmentId + ' not found');
      const assignment = assignmentResult.rows[0];

      // Fetch ALL submissions with files — no question_id grouping
      const submissionsQuery = `
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
          AND s.analysis_status IN ('pending', 'failed')
        GROUP BY s.submission_id, s.student_id, u.first_name, u.last_name
        ORDER BY s.student_id
      `;
      const submissionsResult = await pool.query(submissionsQuery, [assignmentId]);
      if (!submissionsResult.rows.length) {
        console.log('[AnalysisService] No pending submissions');
        return { status: 'skipped', reason: 'no_pending_submissions' };
      }

      const validSubmissions = submissionsResult.rows.filter(
        r => r.file_paths && r.file_paths.length > 0
      );
      if (validSubmissions.length < 2) {
        console.log('[AnalysisService] Need at least 2 submissions with files');
        return { status: 'skipped', reason: 'insufficient_submissions' };
      }

      console.log('[AnalysisService] Pooling ' + validSubmissions.length + ' students for flat comparison');

      // Mark processing
      const subIds = validSubmissions.map(r => r.submission_id);
      await pool.query(
        'UPDATE submissions SET analysis_status = \'processing\' WHERE submission_id = ANY($1)',
        [subIds]
      );

      // Build payload — flat list, no question grouping
      const submissionsPayload = validSubmissions.map(r => ({
        student_id:    r.student_id,
        submission_id: r.submission_id,
        student_name:  r.student_name,
        files:         r.file_paths,
      }));

      // Send to engine
      const response = await axios.post(
        ANALYSIS_ENGINE_URL + '/api/analyze/assignment',
        {
          assignment_id: parseInt(assignmentId),
          language:      assignment.primary_language || 'cpp',
          submissions:   submissionsPayload,
        },
        { timeout: 20000 }
      );

      console.log('[AnalysisService] Job submitted: ' + JSON.stringify(response.data));
      return { status: 'submitted', job: response.data };

    } catch (error) {
      console.error('[AnalysisService] analyzeAssignment error:', error.message);
      throw error;
    }
  }

  static async analyzeSubmission(submissionId, files) {
    try {
      await Submission.updateStatus(submissionId, 'processing');
      const FormData = require('form-data');
      const fs = require('fs');
      const form = new FormData();
      for (const file of files) {
        form.append('files', fs.createReadStream(file.file_path), file.filename);
      }
      const response = await axios.post(
        ANALYSIS_ENGINE_URL + '/api/analyze/detailed',
        form,
        { headers: form.getHeaders(), timeout: 120000 }
      );
      const data = response.data;
      const result = await AnalysisResult.create({
        submissionId,
        scores: {
          overallSimilarity: data.statistics?.overall?.high_similarity || 0,
          type1Score: 0, type2Score: 0,
          type3Score: data.statistics?.structural?.high || 0,
          type4Score: data.statistics?.semantic?.high || 0,
          hybridScore: 0,
        },
        details: data,
      });
      await Submission.updateStatus(submissionId, 'completed');
      return result;
    } catch (error) {
      console.error('[AnalysisService] analyzeSubmission error:', error.message);
      await Submission.updateStatus(submissionId, 'failed');
      throw error;
    }
  }

  static async checkHealth() {
    try {
      const response = await axios.get(ANALYSIS_ENGINE_URL + '/health', { timeout: 5000 });
      return response.data;
    } catch (error) {
      return { status: 'unavailable', error: error.message };
    }
  }
}

module.exports = AnalysisService;
