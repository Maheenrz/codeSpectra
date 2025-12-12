const pool = require('../config/database');

// Get all courses for current user
exports.getAllCourses = async (req, res) => {
  try {
    const userId = req.user.user_id;
    const userRole = req.user.role;

    let query;
    if (userRole === 'instructor' || userRole === 'admin') {
      query = `
        SELECT c.*, 
               COUNT(DISTINCT e.student_id) as student_count,
               COUNT(DISTINCT a.assignment_id) as assignment_count
        FROM courses c
        LEFT JOIN enrollments e ON c.course_id = e.course_id
        LEFT JOIN assignments a ON c.course_id = a.course_id
        WHERE c.instructor_id = $1
        GROUP BY c.course_id
        ORDER BY c.created_at DESC
      `;
    } else {
      query = `
        SELECT c.*, 
               COUNT(DISTINCT a.assignment_id) as assignment_count,
               u.first_name as instructor_first_name,
               u.last_name as instructor_last_name
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        LEFT JOIN assignments a ON c.course_id = a.course_id
        LEFT JOIN users u ON c.instructor_id = u.user_id
        WHERE e.student_id = $1
        GROUP BY c.course_id, u.first_name, u.last_name
        ORDER BY c.created_at DESC
      `;
    }

    const result = await pool.query(query, [userId]);
    res.json(result.rows);
  } catch (error) {
    console.error('Get courses error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Create new course (instructor only)
exports.createCourse = async (req, res) => {
  try {
    const { courseCode, courseName, semester, year } = req.body;
    const instructorId = req.user.user_id;

    const result = await pool.query(
      `INSERT INTO courses (course_code, course_name, instructor_id, semester, year)
       VALUES ($1, $2, $3, $4, $5)
       RETURNING *`,
      [courseCode, courseName, instructorId, semester, year]
    );

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Create course error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get single course by ID
exports.getCourseById = async (req, res) => {
  try {
    const { id } = req.params;
    const result = await pool.query(
      `SELECT c.*, 
              u.first_name as instructor_first_name,
              u.last_name as instructor_last_name,
              COUNT(DISTINCT e.student_id) as student_count
       FROM courses c
       LEFT JOIN users u ON c.instructor_id = u.user_id
       LEFT JOIN enrollments e ON c.course_id = e.course_id
       WHERE c.course_id = $1
       GROUP BY c.course_id, u.first_name, u.last_name`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Course not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Get course error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Update course
exports.updateCourse = async (req, res) => {
  try {
    const { id } = req.params;
    const { courseCode, courseName, semester, year } = req.body;

    const result = await pool.query(
      `UPDATE courses 
       SET course_code = $1, course_name = $2, semester = $3, year = $4
       WHERE course_id = $5 AND instructor_id = $6
       RETURNING *`,
      [courseCode, courseName, semester, year, id, req.user.user_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Course not found or unauthorized' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Update course error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Delete course
exports.deleteCourse = async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      'DELETE FROM courses WHERE course_id = $1 AND instructor_id = $2 RETURNING *',
      [id, req.user.user_id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Course not found or unauthorized' });
    }

    res.json({ message: 'Course deleted successfully' });
  } catch (error) {
    console.error('Delete course error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get course assignments
exports.getCourseAssignments = async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      `SELECT a.*,
              COUNT(DISTINCT s.submission_id) as submission_count,
              COUNT(DISTINCT CASE WHEN s.analysis_status = 'completed' THEN s.submission_id END) as analyzed_count
       FROM assignments a
       LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
       WHERE a.course_id = $1
       GROUP BY a.assignment_id
       ORDER BY a.due_date DESC`,
      [id]
    );

    res.json(result.rows);
  } catch (error) {
    console.error('Get assignments error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Enroll student in course
exports.enrollStudent = async (req, res) => {
  try {
    const { id } = req.params;
    const { studentEmail } = req.body;

    // Find student by email
    const studentResult = await pool.query(
      'SELECT user_id FROM users WHERE email = $1 AND role = $2',
      [studentEmail, 'student']
    );

    if (studentResult.rows.length === 0) {
      return res.status(404).json({ message: 'Student not found' });
    }

    const studentId = studentResult.rows[0].user_id;

    // Enroll student
    await pool.query(
      'INSERT INTO enrollments (course_id, student_id) VALUES ($1, $2) ON CONFLICT DO NOTHING',
      [id, studentId]
    );

    res.json({ message: 'Student enrolled successfully' });
  } catch (error) {
    console.error('Enroll student error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};