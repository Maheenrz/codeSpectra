const pool = require('../config/database');

class Report {
  static async create({ assignmentId, generatedById, format, fileUrl }) {
    const query = `
      INSERT INTO reports (assignment_id, generated_by_id, format, file_url)
      VALUES ($1, $2, $3, $4)
      RETURNING *
    `;
    const values = [assignmentId, generatedById, format, fileUrl];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findById(reportId) {
    const query = `
      SELECT r.*,
             a.title as assignment_title,
             c.course_name,
             u.first_name || ' ' || u.last_name as generator_name
      FROM reports r
      JOIN assignments a ON r.assignment_id = a.assignment_id
      JOIN courses c ON a.course_id = c.course_id
      JOIN users u ON r.generated_by_id = u.user_id
      WHERE r.report_id = $1
    `;
    const result = await pool.query(query, [reportId]);
    return result.rows[0];
  }

  static async findByAssignment(assignmentId) {
    const query = `
      SELECT r.*,
             u.first_name || ' ' || u.last_name as generator_name
      FROM reports r
      JOIN users u ON r.generated_by_id = u.user_id
      WHERE r.assignment_id = $1
      ORDER BY r.created_at DESC
    `;
    const result = await pool.query(query, [assignmentId]);
    return result.rows;
  }

  static async delete(reportId) {
    const query = 'DELETE FROM reports WHERE report_id = $1 RETURNING *';
    const result = await pool.query(query, [reportId]);
    return result.rows[0];
  }
}

module.exports = Report;