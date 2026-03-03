const pool = require('../config/database');

class Submission {
  static async create(assignmentId, studentId) {
    const query = `
      INSERT INTO submissions (assignment_id, student_id, analysis_status)
      VALUES ($1, $2, 'pending')
      ON CONFLICT (assignment_id, student_id) 
      DO UPDATE SET submitted_at = CURRENT_TIMESTAMP
      RETURNING *
    `;
    const result = await pool.query(query, [assignmentId, studentId]);
    return result.rows[0];
  }

  static async findById(submissionId) {
    const query = `
      SELECT s.*,
             u.first_name || ' ' || u.last_name as student_name,
             u.email as student_email,
             a.title as assignment_title,
             c.course_name, c.course_code
      FROM submissions s
      JOIN users u ON s.student_id = u.user_id
      JOIN assignments a ON s.assignment_id = a.assignment_id
      JOIN courses c ON a.course_id = c.course_id
      WHERE s.submission_id = $1
    `;
    const result = await pool.query(query, [submissionId]);
    return result.rows[0];
  }

  static async findByAssignmentAndStudent(assignmentId, studentId) {
    const query = `
      SELECT * FROM submissions 
      WHERE assignment_id = $1 AND student_id = $2
    `;
    const result = await pool.query(query, [assignmentId, studentId]);
    return result.rows[0];
  }

  static async findByAssignment(assignmentId) {
    const query = `
      SELECT s.*,
             u.first_name || ' ' || u.last_name as student_name,
             u.email as student_email,
             COUNT(cf.file_id) as file_count
      FROM submissions s
      JOIN users u ON s.student_id = u.user_id
      LEFT JOIN code_files cf ON s.submission_id = cf.submission_id
      WHERE s.assignment_id = $1
      GROUP BY s.submission_id, u.first_name, u.last_name, u.email
      ORDER BY s.submitted_at DESC
    `;
    const result = await pool.query(query, [assignmentId]);
    return result.rows;
  }

  static async findByStudent(studentId) {
    const query = `
      SELECT s.*,
             a.title as assignment_title,
             a.due_date,
             c.course_name, c.course_code,
             COUNT(cf.file_id) as file_count
      FROM submissions s
      JOIN assignments a ON s.assignment_id = a.assignment_id
      JOIN courses c ON a.course_id = c.course_id
      LEFT JOIN code_files cf ON s.submission_id = cf.submission_id
      WHERE s.student_id = $1
      GROUP BY s.submission_id, a.title, a.due_date, c.course_name, c.course_code
      ORDER BY s.submitted_at DESC
    `;
    const result = await pool.query(query, [studentId]);
    return result.rows;
  }

  static async updateStatus(submissionId, status) {
    const query = `
      UPDATE submissions 
      SET analysis_status = $1, 
          analyzed_at = CASE WHEN $1 = 'completed' THEN CURRENT_TIMESTAMP ELSE analyzed_at END
      WHERE submission_id = $2
      RETURNING *
    `;
    const result = await pool.query(query, [status, submissionId]);
    return result.rows[0];
  }

  static async delete(submissionId) {
    const query = 'DELETE FROM submissions WHERE submission_id = $1 RETURNING submission_id';
    const result = await pool.query(query, [submissionId]);
    return result.rows[0];
  }

  // Get files for submission
  static async getFiles(submissionId) {
    const query = `
      SELECT * FROM code_files 
      WHERE submission_id = $1
      ORDER BY uploaded_at DESC
    `;
    const result = await pool.query(query, [submissionId]);
    return result.rows;
  }
}

module.exports = Submission;