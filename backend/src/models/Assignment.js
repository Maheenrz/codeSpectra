const pool = require('../config/database');
const AssignmentQuestion = require('./AssignmentQuestion');

class Assignment {
  // Create assignment with questions
  static async createWithQuestions(assignmentData, questions = []) {
    const client = await pool.connect();
    
    try {
      await client.query('BEGIN');

      // Create assignment
      const assignmentQuery = `
        INSERT INTO assignments (
          course_id, title, description, due_date, created_by,
          primary_language, allowed_extensions, max_file_size_mb,
          enable_type1, enable_type2, enable_type3, enable_type4,
          high_similarity_threshold, medium_similarity_threshold,
          analysis_mode, show_results_to_students, generate_feedback,
          has_questions, total_marks
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19)
        RETURNING *
      `;

      const assignmentValues = [
        assignmentData.courseId,
        assignmentData.title,
        assignmentData.description,
        assignmentData.dueDate,
        assignmentData.createdBy,
        assignmentData.primaryLanguage || 'cpp',
        assignmentData.allowedExtensions || '.cpp,.c,.h',
        assignmentData.maxFileSizeMb || 5,
        assignmentData.enableType1 !== false,
        assignmentData.enableType2 !== false,
        assignmentData.enableType3 !== false,
        assignmentData.enableType4 !== false,
        assignmentData.highSimilarityThreshold || 85,
        assignmentData.mediumSimilarityThreshold || 70,
        assignmentData.analysisMode || 'after_deadline',
        assignmentData.showResultsToStudents || false,
        assignmentData.generateFeedback !== false,
        questions.length > 0,
        0  // Will be auto-calculated by trigger
      ];

      const assignmentResult = await client.query(assignmentQuery, assignmentValues);
      const assignment = assignmentResult.rows[0];

      // Create questions if provided
      const createdQuestions = [];
      for (let i = 0; i < questions.length; i++) {
        const questionQuery = `
          INSERT INTO assignment_questions (
            assignment_id, question_number, title, description, 
            expected_files, allowed_extensions, max_marks
          ) VALUES ($1, $2, $3, $4, $5, $6, $7)
          RETURNING *
        `;

        const questionValues = [
          assignment.assignment_id,
          i + 1,
          questions[i].title,
          questions[i].description,
          questions[i].expectedFiles ? JSON.stringify(questions[i].expectedFiles) : null,
          questions[i].allowedExtensions ? JSON.stringify(questions[i].allowedExtensions) : null,
          questions[i].maxMarks || 0
        ];

        const questionResult = await client.query(questionQuery, questionValues);
        const question = questionResult.rows[0];
        
        // Parse JSON fields
        question.expected_files = question.expected_files ? JSON.parse(question.expected_files) : [];
        question.allowed_extensions = question.allowed_extensions ? JSON.parse(question.allowed_extensions) : [];
        
        createdQuestions.push(question);
      }

      await client.query('COMMIT');

      return {
        ...assignment,
        questions: createdQuestions
      };

    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  // Get assignment with questions
  static async findByIdWithQuestions(assignmentId) {
    const query = `
      SELECT 
        a.*,
        c.course_code,
        c.course_name,
        u.first_name || ' ' || u.last_name as instructor_name
      FROM assignments a
      LEFT JOIN courses c ON a.course_id = c.course_id
      LEFT JOIN users u ON a.created_by = u.user_id
      WHERE a.assignment_id = $1
    `;
    
    const result = await pool.query(query, [assignmentId]);
    
    if (result.rows.length === 0) {
      return null;
    }
    
    const assignment = result.rows[0];
    
    // Get questions
    if (assignment.has_questions) {
      assignment.questions = await AssignmentQuestion.findByAssignment(assignmentId);
    } else {
      assignment.questions = [];
    }
    
    return assignment;
  }

  // Get assignment by ID (existing method - keep for compatibility)
  static async findById(assignmentId) {
    const query = `
      SELECT 
        a.*,
        c.course_code,
        c.course_name,
        u.first_name || ' ' || u.last_name as instructor_name
      FROM assignments a
      LEFT JOIN courses c ON a.course_id = c.course_id
      LEFT JOIN users u ON a.created_by = u.user_id
      WHERE a.assignment_id = $1
    `;
    
    const result = await pool.query(query, [assignmentId]);
    return result.rows[0];
  }

  // Get assignments for a course
  static async findByCourse(courseId) {
    const query = `
      SELECT 
        a.*,
        COUNT(DISTINCT s.submission_id) as submission_count,
        COUNT(DISTINCT aq.question_id) as question_count
      FROM assignments a
      LEFT JOIN submissions s ON a.assignment_id = s.assignment_id
      LEFT JOIN assignment_questions aq ON a.assignment_id = aq.assignment_id
      WHERE a.course_id = $1
      GROUP BY a.assignment_id
      ORDER BY a.created_at DESC
    `;
    const result = await pool.query(query, [courseId]);
    return result.rows;
  }

  // Update assignment
  static async update(assignmentId, updates) {
    const fields = [];
    const values = [];
    let paramCount = 1;

    const allowedFields = [
      'title', 'description', 'due_date', 'primary_language', 
      'allowed_extensions', 'max_file_size_mb', 'enable_type1', 
      'enable_type2', 'enable_type3', 'enable_type4',
      'high_similarity_threshold', 'medium_similarity_threshold',
      'analysis_mode', 'show_results_to_students', 'generate_feedback'
    ];

    Object.keys(updates).forEach(key => {
      if (allowedFields.includes(key) && updates[key] !== undefined) {
        fields.push(`${key} = $${paramCount}`);
        values.push(updates[key]);
        paramCount++;
      }
    });

    if (fields.length === 0) return null;

    values.push(assignmentId);
    const query = `
      UPDATE assignments 
      SET ${fields.join(', ')}, updated_at = CURRENT_TIMESTAMP
      WHERE assignment_id = $${paramCount}
      RETURNING *
    `;

    const result = await pool.query(query, values);
    return result.rows[0];
  }

  // Delete assignment (cascade deletes questions and submissions)
  static async delete(assignmentId) {
    const query = 'DELETE FROM assignments WHERE assignment_id = $1 RETURNING assignment_id';
    const result = await pool.query(query, [assignmentId]);
    return result.rows[0];
  }

  // Get submissions for assignment
  static async getSubmissions(assignmentId) {
    const query = `
      SELECT 
        s.*,
        u.first_name || ' ' || u.last_name as student_name,
        u.email as student_email,
        COUNT(cf.file_id) as file_count,
        aq.question_number,
        aq.title as question_title
      FROM submissions s
      JOIN users u ON s.student_id = u.user_id
      LEFT JOIN code_files cf ON s.submission_id = cf.submission_id
      LEFT JOIN assignment_questions aq ON s.question_id = aq.question_id
      WHERE s.assignment_id = $1
      GROUP BY s.submission_id, u.first_name, u.last_name, u.email, aq.question_number, aq.title
      ORDER BY s.submitted_at DESC
    `;
    const result = await pool.query(query, [assignmentId]);
    return result.rows;
  }

  // Get language-specific file extensions
  static getExtensionsForLanguage(language) {
    const extensionMap = {
      'cpp': ['.cpp', '.c', '.h', '.hpp', '.cc', '.cxx'],
      'c': ['.c', '.h'],
      'java': ['.java'],
      'python': ['.py'],
      'javascript': ['.js', '.jsx', '.ts', '.tsx'],
      'mixed': ['.cpp', '.c', '.h', '.java', '.py', '.js']
    };
    
    return extensionMap[language] || extensionMap['mixed'];
  }
}

module.exports = Assignment;