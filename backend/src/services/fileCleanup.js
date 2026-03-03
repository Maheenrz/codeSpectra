const fs = require('fs').promises;
const path = require('path');
const pool = require('../config/database');

const RETENTION_DAYS = 7;
const UPLOADS_DIR = path.join(__dirname, '../../uploads');

class FileCleanupService {
  /**
   * Delete files older than retention period
   */
  async cleanupOldFiles() {
    try {
      console.log(`Starting file cleanup (retention: ${RETENTION_DAYS} days)`);
      
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - RETENTION_DAYS);
      
      // Find old submissions
      const query = `
        SELECT DISTINCT s.submission_id, cf.file_path
        FROM submissions s
        JOIN code_files cf ON s.submission_id = cf.submission_id
        WHERE s.analyzed_at < $1 OR (s.submitted_at < $1 AND s.analysis_status = 'completed')
      `;
      
      const result = await pool.query(query, [cutoffDate]);
      
      let deletedCount = 0;
      for (const row of result.rows) {
        try {
          await fs.unlink(row.file_path);
          deletedCount++;
        } catch (err) {
          console.error(`Failed to delete ${row.file_path}:`, err.message);
        }
      }
      
      console.log(`✅ Cleanup complete: ${deletedCount} files deleted`);
      return { deletedCount };
      
    } catch (error) {
      console.error('Cleanup error:', error);
      throw error;
    }
  }
  
  /**
   * Delete files for specific submission
   */
  async cleanupSubmission(submissionId) {
    const query = 'SELECT file_path FROM code_files WHERE submission_id = $1';
    const result = await pool.query(query, [submissionId]);
    
    for (const row of result.rows) {
      try {
        await fs.unlink(row.file_path);
      } catch (err) {
        console.error(`Failed to delete ${row.file_path}:`, err.message);
      }
    }
  }
}

module.exports = new FileCleanupService();
