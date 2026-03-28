const pool = require('../config/database');

class Course {
  static async create({ courseCode, courseName, instructorId, semester, year }) {
    const query = `
      INSERT INTO courses (course_code, course_name, instructor_id, semester, year)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    const result = await pool.query(query, [courseCode, courseName, instructorId, semester, year]);
    return result.rows[0];
  }

  static async findById(courseId) {
    const query = `
      SELECT c.*,
             u.first_name || ' ' || u.last_name AS instructor_name,
             u.email AS instructor_email
      FROM courses c
      LEFT JOIN users u ON c.instructor_id = u.user_id
      WHERE c.course_id = $1
    `;
    const result = await pool.query(query, [courseId]);
    return result.rows[0];
  }

  static async findByInstructor(instructorId) {
    const query = `
      SELECT c.*,
             COUNT(DISTINCT e.student_id) AS student_count,
             COUNT(DISTINCT a.assignment_id) AS assignment_count
      FROM courses c
      LEFT JOIN enrollments e ON c.course_id = e.course_id
      LEFT JOIN assignments a ON c.course_id = a.course_id
      WHERE c.instructor_id = $1
      GROUP BY c.course_id
      ORDER BY c.created_at DESC
    `;
    const result = await pool.query(query, [instructorId]);
    return result.rows;
  }

  static async findAll() {
    const query = `
      SELECT c.*,
             u.first_name || ' ' || u.last_name AS instructor_name,
             COUNT(DISTINCT e.student_id) AS student_count
      FROM courses c
      LEFT JOIN users u ON c.instructor_id = u.user_id
      LEFT JOIN enrollments e ON c.course_id = e.course_id
      GROUP BY c.course_id, u.first_name, u.last_name
      ORDER BY c.created_at DESC
    `;
    const result = await pool.query(query);
    return result.rows;
  }

  static async update(courseId, updates) {
    const fields = [];
    const values = [];
    let paramCount = 1;

    const allowedFields = ['course_name', 'semester', 'year'];
    Object.keys(updates).forEach(key => {
      if (allowedFields.includes(key) && updates[key] !== undefined) {
        fields.push(`${key} = $${paramCount}`);
        values.push(updates[key]);
        paramCount++;
      }
    });

    if (fields.length === 0) return null;

    values.push(courseId);
    const query = `
      UPDATE courses
      SET ${fields.join(', ')}, updated_at = CURRENT_TIMESTAMP
      WHERE course_id = $${paramCount}
      RETURNING *
    `;
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async delete(courseId) {
    const result = await pool.query(
      'DELETE FROM courses WHERE course_id = $1 RETURNING course_id',
      [courseId]
    );
    return result.rows[0];
  }

  static async getStudents(courseId) {
    const query = `
      SELECT u.user_id, u.email, u.first_name, u.last_name, e.enrolled_at
      FROM users u
      JOIN enrollments e ON u.user_id = e.student_id
      WHERE e.course_id = $1
      ORDER BY u.last_name, u.first_name
    `;
    const result = await pool.query(query, [courseId]);
    return result.rows;
  }

  static async generateJoinCode(courseId) {
    const result = await pool.query(
      `UPDATE courses SET join_code = generate_join_code() WHERE course_id = $1 RETURNING join_code`,
      [courseId]
    );
    return result.rows[0];
  }

  static async findByJoinCode(joinCode) {
    const query = `
      SELECT c.*,
             u.first_name || ' ' || u.last_name AS instructor_name,
             COUNT(DISTINCT e.student_id) AS student_count
      FROM courses c
      LEFT JOIN users u ON c.instructor_id = u.user_id
      LEFT JOIN enrollments e ON c.course_id = e.course_id
      WHERE c.join_code = $1
      GROUP BY c.course_id, u.first_name, u.last_name
    `;
    const result = await pool.query(query, [joinCode.toUpperCase()]);
    return result.rows[0];
  }

  static async enrollWithCode(studentId, joinCode) {
    const client = await pool.connect();
    try {
      await client.query('BEGIN');

      const courseResult = await client.query(
        'SELECT course_id FROM courses WHERE join_code = $1',
        [joinCode.toUpperCase()]
      );

      if (courseResult.rows.length === 0) {
        throw new Error('Invalid join code');
      }

      const courseId = courseResult.rows[0].course_id;

      const checkResult = await client.query(
        'SELECT * FROM enrollments WHERE student_id = $1 AND course_id = $2',
        [studentId, courseId]
      );

      if (checkResult.rows.length > 0) {
        throw new Error('Already enrolled in this course');
      }

      const enrollResult = await client.query(
        `INSERT INTO enrollments (student_id, course_id) VALUES ($1, $2) RETURNING *`,
        [studentId, courseId]
      );

      await client.query('COMMIT');
      return { enrollment: enrollResult.rows[0], courseId };
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }
}

module.exports = Course;
