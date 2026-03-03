const express = require('express');
const router = express.Router();
const UserController = require('../controllers/user.controller');
const { authenticateToken, requireAdmin } = require('../middleware/auth');

// All routes require authentication
router.use(authenticateToken);

// Get all users (admin only)
router.get('/', requireAdmin, UserController.getAllUsers);

// Get users by role (admin only)
router.get('/role/:role', requireAdmin, UserController.getUsersByRole);

// Get user by ID
router.get('/:userId', UserController.getUserById);

// Update user (admin only)
router.put('/:userId', requireAdmin, UserController.updateUser);

// Delete user (admin only)
router.delete('/:userId', requireAdmin, UserController.deleteUser);

module.exports = router;