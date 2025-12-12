const express = require('express');
const router = express.Router();
const submissionController = require('../controllers/submission.controller');
const { authenticate, isInstructor } = require('../middleware/auth');

// All routes require authentication
router.use(authenticate);

// Get all submissions (with filters)
router.get('/', submissionController.getAllSubmissions);

// Get submission by ID
router.get('/:id', submissionController.getSubmissionById);

// Download submission file
router.get('/:id/download', submissionController.downloadSubmission);

// Get submission analysis results
router.get('/:id/analysis', submissionController.getSubmissionAnalysis);

// Trigger analysis (instructor only)
router.post('/:id/analyze', isInstructor, submissionController.triggerAnalysis);

// Delete submission
router.delete('/:id', submissionController.deleteSubmission);

module.exports = router;
