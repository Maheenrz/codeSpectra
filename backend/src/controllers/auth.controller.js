const jwt = require('jsonwebtoken');
const { User } = require('../models');

const JWT_SECRET     = process.env.JWT_SECRET || 'change-this-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

class AuthController {

  static async register(req, res) {
    try {
      const { email, password, firstName, lastName, role, institution } = req.body;

      if (!email || !password || !firstName || !lastName || !role) {
        return res.status(400).json({ error: 'Missing required fields' });
      }

      const existingUser = await User.findByEmail(email);
      if (existingUser) {
        return res.status(409).json({ error: 'Email already registered' });
      }

      const user = await User.create({ email, password, firstName, lastName, role, institution });

      const token = jwt.sign(
        { userId: user.user_id, email: user.email, role: user.role },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRES_IN }
      );

      res.status(201).json({
        message: 'User registered successfully',
        user: {
          userId:    user.user_id,
          email:     user.email,
          firstName: user.first_name,
          lastName:  user.last_name,
          role:      user.role,
        },
        token,
      });
    } catch (error) {
      console.error('Registration error:', error);
      res.status(500).json({ error: 'Registration failed', details: error.message });
    }
  }

  static async login(req, res) {
    try {
      const { email, password } = req.body;

      if (!email || !password) {
        return res.status(400).json({ error: 'Email and password are required' });
      }

      const user = await User.findByEmail(email);
      if (!user) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      if (!user.is_active) {
        return res.status(403).json({ error: 'Account is disabled' });
      }

      const isValidPassword = await User.verifyPassword(password, user.password_hash);
      if (!isValidPassword) {
        return res.status(401).json({ error: 'Invalid credentials' });
      }

      await User.updateLastLogin(user.user_id);

      const token = jwt.sign(
        { userId: user.user_id, email: user.email, role: user.role },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRES_IN }
      );

      res.json({
        message: 'Login successful',
        user: {
          userId:      user.user_id,
          email:       user.email,
          firstName:   user.first_name,
          lastName:    user.last_name,
          role:        user.role,
          institution: user.institution,
        },
        token,
      });
    } catch (error) {
      console.error('Login error:', error);
      res.status(500).json({ error: 'Login failed', details: error.message });
    }
  }

  static async getProfile(req, res) {
    try {
      const user = await User.findById(req.user.userId);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({
        userId:      user.user_id,
        email:       user.email,
        firstName:   user.first_name,
        lastName:    user.last_name,
        role:        user.role,
        institution: user.institution,
        isActive:    user.is_active,
        createdAt:   user.created_at,
        lastLogin:   user.last_login,
      });
    } catch (error) {
      console.error('Get profile error:', error);
      res.status(500).json({ error: 'Failed to get profile', details: error.message });
    }
  }

  static async updateProfile(req, res) {
    try {
      const { firstName, lastName, institution } = req.body;
      const updates = {};

      if (firstName)   updates.first_name  = firstName;
      if (lastName)    updates.last_name   = lastName;
      if (institution) updates.institution = institution;

      const user = await User.update(req.user.userId, updates);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({
        message: 'Profile updated successfully',
        user: {
          userId:      user.user_id,
          email:       user.email,
          firstName:   user.first_name,
          lastName:    user.last_name,
          role:        user.role,
          institution: user.institution,
        },
      });
    } catch (error) {
      console.error('Update profile error:', error);
      res.status(500).json({ error: 'Failed to update profile', details: error.message });
    }
  }
}

module.exports = AuthController;
