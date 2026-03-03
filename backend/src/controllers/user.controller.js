const { User } = require('../models');

class UserController {
  // Get all users (admin only)
  static async getAllUsers(req, res) {
    try {
      const users = await User.findAll();
      res.json(users);
    } catch (error) {
      console.error('Get all users error:', error);
      res.status(500).json({ error: 'Failed to get users', details: error.message });
    }
  }

  // Get users by role
  static async getUsersByRole(req, res) {
    try {
      const { role } = req.params;
      const users = await User.findByRole(role);
      res.json(users);
    } catch (error) {
      console.error('Get users by role error:', error);
      res.status(500).json({ error: 'Failed to get users', details: error.message });
    }
  }

  // Get user by ID
  static async getUserById(req, res) {
    try {
      const { userId } = req.params;
      const user = await User.findById(userId);
      
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json(user);
    } catch (error) {
      console.error('Get user error:', error);
      res.status(500).json({ error: 'Failed to get user', details: error.message });
    }
  }

  // Update user (admin only)
  static async updateUser(req, res) {
    try {
      const { userId } = req.params;
      const updates = req.body;

      const user = await User.update(userId, updates);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({ message: 'User updated successfully', user });
    } catch (error) {
      console.error('Update user error:', error);
      res.status(500).json({ error: 'Failed to update user', details: error.message });
    }
  }

  // Delete user (admin only)
  static async deleteUser(req, res) {
    try {
      const { userId } = req.params;

      const user = await User.delete(userId);
      if (!user) {
        return res.status(404).json({ error: 'User not found' });
      }

      res.json({ message: 'User deleted successfully' });
    } catch (error) {
      console.error('Delete user error:', error);
      res.status(500).json({ error: 'Failed to delete user', details: error.message });
    }
  }
}

module.exports = UserController;