const express = require('express');
const router = express.Router();
const multer = require('multer');
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

// Multer setup to handle multiple files in memory
const upload = multer({ storage: multer.memoryStorage() });

router.post('/batch-check', upload.array('files', 50), async (req, res) => {
  try {
    if (!req.files || req.files.length < 2) {
      return res.status(400).json({ message: "Upload at least 2 files." });
    }

    console.log(`Received ${req.files.length} files. Forwarding to Python Engine...`);

    // Create a form to send files to Python
    const formData = new FormData();
    req.files.forEach((file) => {
      formData.append('files', file.buffer, file.originalname);
    });

    // Call Python FastAPI
    const pythonResponse = await axios.post('http://127.0.0.1:5000/api/analyze-type3-batch', formData, {
      headers: {
        ...formData.getHeaders(),
      },
      maxContentLength: Infinity,
      maxBodyLength: Infinity
    });

    res.json(pythonResponse.data);

  } catch (err) {
    console.error("Batch Analysis Error:", err.message);
    res.status(500).json({ message: "Analysis Failed", error: err.message });
  }
});

module.exports = router;