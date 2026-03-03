const { Assignment, AssignmentQuestion } = require('../models');
const pool = require('../config/database');

class AssignmentController {
  // Create new assignment with questions
  static async createAssignment(req, res) {
    try {
      const { questions, ...assignmentData } = req.body;
      
      assignmentData.createdBy = req.user.userId;

      // Validate questions if provided
      if (questions && questions.length > 0) {
        // Validate each question
        for (let i = 0; i < questions.length; i++) {
          const q = questions[i];
          
          if (!q.title || !q.description) {
            return res.status(400).json({ 
              error: `Question ${i + 1}: Title and description are required` 
            });
          }
          
          if (!q.maxMarks || q.maxMarks < 0) {
            return res.status(400).json({ 
              error: `Question ${i + 1}: Max marks must be a positive number` 
            });
          }

          // Parse expectedFiles if string
          if (typeof q.expectedFiles === 'string') {
            q.expectedFiles = q.expectedFiles.split(',').map(f => f.trim()).filter(Boolean);
          }

          // Auto-detect allowed extensions based on primary language if not provided
          if (!q.allowedExtensions || q.allowedExtensions.length === 0) {
            q.allowedExtensions = Assignment.getExtensionsForLanguage(
              assignmentData.primaryLanguage || 'cpp'
            );
          } else if (typeof q.allowedExtensions === 'string') {
            q.allowedExtensions = q.allowedExtensions.split(',').map(e => e.trim());
          }
        }
      }

      // Create assignment with questions
      const result = await Assignment.createWithQuestions(assignmentData, questions || []);

      res.status(201).json({
        message: 'Assignment created successfully',
        assignment: result
      });
    } catch (error) {
      console.error('Create assignment error:', error);
      res.status(500).json({ error: 'Failed to create assignment', details: error.message });
    }
  }

  // Get assignment by ID (with questions)
  static async getAssignmentById(req, res) {
    try {
      const { assignmentId } = req.params;
      const assignment = await Assignment.findByIdWithQuestions(assignmentId);

      if (!assignment) {
        return res.status(404).json({ error: 'Assignment not found' });
      }

      res.json(assignment);
    } catch (error) {
      console.error('Get assignment error:', error);
      res.status(500).json({ error: 'Failed to get assignment', details: error.message });
    }
  }

  // Get assignments for a course
  static async getCourseAssignments(req, res) {
    try {
      const { courseId } = req.params;
      const assignments = await Assignment.findByCourse(courseId);
      res.json(assignments);
    } catch (error) {
      console.error('Get course assignments error:', error);
      res.status(500).json({ error: 'Failed to get assignments', details: error.message });
    }
  }

  // Update assignment
  static async updateAssignment(req, res) {
    try {
      const { assignmentId } = req.params;
      const updates = req.body;

      const assignment = await Assignment.update(assignmentId, updates);
      if (!assignment) {
        return res.status(404).json({ error: 'Assignment not found' });
      }

      res.json({
        message: 'Assignment updated successfully',
        assignment
      });
    } catch (error) {
      console.error('Update assignment error:', error);
      res.status(500).json({ error: 'Failed to update assignment', details: error.message });
    }
  }

  // Delete assignment
  static async deleteAssignment(req, res) {
    try {
      const { assignmentId } = req.params;

      const assignment = await Assignment.delete(assignmentId);
      if (!assignment) {
        return res.status(404).json({ error: 'Assignment not found' });
      }

      res.json({ message: 'Assignment deleted successfully' });
    } catch (error) {
      console.error('Delete assignment error:', error);
      res.status(500).json({ error: 'Failed to delete assignment', details: error.message });
    }
  }

  // Get submissions for assignment
  static async getAssignmentSubmissions(req, res) {
    try {
      const { assignmentId } = req.params;
      const submissions = await Assignment.getSubmissions(assignmentId);
      res.json(submissions);
    } catch (error) {
      console.error('Get assignment submissions error:', error);
      res.status(500).json({ error: 'Failed to get submissions', details: error.message });
    }
  }

  // ========== QUESTION MANAGEMENT ==========

  // Get question by ID
  static async getQuestionById(req, res) {
    try {
      const { questionId } = req.params;
      const question = await AssignmentQuestion.findById(questionId);

      if (!question) {
        return res.status(404).json({ error: 'Question not found' });
      }

      res.json(question);
    } catch (error) {
      console.error('Get question error:', error);
      res.status(500).json({ error: 'Failed to get question', details: error.message });
    }
  }

  // Update question
  static async updateQuestion(req, res) {
    try {
      const { questionId } = req.params;
      const updates = req.body;

      // Parse array fields if they're strings
      if (typeof updates.expectedFiles === 'string') {
        updates.expectedFiles = updates.expectedFiles.split(',').map(f => f.trim()).filter(Boolean);
      }
      if (typeof updates.allowedExtensions === 'string') {
        updates.allowedExtensions = updates.allowedExtensions.split(',').map(e => e.trim());
      }

      const question = await AssignmentQuestion.update(questionId, updates);
      
      if (!question) {
        return res.status(404).json({ error: 'Question not found' });
      }

      res.json({
        message: 'Question updated successfully',
        question
      });
    } catch (error) {
      console.error('Update question error:', error);
      res.status(500).json({ error: 'Failed to update question', details: error.message });
    }
  }

  // Delete question
  static async deleteQuestion(req, res) {
    try {
      const { questionId } = req.params;

      const question = await AssignmentQuestion.delete(questionId);
      if (!question) {
        return res.status(404).json({ error: 'Question not found' });
      }

      res.json({ message: 'Question deleted successfully' });
    } catch (error) {
      console.error('Delete question error:', error);
      res.status(500).json({ error: 'Failed to delete question', details: error.message });
    }
  }

  // Get submissions for a specific question
  static async getQuestionSubmissions(req, res) {
    try {
      const { questionId } = req.params;
      
      const query = `
        SELECT 
          s.*,
          u.first_name || ' ' || u.last_name as student_name,
          u.email as student_email,
          COUNT(cf.file_id) as file_count
        FROM submissions s
        JOIN users u ON s.student_id = u.user_id
        LEFT JOIN code_files cf ON s.submission_id = cf.submission_id
        WHERE s.question_id = $1
        GROUP BY s.submission_id, u.first_name, u.last_name, u.email
        ORDER BY s.submitted_at DESC
      `;
      
      const result = await pool.query(query, [questionId]);
      res.json(result.rows);
    } catch (error) {
      console.error('Get question submissions error:', error);
      res.status(500).json({ error: 'Failed to get submissions', details: error.message });
    }
  }
}

module.exports = AssignmentController;