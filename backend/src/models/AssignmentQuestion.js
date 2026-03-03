const pool = require('../config/database');

class AssignmentQuestion {
  // Create a new question
  static async create(questionData) {
    const query = `
      INSERT INTO assignment_questions (
        assignment_id, question_number, title, description, 
        expected_files, allowed_extensions, max_marks
      ) VALUES ($1, $2, $3, $4, $5, $6, $7)
      RETURNING *
    `;
    
    const values = [
      questionData.assignmentId,
      questionData.questionNumber,
      questionData.title,
      questionData.description,
      questionData.expectedFiles ? JSON.stringify(questionData.expectedFiles) : null,
      questionData.allowedExtensions ? JSON.stringify(questionData.allowedExtensions) : null,
      questionData.maxMarks || 0
    ];
    
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  // Get question by ID
  static async findById(questionId) {
    const query = `
      SELECT 
        q.*,
        a.title as assignment_title,
        a.course_id
      FROM assignment_questions q
      JOIN assignments a ON q.assignment_id = a.assignment_id
      WHERE q.question_id = $1
    `;
    const result = await pool.query(query, [questionId]);
    
    if (result.rows[0]) {
      const row = result.rows[0];
      // Parse JSON fields
      row.expected_files = row.expected_files ? JSON.parse(row.expected_files) : [];
      row.allowed_extensions = row.allowed_extensions ? JSON.parse(row.allowed_extensions) : [];
    }
    
    return result.rows[0];
  }

  // Get all questions for an assignment
  static async findByAssignment(assignmentId) {
    const query = `
      SELECT * FROM assignment_questions
      WHERE assignment_id = $1
      ORDER BY question_number ASC
    `;
    const result = await pool.query(query, [assignmentId]);
    
    // Parse JSON fields for each question
    return result.rows.map(row => ({
      ...row,
      expected_files: row.expected_files ? JSON.parse(row.expected_files) : [],
      allowed_extensions: row.allowed_extensions ? JSON.parse(row.allowed_extensions) : []
    }));
  }

  // Update question
  static async update(questionId, updates) {
    const fields = [];
    const values = [];
    let paramCount = 1;

    const allowedFields = ['title', 'description', 'expected_files', 'allowed_extensions', 'max_marks'];
    
    Object.keys(updates).forEach(key => {
      if (allowedFields.includes(key) && updates[key] !== undefined) {
        // Special handling for JSON fields
        if (key === 'expected_files' || key === 'allowed_extensions') {
          fields.push(`${key} = $${paramCount}`);
          values.push(JSON.stringify(updates[key]));
        } else {
          fields.push(`${key} = $${paramCount}`);
          values.push(updates[key]);
        }
        paramCount++;
      }
    });

    if (fields.length === 0) return null;

    values.push(questionId);
    const query = `
      UPDATE assignment_questions 
      SET ${fields.join(', ')}, updated_at = CURRENT_TIMESTAMP
      WHERE question_id = $${paramCount}
      RETURNING *
    `;

    const result = await pool.query(query, values);
    
    if (result.rows[0]) {
      const row = result.rows[0];
      row.expected_files = row.expected_files ? JSON.parse(row.expected_files) : [];
      row.allowed_extensions = row.allowed_extensions ? JSON.parse(row.allowed_extensions) : [];
    }
    
    return result.rows[0];
  }

  // Delete question
  static async delete(questionId) {
    const query = 'DELETE FROM assignment_questions WHERE question_id = $1 RETURNING question_id';
    const result = await pool.query(query, [questionId]);
    return result.rows[0];
  }

  // Validate file against question's allowed extensions
  static async validateFile(questionId, filename) {
    const question = await this.findById(questionId);
    
    if (!question || !question.allowed_extensions || question.allowed_extensions.length === 0) {
      return true; // No restrictions
    }
    
    const ext = filename.substring(filename.lastIndexOf('.')).toLowerCase();
    return question.allowed_extensions.includes(ext);
  }

  // Get submission statistics for a question
  static async getSubmissionStats(questionId) {
    const query = `
      SELECT 
        COUNT(*) as total_submissions,
        COUNT(CASE WHEN s.analysis_status = 'completed' THEN 1 END) as analyzed_submissions,
        AVG(ar.overall_similarity) as avg_similarity
      FROM submissions s
      LEFT JOIN analysis_results ar ON s.submission_id = ar.submission_id
      WHERE s.question_id = $1
    `;
    const result = await pool.query(query, [questionId]);
    return result.rows[0];
  }
}

module.exports = AssignmentQuestion;