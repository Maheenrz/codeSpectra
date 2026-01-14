const pool = require('../config/database');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs').promises;

// Get all assignments
exports.getAllAssignments = async (req, res) => {
  try {
    const userId = req.user.user_id;
    const userRole = req.user.role;

    let query;
    if (userRole === 'instructor' || userRole === 'admin') {
      query = `
        SELECT a.*, 
               c.course_code, c.course_name,
               COUNT(DISTINCT s.submission_id) as submission_count,
               COUNT(DISTINCT CASE WHEN s.analysis_status = 'completed' THEN s.submission_id END) as analyzed_count
        FROM assignments a
        JOIN courses c ON a.course_id = c.course_id
        LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
        WHERE c.instructor_id = $1
        GROUP BY a.assignment_id, c.course_code, c.course_name
        ORDER BY a.due_date DESC
      `;
    } else {
      query = `
        SELECT a.*, 
               c.course_code, c.course_name,
               s.submission_id, s.analysis_status,
               s.submitted_at
        FROM enrollments e
        JOIN courses c ON e.course_id = c.course_id
        JOIN assignments a ON c.course_id = a.course_id
        LEFT JOIN submissions s ON a.assignment_id = s.assignment_id AND s.student_id = $1
        WHERE e.student_id = $1
        ORDER BY a.due_date DESC
      `;
    }

    const result = await pool.query(query, [userId]);
    res.json(result.rows);
  } catch (error) {
    console.error('Get assignments error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Create new assignment
exports.createAssignment = async (req, res) => {
  try {
    const {
      title,
      description,
      courseId,
      dueDate,
      primaryLanguage = 'cpp',
      allowedExtensions = '.cpp,.h',
      maxFileSizeMb = 5,
      enableType1 = true,
      enableType2 = true,
      enableType3 = true,
      enableType4 = true,
      enableCrd = true,
      highSimilarityThreshold = 85,
      mediumSimilarityThreshold = 70,
      analysisMode = 'after_deadline',
      showResultsToStudents = false,
      generateFeedback = true
    } = req.body;

    // Verify instructor owns the course
    const courseCheck = await pool.query(
      'SELECT * FROM courses WHERE course_id = $1 AND instructor_id = $2',
      [courseId, req.user.user_id]
    );

    if (courseCheck.rows.length === 0) {
      return res.status(403).json({ message: 'Unauthorized: You do not own this course' });
    }

    const result = await pool.query(
      `INSERT INTO assignments (
        course_id, title, description, due_date, primary_language,
        allowed_extensions, max_file_size_mb, enable_type1, enable_type2,
        enable_type3, enable_type4, enable_crd, high_similarity_threshold,
        medium_similarity_threshold, analysis_mode, show_results_to_students,
        generate_feedback, created_by
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18)
      RETURNING *`,
      [
        courseId, title, description, dueDate, primaryLanguage,
        allowedExtensions, maxFileSizeMb, enableType1, enableType2,
        enableType3, enableType4, enableCrd, highSimilarityThreshold,
        mediumSimilarityThreshold, analysisMode, showResultsToStudents,
        generateFeedback, req.user.user_id
      ]
    );

    res.status(201).json(result.rows[0]);
  } catch (error) {
    console.error('Create assignment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get single assignment by ID
exports.getAssignmentById = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.user_id;
    const userRole = req.user.role;

    let query;
    if (userRole === 'instructor' || userRole === 'admin') {
      query = `
        SELECT a.*, 
               c.course_code, c.course_name,
               u.first_name as instructor_first_name,
               u.last_name as instructor_last_name,
               COUNT(DISTINCT s.submission_id) as submission_count
        FROM assignments a
        JOIN courses c ON a.course_id = c.course_id
        JOIN users u ON c.instructor_id = u.user_id
        LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
        WHERE a.assignment_id = $1 AND c.instructor_id = $2
        GROUP BY a.assignment_id, c.course_code, c.course_name, u.first_name, u.last_name
      `;
    } else {
      query = `
        SELECT a.*, 
               c.course_code, c.course_name,
               s.submission_id, s.analysis_status,
               s.submitted_at
        FROM assignments a
        JOIN courses c ON a.course_id = c.course_id
        JOIN enrollments e ON c.course_id = e.course_id
        LEFT JOIN submissions s ON a.assignment_id = s.assignment_id AND s.student_id = $2
        WHERE a.assignment_id = $1 AND e.student_id = $2
      `;
    }

    const result = await pool.query(query, [id, userId]);

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Assignment not found or unauthorized' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Get assignment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Update assignment
exports.updateAssignment = async (req, res) => {
  try {
    const { id } = req.params;
    const {
      title,
      description,
      dueDate,
      primaryLanguage,
      allowedExtensions,
      maxFileSizeMb,
      enableType1,
      enableType2,
      enableType3,
      enableType4,
      enableCrd,
      highSimilarityThreshold,
      mediumSimilarityThreshold,
      analysisMode,
      showResultsToStudents,
      generateFeedback
    } = req.body;

    // Verify instructor owns the assignment's course
    const assignmentCheck = await pool.query(
      `SELECT c.instructor_id 
       FROM assignments a
       JOIN courses c ON a.course_id = c.course_id
       WHERE a.assignment_id = $1`,
      [id]
    );

    if (assignmentCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Assignment not found' });
    }

    if (assignmentCheck.rows[0].instructor_id !== req.user.user_id) {
      return res.status(403).json({ message: 'Unauthorized: You do not own this assignment' });
    }

    const result = await pool.query(
      `UPDATE assignments 
       SET title = COALESCE($1, title),
           description = COALESCE($2, description),
           due_date = COALESCE($3, due_date),
           primary_language = COALESCE($4, primary_language),
           allowed_extensions = COALESCE($5, allowed_extensions),
           max_file_size_mb = COALESCE($6, max_file_size_mb),
           enable_type1 = COALESCE($7, enable_type1),
           enable_type2 = COALESCE($8, enable_type2),
           enable_type3 = COALESCE($9, enable_type3),
           enable_type4 = COALESCE($10, enable_type4),
           enable_crd = COALESCE($11, enable_crd),
           high_similarity_threshold = COALESCE($12, high_similarity_threshold),
           medium_similarity_threshold = COALESCE($13, medium_similarity_threshold),
           analysis_mode = COALESCE($14, analysis_mode),
           show_results_to_students = COALESCE($15, show_results_to_students),
           generate_feedback = COALESCE($16, generate_feedback),
           updated_at = NOW()
       WHERE assignment_id = $17
       RETURNING *`,
      [
        title, description, dueDate, primaryLanguage, allowedExtensions,
        maxFileSizeMb, enableType1, enableType2, enableType3, enableType4,
        enableCrd, highSimilarityThreshold, mediumSimilarityThreshold,
        analysisMode, showResultsToStudents, generateFeedback, id
      ]
    );

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Update assignment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Delete assignment
exports.deleteAssignment = async (req, res) => {
  try {
    const { id } = req.params;

    // Verify instructor owns the assignment's course
    const assignmentCheck = await pool.query(
      `SELECT c.instructor_id 
       FROM assignments a
       JOIN courses c ON a.course_id = c.course_id
       WHERE a.assignment_id = $1`,
      [id]
    );

    if (assignmentCheck.rows.length === 0) {
      return res.status(404).json({ message: 'Assignment not found' });
    }

    if (assignmentCheck.rows[0].instructor_id !== req.user.user_id) {
      return res.status(403).json({ message: 'Unauthorized: You do not own this assignment' });
    }

    await pool.query('DELETE FROM assignments WHERE assignment_id = $1', [id]);

    res.json({ message: 'Assignment deleted successfully' });
  } catch (error) {
    console.error('Delete assignment error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get assignment submissions
exports.getAssignmentSubmissions = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.user_id;
    const userRole = req.user.role;

    let query;
    if (userRole === 'instructor' || userRole === 'admin') {
      query = `
        SELECT s.*, 
               u.first_name, u.last_name, u.email,
               COUNT(DISTINCT cr.result_id) as clone_count
        FROM submissions s
        JOIN users u ON s.student_id = u.user_id
        LEFT JOIN clone_results cr ON s.submission_id IN (cr.submission1_id, cr.submission2_id)
        WHERE s.assignment_id = $1
        GROUP BY s.submission_id, u.first_name, u.last_name, u.email
        ORDER BY s.submitted_at DESC
      `;
    } else {
      query = `
        SELECT s.*, 
               COUNT(DISTINCT cr.result_id) as clone_count
        FROM submissions s
        LEFT JOIN clone_results cr ON s.submission_id IN (cr.submission1_id, cr.submission2_id)
        WHERE s.assignment_id = $1 AND s.student_id = $2
        GROUP BY s.submission_id
        ORDER BY s.submitted_at DESC
      `;
    }

    const result = await pool.query(query, userRole === 'student' ? [id, userId] : [id]);
    res.json(result.rows);
  } catch (error) {
    console.error('Get assignment submissions error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Student submit assignment
exports.submitAssignment = async (req, res) => {
  try {
    const { id } = req.params;
    const userId = req.user.user_id;

    if (!req.file) {
      return res.status(400).json({ message: 'No file uploaded' });
    }
    
    const result = await pool.query(
      `INSERT INTO submissions (assignment_id, student_id, filename, file_path, file_hash, analysis_status)
       VALUES ($1, $2, $3, $4, $5, 'pending')
       RETURNING *`,
      [id, userId, req.file.filename, req.file.path, req.fileHash]
    );

    res.status(201).json({ message: 'File uploaded successfully', submission: result.rows[0] });
  } catch (error) {
    res.status(500).json({ message: 'Upload failed', error: error.message });
  }
};