const multer = require('multer');
const path = require('path');
const crypto = require('crypto');
const fs = require('fs');

// Ensure uploads directory exists
const uploadsDir = path.join(__dirname, '../../uploads');
if (!fs.existsSync(uploadsDir)) {
  fs.mkdirSync(uploadsDir, { recursive: true });
}

// Configure storage
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    // Create subdirectory based on assignment ID
    const assignmentId = req.params.id || 'temp';
    const assignmentDir = path.join(uploadsDir, `assignment_${assignmentId}`);
    
    if (!fs.existsSync(assignmentDir)) {
      fs.mkdirSync(assignmentDir, { recursive: true });
    }
    
    cb(null, assignmentDir);
  },
  filename: (req, file, cb) => {
    // Generate unique filename: studentId_timestamp_originalname
    const studentId = req.user.user_id;
    const timestamp = Date.now();
    const sanitizedName = file.originalname.replace(/[^a-zA-Z0-9._-]/g, '_');
    const filename = `${studentId}_${timestamp}_${sanitizedName}`;
    
    cb(null, filename);
  }
});

// File filter - only allow specific code file extensions
const fileFilter = (req, file, cb) => {
  const allowedExtensions = ['.cpp', '.c', '.h', '.hpp', '.java', '.py', '.js', '.cs'];
  const ext = path.extname(file.originalname).toLowerCase();
  
  if (allowedExtensions.includes(ext)) {
    cb(null, true);
  } else {
    cb(new Error(`Invalid file type. Allowed: ${allowedExtensions.join(', ')}`), false);
  }
};

// Configure multer
const upload = multer({
  storage: storage,
  fileFilter: fileFilter,
  limits: {
    fileSize: 10 * 1024 * 1024 // 10MB max file size
  }
});

// Middleware to calculate file hash after upload
const calculateHash = (req, res, next) => {
  if (req.file) {
    const fileBuffer = fs.readFileSync(req.file.path);
    req.fileHash = crypto.createHash('sha256').update(fileBuffer).digest('hex');
  }
  next();
};

module.exports = {
  upload,
  calculateHash
};