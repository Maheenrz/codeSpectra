const express = require('express');
const router = express.Router();
const AssignmentController = require('../controllers/assignment.controller');
const { authenticateToken, requireInstructor } = require('../middleware/auth');
const { validateAssignment } = require('../middleware/validation');

// All routes require authentication
router.use(authenticateToken);

// ========== ASSIGNMENT ROUTES ==========

// Create assignment (with questions)
router.post('/', requireInstructor, validateAssignment, AssignmentController.createAssignment);

// Get assignment by ID (with questions)
router.get('/:assignmentId', AssignmentController.getAssignmentById);

// Get assignments for course
router.get('/course/:courseId', AssignmentController.getCourseAssignments);

// Update assignment
router.put('/:assignmentId', requireInstructor, AssignmentController.updateAssignment);

// Delete assignment
router.delete('/:assignmentId', requireInstructor, AssignmentController.deleteAssignment);

// Get submissions for assignment
router.get('/:assignmentId/submissions', AssignmentController.getAssignmentSubmissions);

// ========== QUESTION ROUTES ==========

// Get question by ID
router.get('/questions/:questionId', AssignmentController.getQuestionById);

// Update question
router.put('/questions/:questionId', requireInstructor, AssignmentController.updateQuestion);

// Delete question
router.delete('/questions/:questionId', requireInstructor, AssignmentController.deleteQuestion);

// Get submissions for specific question
router.get('/questions/:questionId/submissions', AssignmentController.getQuestionSubmissions);

module.exports = router;