const pool = require('../config/database');

class AnalysisResult {
  static async create({ submissionId, scores, details = {} }) {
    const {
      overallSimilarity,
      type1Score,
      type2Score,
      type3Score,
      type4Score,
      hybridScore
    } = scores;

    const query = `
      INSERT INTO analysis_results (
        submission_id, overall_similarity, type1_score, type2_score,
        type3_score, type4_score, hybrid_score, details
      )
      VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
      ON CONFLICT (submission_id) 
      DO UPDATE SET 
        overall_similarity = EXCLUDED.overall_similarity,
        type1_score = EXCLUDED.type1_score,
        type2_score = EXCLUDED.type2_score,
        type3_score = EXCLUDED.type3_score,
        type4_score = EXCLUDED.type4_score,
        hybrid_score = EXCLUDED.hybrid_score,
        details = EXCLUDED.details,
        analyzed_at = CURRENT_TIMESTAMP
      RETURNING *
    `;

    const values = [
      submissionId, overallSimilarity, type1Score, type2Score,
      type3Score, type4Score, hybridScore, JSON.stringify(details)
    ];

    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findBySubmission(submissionId) {
    const query = `
      SELECT ar.*,
             s.assignment_id, s.student_id,
             u.first_name || ' ' || u.last_name as student_name
      FROM analysis_results ar
      JOIN submissions s ON ar.submission_id = s.submission_id
      JOIN users u ON s.student_id = u.user_id
      WHERE ar.submission_id = $1
    `;
    const result = await pool.query(query, [submissionId]);
    return result.rows[0];
  }

  static async findByAssignment(assignmentId) {
    const query = `
      SELECT ar.*, s.student_id,
             u.first_name || ' ' || u.last_name as student_name
      FROM analysis_results ar
      JOIN submissions s ON ar.submission_id = s.submission_id
      JOIN users u ON s.student_id = u.user_id
      WHERE s.assignment_id = $1
      ORDER BY ar.overall_similarity DESC
    `;
    const result = await pool.query(query, [assignmentId]);
    return result.rows;
  }

  static async getHighSimilarity(assignmentId, threshold = 70.0) {
    const query = `
      SELECT ar.*, s.student_id,
             u.first_name || ' ' || u.last_name as student_name,
             u.email as student_email
      FROM analysis_results ar
      JOIN submissions s ON ar.submission_id = s.submission_id
      JOIN users u ON s.student_id = u.user_id
      WHERE s.assignment_id = $1 AND ar.overall_similarity >= $2
      ORDER BY ar.overall_similarity DESC
    `;
    const result = await pool.query(query, [assignmentId, threshold]);
    return result.rows;
  }

  static async delete(resultId) {
    const query = 'DELETE FROM analysis_results WHERE result_id = $1 RETURNING *';
    const result = await pool.query(query, [resultId]);
    return result.rows[0];
  }
}

module.exports = AnalysisResult;