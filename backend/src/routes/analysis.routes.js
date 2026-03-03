const express  = require('express');
const router   = express.Router();
const multer   = require('multer');
const path     = require('path');
const AnalysisController = require('../controllers/analysis.controller');
const { authenticateToken, requireInstructor } = require('../middleware/auth');

// ── Multer config for generic file uploads ──────────────────────────────────
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, '../../uploads/temp'));
  },
  filename: (req, file, cb) => {
    const unique = `${Date.now()}-${Math.round(Math.random() * 1e9)}`;
    cb(null, `${unique}-${file.originalname}`);
  },
});

const upload = multer({
  storage,
  limits: { fileSize: 200 * 1024 * 1024 }, // 200 MB (for ZIPs)
  fileFilter: (req, file, cb) => {
    const allowed = [
      '.cpp', '.c', '.h', '.hpp', '.cc', '.cxx',
      '.java', '.py',
      '.js', '.jsx', '.ts', '.tsx',
      '.zip',
    ];
    const ext = path.extname(file.originalname).toLowerCase();
    cb(null, allowed.includes(ext));
  },
});

// All routes require authentication
router.use(authenticateToken);

// Health check
router.get('/health', AnalysisController.checkHealth);

// ── Generic file analysis (no assignment) ───────────────────────────────────
router.post(
  '/files',
  requireInstructor,
  upload.array('files', 100),
  AnalysisController.analyzeFiles,
);

// ── Assignment-scoped analysis ───────────────────────────────────────────────
router.post('/submission/:submissionId', requireInstructor, AnalysisController.analyzeSubmission);
router.post('/assignment/:assignmentId', requireInstructor, AnalysisController.analyzeAssignment);

// ── Results ──────────────────────────────────────────────────────────────────
router.get('/results/submission/:submissionId', AnalysisController.getSubmissionResults);
router.get('/results/assignment/:assignmentId', AnalysisController.getAssignmentResults);

module.exports = router;