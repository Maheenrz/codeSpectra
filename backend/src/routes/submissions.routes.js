const express = require('express');
const router = express.Router();
const SubmissionController = require('../controllers/submission.controller');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { upload } = require('../utils/fileUpload');   // ← destructure correctly

router.use(authenticateToken);

router.get('/my-submissions', requireRole('student'), SubmissionController.getStudentSubmissions);
router.get('/assignment/:assignmentId', SubmissionController.getAssignmentSubmissions);

router.post('/', upload.array('files', 20), SubmissionController.createSubmission);  // 20 files max
router.get('/:submissionId', SubmissionController.getSubmissionById);
router.delete('/:submissionId', SubmissionController.deleteSubmission);

module.exports = router;