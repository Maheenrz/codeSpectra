const pool = require('../config/database');
const crypto = require('crypto');
const fs = require('fs').promises;

// Get all submissions (with filters)
exports.getAllSubmissions = async (req, res) => {
  try {
    const userId = req.user.user_id;
    const userRole = req.user.role;
    const { assignmentId, status } = req.query;

    let query;
    let params = [userId];

    if (userRole === 'instructor' || userRole === 'admin') {
      query = `
        SELECT s.*, 
               u.first_name, u.last_name, u.email,
               a.title as assignment_title,
               c.course_name
        FROM submissions s
        JOIN users u ON s.student_id = u.user_id
        JOIN assignments a ON s.assignment_id = a.assignment_id
        JOIN courses c ON a.course_id = c.course_id
        WHERE c.instructor_id = $1
      `;

      if (assignmentId) {
        query += ' AND s.assignment_id = $2';
        params.push(assignmentId);
      }
      if (status) {
        query += ` AND s.analysis_status = $${params.length + 1}`;
        params.push(status);
      }
    } else {
      query = `
        SELECT s.*, 
               a.title as assignment_title,
               c.course_name,
               c.course_code
        FROM submissions s
        JOIN assignments a ON s.assignment_id = a.assignment_id
        JOIN courses c ON a.course_id = c.course_id
        WHERE s.student_id = $1
      `;
    }

    query += ' ORDER BY s.submitted_at DESC';

    const result = await pool.query(query, params);
    res.json(result.rows);
  } catch (error) {
    console.error('Get submissions error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get submission by ID
exports.getSubmissionById = async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      `SELECT s.*, 
              u.first_name, u.last_name, u.email,
              a.title as assignment_title, a.description as assignment_description,
              c.course_name, c.course_code
       FROM submissions s
       JOIN users u ON s.student_id = u.user_id
       JOIN assignments a ON s.assignment_id = a.assignment_id
       JOIN courses c ON a.course_id = c.course_id
       WHERE s.submission_id = $1`,
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Submission not found' });
    }

    res.json(result.rows[0]);
  } catch (error) {
    console.error('Get submission error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Download submission file
exports.downloadSubmission = async (req, res) => {
  try {
    const { id } = req.params;

    const result = await pool.query(
      'SELECT file_path, filename FROM submissions WHERE submission_id = $1',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Submission not found' });
    }

    const { file_path, filename } = result.rows[0];

    // Check if file exists
    try {
      await fs.access(file_path);
    } catch {
      return res.status(404).json({ message: 'File not found on server' });
    }

    res.download(file_path, filename);
  } catch (error) {
    console.error('Download submission error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Delete submission
exports.deleteSubmission = async (req, res) => {
  try {
    const { id } = req.params;

    // Get file path before deletion
    const result = await pool.query(
      'SELECT file_path FROM submissions WHERE submission_id = $1',
      [id]
    );

    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'Submission not found' });
    }

    const filePath = result.rows[0].file_path;

    // Delete from database
    await pool.query('DELETE FROM submissions WHERE submission_id = $1', [id]);

    // Delete file from filesystem
    try {
      await fs.unlink(filePath);
    } catch (err) {
      console.error('File deletion error:', err);
    }

    res.json({ message: 'Submission deleted successfully' });
  } catch (error) {
    console.error('Delete submission error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Get submission analysis results
exports.getSubmissionAnalysis = async (req, res) => {
  try {
    const { id } = req.params;

    // Get clone results
    const cloneResults = await pool.query(
      `SELECT cr.*,
              s1.filename as file1_name,
              s2.filename as file2_name,
              u1.first_name as student1_first_name,
              u1.last_name as student1_last_name,
              u2.first_name as student2_first_name,
              u2.last_name as student2_last_name
       FROM clone_results cr
       JOIN submissions s1 ON cr.submission1_id = s1.submission_id
       JOIN submissions s2 ON cr.submission2_id = s2.submission_id
       JOIN users u1 ON s1.student_id = u1.user_id
       JOIN users u2 ON s2.student_id = u2.user_id
       WHERE cr.submission1_id = $1 OR cr.submission2_id = $1
       ORDER BY cr.similarity_score DESC`,
      [id]
    );

    // Get feedback
    const feedback = await pool.query(
      'SELECT * FROM feedback WHERE submission_id = $1 ORDER BY generated_at DESC',
      [id]
    );

    // Get submission status
    const submission = await pool.query(
      'SELECT analysis_status, analyzed_at FROM submissions WHERE submission_id = $1',
      [id]
    );

    res.json({
      submission: submission.rows[0],
      cloneResults: cloneResults.rows,
      feedback: feedback.rows
    });
  } catch (error) {
    console.error('Get analysis error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Trigger analysis for submission
exports.triggerAnalysis = async (req, res) => {
  try {
    const { id } = req.params;

    // Update submission status
    await pool.query(
      `UPDATE submissions 
       SET analysis_status = 'processing'
       WHERE submission_id = $1`,
      [id]
    );

    // TODO: Send to analysis queue/service
    // This would typically trigger your Python analysis engine

    res.json({ 
      message: 'Analysis triggered successfully',
      status: 'processing'
    });
  } catch (error) {
    console.error('Trigger analysis error:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
};

// Calculate file hash helper
function calculateFileHash(fileBuffer) {
  return crypto.createHash('sha256').update(fileBuffer).digest('hex');
}

module.exports.calculateFileHash = calculateFileHash;