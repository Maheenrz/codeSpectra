const pool = require('../config/database');

class CodeFile {
  static async create({ submissionId, filename, filePath, fileHash, fileSize }) {
    const query = `
      INSERT INTO code_files (submission_id, filename, file_path, file_hash, file_size)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING *
    `;
    const values = [submissionId, filename, filePath, fileHash, fileSize];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findById(fileId) {
    const query = 'SELECT * FROM code_files WHERE file_id = $1';
    const result = await pool.query(query, [fileId]);
    return result.rows[0];
  }

  static async findBySubmission(submissionId) {
    const query = `
      SELECT * FROM code_files 
      WHERE submission_id = $1
      ORDER BY uploaded_at DESC
    `;
    const result = await pool.query(query, [submissionId]);
    return result.rows;
  }

  static async findByHash(fileHash) {
    const query = `
      SELECT cf.*, s.assignment_id, s.student_id
      FROM code_files cf
      JOIN submissions s ON cf.submission_id = s.submission_id
      WHERE cf.file_hash = $1
    `;
    const result = await pool.query(query, [fileHash]);
    return result.rows;
  }

  static async delete(fileId) {
    const query = 'DELETE FROM code_files WHERE file_id = $1 RETURNING *';
    const result = await pool.query(query, [fileId]);
    return result.rows[0];
  }

  static async deleteBySubmission(submissionId) {
    const query = 'DELETE FROM code_files WHERE submission_id = $1 RETURNING *';
    const result = await pool.query(query, [submissionId]);
    return result.rows;
  }
}

module.exports = CodeFile;