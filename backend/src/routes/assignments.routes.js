const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const assignmentController = require('../controllers/assignment.controller');
const { authenticate, isInstructor } = require('../middleware/auth'); // CHANGED
const {upload , calculateHash} = require('../utils/fileUpload');



router.use(authenticate); // CHANGED

// Validation rules (keep as is)
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

// Routes - update middleware calls
router.get('/', assignmentController.getAllAssignments);
router.post('/', isInstructor, assignmentValidation, assignmentController.createAssignment); // CHANGED
router.get('/:id', assignmentController.getAssignmentById);
router.put('/:id', isInstructor, assignmentValidation, assignmentController.updateAssignment); // CHANGED
router.delete('/:id', isInstructor, assignmentController.deleteAssignment); // CHANGED
router.get('/:id/submissions', assignmentController.getAssignmentSubmissions);
router.post('/:id/submit', upload.single('submissionFile'),calculateHash,assignmentController.submitAssignment);
module.exports = router;
