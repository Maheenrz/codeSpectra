const pool = require('../config/database');

class Enrollment {
  static async enroll(studentId, courseId) {
    const query = `
      INSERT INTO enrollments (student_id, course_id)
      VALUES ($1, $2)
      ON CONFLICT (student_id, course_id) DO NOTHING
      RETURNING *
    `;
    const result = await pool.query(query, [studentId, courseId]);
    return result.rows[0];
  }

  static async unenroll(studentId, courseId) {
    const query = `
      DELETE FROM enrollments 
      WHERE student_id = $1 AND course_id = $2
      RETURNING *
    `;
    const result = await pool.query(query, [studentId, courseId]);
    return result.rows[0];
  }

  static async getStudentCourses(studentId) {
    const query = `
      SELECT c.*, 
             u.first_name || ' ' || u.last_name as instructor_name,
             e.enrolled_at,
             COUNT(DISTINCT a.assignment_id) as assignment_count
      FROM enrollments e
      JOIN courses c ON e.course_id = c.course_id
      LEFT JOIN users u ON c.instructor_id = u.user_id
      LEFT JOIN assignments a ON c.course_id = a.course_id
      WHERE e.student_id = $1
      GROUP BY c.course_id, u.first_name, u.last_name, e.enrolled_at
      ORDER BY e.enrolled_at DESC
    `;
    const result = await pool.query(query, [studentId]);
    return result.rows;
  }

  static async getCourseStudents(courseId) {
    const query = `
      SELECT u.user_id, u.email, u.first_name, u.last_name, e.enrolled_at
      FROM enrollments e
      JOIN users u ON e.student_id = u.user_id
      WHERE e.course_id = $1
      ORDER BY u.last_name, u.first_name
    `;
    const result = await pool.query(query, [courseId]);
    return result.rows;
  }

  static async isEnrolled(studentId, courseId) {
    const query = `
      SELECT * FROM enrollments 
      WHERE student_id = $1 AND course_id = $2
    `;
    const result = await pool.query(query, [studentId, courseId]);
    return result.rows.length > 0;
  }
}

module.exports = Enrollment;