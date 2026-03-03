// backend/src/models/ClonePair.js
const pool = require('../config/database');

class ClonePair {
  static async create({ resultId, submissionAId, submissionBId, similarity, cloneType, matchingBlocks = [] }) {
    const query = `
      INSERT INTO clone_pairs
        (result_id, submission_a_id, submission_b_id, similarity, clone_type, matching_blocks)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING *
    `;
    const result = await pool.query(query, [
      resultId, submissionAId, submissionBId,
      similarity, cloneType, JSON.stringify(matchingBlocks),
    ]);
    return result.rows[0];
  }

  static async findByResult(resultId) {
    const query = `
      SELECT cp.*,
             ua.first_name || ' ' || ua.last_name AS student_a_name,
             ub.first_name || ' ' || ub.last_name AS student_b_name,
             sa.student_id AS student_a_id,
             sb.student_id AS student_b_id
      FROM clone_pairs cp
      JOIN submissions sa ON cp.submission_a_id = sa.submission_id
      JOIN submissions sb ON cp.submission_b_id = sb.submission_id
      JOIN users ua ON sa.student_id = ua.user_id
      JOIN users ub ON sb.student_id = ub.user_id
      WHERE cp.result_id = $1
      ORDER BY cp.similarity DESC
    `;
    const result = await pool.query(query, [resultId]);
    return result.rows;
  }

  static async findByAssignment(assignmentId, threshold = 70.0) {
    const query = `
      SELECT cp.*,
             ua.first_name || ' ' || ua.last_name AS student_a_name,
             ub.first_name || ' ' || ub.last_name AS student_b_name,
             sa.student_id AS student_a_id,
             sb.student_id AS student_b_id
      FROM clone_pairs cp
      JOIN analysis_results ar ON cp.result_id = ar.result_id
      JOIN submissions sa ON cp.submission_a_id = sa.submission_id
      JOIN submissions sb ON cp.submission_b_id = sb.submission_id
      JOIN users ua ON sa.student_id = ua.user_id
      JOIN users ub ON sb.student_id = ub.user_id
      WHERE sa.assignment_id = $1
        AND cp.similarity >= $2
      ORDER BY cp.similarity DESC
    `;
    const result = await pool.query(query, [assignmentId, threshold]);
    return result.rows;
  }

  /**
   * Richer query used by the instructor report page.
   * Returns pairs with question_id extracted from matching_blocks JSONB.
   */
  static async findByAssignmentDetailed(assignmentId, threshold = 50.0) {
    const query = `
      SELECT
        cp.pair_id,
        cp.similarity,
        cp.clone_type,
        cp.detected_at,
        cp.matching_blocks,
        (cp.matching_blocks->>'question_id')::int      AS question_id,
        (cp.matching_blocks->>'confidence')            AS confidence,
        (cp.matching_blocks->>'structural_score')::float AS structural_score,
        (cp.matching_blocks->>'semantic_score')::float   AS semantic_score,
        ua.first_name || ' ' || ua.last_name AS student_a_name,
        ua.email                             AS student_a_email,
        ub.first_name || ' ' || ub.last_name AS student_b_name,
        ub.email                             AS student_b_email,
        sa.submission_id AS submission_a_id,
        sb.submission_id AS submission_b_id
      FROM clone_pairs cp
      JOIN analysis_results ar ON cp.result_id = ar.result_id
      JOIN submissions sa ON cp.submission_a_id = sa.submission_id
      JOIN submissions sb ON cp.submission_b_id = sb.submission_id
      JOIN users ua ON sa.student_id = ua.user_id
      JOIN users ub ON sb.student_id = ub.user_id
      WHERE sa.assignment_id = $1
        AND cp.similarity >= $2
      ORDER BY cp.similarity DESC
    `;
    const result = await pool.query(query, [assignmentId, threshold]);
    return result.rows;
  }

  static async delete(pairId) {
    const query = 'DELETE FROM clone_pairs WHERE pair_id = $1 RETURNING *';
    const result = await pool.query(query, [pairId]);
    return result.rows[0];
  }
}

module.exports = ClonePair;