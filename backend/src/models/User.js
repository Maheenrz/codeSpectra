const pool = require('../config/database');

class User {
  static async create(userData) {
    const { email, password_hash, first_name, last_name, role, institution } = userData;
    const query = `
      INSERT INTO users (email, password_hash, first_name, last_name, role, institution)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING user_id, email, first_name, last_name, role, institution, created_at;
    `;
    const values = [email, password_hash, first_name, last_name, role, institution];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  static async findByEmail(email) {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await pool.query(query, [email]);
    return result.rows[0];
  }

  static async findById(userId) {
    const query = 'SELECT user_id, email, first_name, last_name, role, institution FROM users WHERE user_id = $1';
    const result = await pool.query(query, [userId]);
    return result.rows[0];
  }

  static async updateLastLogin(userId) {
    const query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = $1';
    await pool.query(query, [userId]);
  }
}

module.exports = User;