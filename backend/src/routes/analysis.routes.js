// backend/src/routes/analysis.routes.js
const express  = require('express');
const router   = express.Router();
const multer   = require('multer');
const path     = require('path');
const AnalysisController = require('../controllers/analysis.controller');
const { authenticateToken, requireInstructor } = require('../middleware/auth');

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, path.join(__dirname, '../../uploads/temp')),
  filename:    (req, file, cb) => cb(null, `${Date.now()}-${Math.round(Math.random() * 1e9)}-${file.originalname}`),
});

const upload = multer({
  storage,
  limits: { fileSize: 200 * 1024 * 1024 },
  fileFilter: (req, file, cb) => {
    const allowed = ['.cpp','.c','.h','.hpp','.cc','.cxx','.java','.py','.js','.jsx','.ts','.tsx','.zip'];
    cb(null, allowed.includes(path.extname(file.originalname).toLowerCase()));
  },
});

router.use(authenticateToken);

router.get('/health', AnalysisController.checkHealth);

router.post('/files', requireInstructor, upload.array('files', 100), AnalysisController.analyzeFiles);

router.post('/submission/:submissionId', requireInstructor, AnalysisController.analyzeSubmission);
router.post('/assignment/:assignmentId', requireInstructor, AnalysisController.analyzeAssignment);

// Results
router.get('/results/submission/:submissionId', AnalysisController.getSubmissionResults);
router.get('/results/assignment/:assignmentId', AnalysisController.getAssignmentResults);

// ── NEW: single pair detail with file content ─────────────────────────────
router.get('/pair/:pairId', AnalysisController.getPairDetail);

module.exports = router;
