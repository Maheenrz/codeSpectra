const express = require('express');
const cors = require('cors');
const path = require('path');
require('dotenv').config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Static files for uploads (optional - for serving downloaded files)
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// Test database connection
const pool = require('./config/database');
pool.query('SELECT NOW()', (err, res) => {
  if (err) {
    console.error('❌ Database connection failed:', err);
  } else {
    console.log('✅ Database connected at:', res.rows[0].now);
  }
});

// Routes
app.get('/', (req, res) => {
  res.json({ 
    message: 'Welcome to CodeSpectra API',
    version: '1.0.0',
    endpoints: {
      health: '/health',
      auth: '/api/auth',
      courses: '/api/courses',
      assignments: '/api/assignments',
      submissions: '/api/submissions'
    }
  });
});

app.get('/health', (req, res) => {
  res.json({ 
    status: 'ok', 
    message: 'CodeSpectra Backend is running!',
    timestamp: new Date().toISOString(),
    database: 'connected'
  });
});

// API Routes
app.use('/api/auth', require('./routes/auth.routes'));
app.use('/api/courses', require('./routes/courses.routes'));
app.use('/api/assignments', require('./routes/assignments.routes'));
app.use('/api/submissions', require('./routes/submissions.routes'));

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  
  // Multer errors
  if (err.code === 'LIMIT_FILE_SIZE') {
    return res.status(400).json({ message: 'File too large. Max size: 10MB' });
  }
  
  if (err.message.includes('Invalid file type')) {
    return res.status(400).json({ message: err.message });
  }
  
  res.status(500).json({ 
    message: 'Something went wrong!',
    error: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`🚀 Backend running on http://localhost:${PORT}`);
  console.log(`📁 Uploads directory: ${path.join(__dirname, 'uploads')}`);
});