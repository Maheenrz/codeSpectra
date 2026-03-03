const pool = require('../config/database');
const bcrypt = require('bcryptjs');

class User {
  // Create a new user
  static async create({ email, password, firstName, lastName, role, institution }) {
    const hashedPassword = await bcrypt.hash(password, 10);
    
    const query = `
      INSERT INTO users (email, password_hash, first_name, last_name, role, institution)
      VALUES ($1, $2, $3, $4, $5, $6)
      RETURNING user_id, email, first_name, last_name, role, institution, is_active, created_at
    `;
    
    const values = [email, hashedPassword, firstName, lastName, role, institution];
    const result = await pool.query(query, values);
    return result.rows[0];
  }

  // Find user by email
  static async findByEmail(email) {
    const query = 'SELECT * FROM users WHERE email = $1';
    const result = await pool.query(query, [email]);
    return result.rows[0];
  }

  // Find user by ID
  static async findById(userId) {
    const query = `
      SELECT user_id, email, first_name, last_name, role, institution, is_active, created_at, last_login
      FROM users WHERE user_id = $1
    `;
    const result = await pool.query(query, [userId]);
    return result.rows[0];
  }

  // Verify password
  static async verifyPassword(plainPassword, hashedPassword) {
    return bcrypt.compare(plainPassword, hashedPassword);
  }

  // Update last login
  static async updateLastLogin(userId) {
    const query = 'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE user_id = $1';
    await pool.query(query, [userId]);
  }

  // Get all users by role
  static async findByRole(role) {
    const query = `
      SELECT user_id, email, first_name, last_name, role, institution, is_active, created_at
      FROM users WHERE role = $1
      ORDER BY created_at DESC
    `;
    const result = await pool.query(query, [role]);
    return result.rows;
  }

  // Get all users
  static async findAll() {
    const query = `
      SELECT user_id, email, first_name, last_name, role, institution, is_active, created_at
      FROM users
      ORDER BY created_at DESC
    `;
    const result = await pool.query(query);
    return result.rows;
  }

  // Update user
  static async update(userId, updates) {
    const fields = [];
    const values = [];
    let paramCount = 1;

    Object.keys(updates).forEach(key => {
      if (updates[key] !== undefined) {
        fields.push(`${key} = $${paramCount}`);
        values.push(updates[key]);
        paramCount++;
      }
    });

    if (fields.length === 0) {
      throw new Error('No fields to update');
    }

    values.push(userId);
    const query = `
      UPDATE users SET ${fields.join(', ')}
      WHERE user_id = $${paramCount}
      RETURNING user_id, email, first_name, last_name, role, institution, is_active
    `;

    const result = await pool.query(query, values);
    return result.rows[0];
  }

  // Delete user
  static async delete(userId) {
    const query = 'DELETE FROM users WHERE user_id = $1 RETURNING user_id';
    const result = await pool.query(query, [userId]);
    return result.rows[0];
  }
}

module.exports = User;