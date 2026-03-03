const pool = require('../config/database');

class Grade {
  static async create({ submissionId, autoScore, instructorOverride, penalty = 0, feedback, gradedById }) {
    const query = `
      INSERT INTO grades (submission_id, auto_score, instructor_override, penalty, feedback, graded_by_id)
      VALUES ($1, $2, $3, $4, $5, $6)
      ON CONFLICT (submission_id)
      DO UPDATE SET
        instructor_override = EXCLUDED.instructor_override,
        penalty = EXCLUDED.penalty,
        feedback = EXCLUDED.feedback,
        graded_by_id = EXCLUDED.graded_by_id,
        graded_at = CURRENT_TIMESTAMP
      RETURNING *
    `;

    const values = [submissionId, autoScore, instructorOverride, penalty, feedback, gradedById];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findBySubmission(submissionId) {
    const query = `
      SELECT g.*,
             u.first_name || ' ' || u.last_name as grader_name
      FROM grades g
      LEFT JOIN users u ON g.graded_by_id = u.user_id
      WHERE g.submission_id = $1
    `;
    const result = await pool.query(query, [submissionId]);
    return result.rows[0];
  }

  static async findByAssignment(assignmentId) {
    const query = `
      SELECT g.*,
             s.student_id,
             u.first_name || ' ' || u.last_name as student_name,
             grader.first_name || ' ' || grader.last_name as grader_name
      FROM grades g
      JOIN submissions s ON g.submission_id = s.submission_id
      JOIN users u ON s.student_id = u.user_id
      LEFT JOIN users grader ON g.graded_by_id = grader.user_id
      WHERE s.assignment_id = $1
      ORDER BY g.graded_at DESC
    `;
    const result = await pool.query(query, [assignmentId]);
    return result.rows;
  }

  static async update(gradeId, updates) {
    const fields = [];
    const values = [];
    let paramCount = 1;

    const allowedFields = ['instructor_override', 'penalty', 'feedback', 'graded_by_id'];
    Object.keys(updates).forEach(key => {
      if (allowedFields.includes(key) && updates[key] !== undefined) {
        fields.push(`${key} = $${paramCount}`);
        values.push(updates[key]);
        paramCount++;
      }
    });

    if (fields.length === 0) return null;

    values.push(gradeId);
    const query = `
      UPDATE grades 
      SET ${fields.join(', ')}, graded_at = CURRENT_TIMESTAMP
      WHERE grade_id = $${paramCount}
      RETURNING *
    `;

    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async delete(gradeId) {
    const query = 'DELETE FROM grades WHERE grade_id = $1 RETURNING *';
    const result = await pool.query(query, [gradeId]);
    return result.rows[0];
  }
}

module.exports = Grade;