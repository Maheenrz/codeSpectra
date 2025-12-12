const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const assignmentController = require('../controllers/assignmentController');
const authMiddleware = require('../middleware/auth');
const instructorMiddleware = require('../middleware/instructor');

router.use(authMiddleware);

// Validation rules
const assignmentValidation = [
  body('title').notEmpty().trim(),
  body('description').notEmpty().trim(),
  body('dueDate').isISO8601().toDate(),
  body('courseId').isInt(),
  body('primaryLanguage').isIn(['cpp', 'java', 'python']),
  body('maxFileSizeMb').isInt({ min: 1, max: 50 }),
  body('highSimilarityThreshold').isFloat({ min: 0, max: 100 }),
  body('mediumSimilarityThreshold').isFloat({ min: 0, max: 100 })
];

// Routes
router.get('/', assignmentController.getAllAssignments);
router.post('/', instructorMiddleware, assignmentValidation, assignmentController.createAssignment);
router.get('/:id', assignmentController.getAssignmentById);
router.put('/:id', instructorMiddleware, assignmentValidation, assignmentController.updateAssignment);
router.delete('/:id', instructorMiddleware, assignmentController.deleteAssignment);
router.get('/:id/submissions', assignmentController.getAssignmentSubmissions);

// Student submission
router.post('/:id/submit', assignmentController.submitAssignment);

module.exports = router;