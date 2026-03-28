// backend/src/routes/analysis.routes.js
const express  = require('express');
const router   = express.Router();
const multer   = require('multer');
const path     = require('path');
const AnalysisController = require('../controllers/analysis.controller');
const { authenticateToken, requireInstructor, requireAuthenticated } = require('../middleware/auth');

// Ensure temp upload dir exists before multer tries to write into it
const TEMP_DIR = path.join(__dirname, '../../uploads/temp');
const fs = require('fs');
if (!fs.existsSync(TEMP_DIR)) fs.mkdirSync(TEMP_DIR, { recursive: true });

const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, TEMP_DIR),
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

// Open to ALL authenticated users
router.post('/files', requireAuthenticated, upload.array('files', 100), AnalysisController.analyzeFiles);

router.post('/submission/:submissionId', requireInstructor, AnalysisController.analyzeSubmission);
router.post('/assignment/:assignmentId', requireInstructor, AnalysisController.analyzeAssignment);

// Results
router.get('/results/submission/:submissionId', AnalysisController.getSubmissionResults);
router.get('/results/assignment/:assignmentId', AnalysisController.getAssignmentResults);

// Single pair detail with file content
router.get('/pair/:pairId', AnalysisController.getPairDetail);

// CSV report (proxy to engine — runs analysis + generates report in one shot)
router.post('/report/csv', requireAuthenticated, upload.array('files', 100), AnalysisController.proxyReportCsv);
// CSV from a completed async assignment analysis job
router.get('/report/csv/:jobId', requireAuthenticated, AnalysisController.proxyJobCsv);

// ── Class ZIP async analysis ───────────────────────────────────────
// Upload a single .zip that contains student sub-zips or student folders.
// Returns job_id immediately; client polls /zip/results/:jobId for progress.
router.post('/zip', requireAuthenticated, upload.single('file'), AnalysisController.analyzeClassZip);
router.get('/zip/results/:jobId', requireAuthenticated, AnalysisController.getZipResults);
router.post('/zip/chunked', requireAuthenticated, upload.single('file'), AnalysisController.analyzeClassZipChunked);   // ← new line



module.exports = router;
