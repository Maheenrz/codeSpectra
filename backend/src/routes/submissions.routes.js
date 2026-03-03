const express = require('express');
const router = express.Router();
const SubmissionController = require('../controllers/submission.controller');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { upload } = require('../utils/fileUpload');

router.use(authenticateToken);

router.get('/my-submissions', requireRole('student'), SubmissionController.getStudentSubmissions);
router.get('/assignment/:assignmentId', SubmissionController.getAssignmentSubmissions);

router.post('/', upload.array('files', 20), SubmissionController.createSubmission);
router.get('/:submissionId', SubmissionController.getSubmissionById);
router.get('/:submissionId/analysis', SubmissionController.getSubmissionWithAnalysis);  // ← NEW
router.delete('/:submissionId', SubmissionController.deleteSubmission);

module.exports = router;