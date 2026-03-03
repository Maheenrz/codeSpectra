const { body, param, query, validationResult } = require('express-validator');

// Handle validation errors
const handleValidationErrors = (req, res, next) => {
  const errors = validationResult(req);
  if (!errors.isEmpty()) {
    return res.status(400).json({ errors: errors.array() });
  }
  next();
};

// Common validations
const validateEmail = body('email')
  .isEmail()
  .normalizeEmail()
  .withMessage('Invalid email address');

const validatePassword = body('password')
  .isLength({ min: 8 })
  .withMessage('Password must be at least 8 characters');

const validateId = (field) => 
  param(field)
    .isInt({ min: 1 })
    .withMessage(`${field} must be a valid ID`);

// Registration validation
const validateRegistration = [
  validateEmail,
  validatePassword,
  body('firstName').trim().notEmpty().withMessage('First name is required'),
  body('lastName').trim().notEmpty().withMessage('Last name is required'),
  body('role').isIn(['student', 'instructor', 'admin']).withMessage('Invalid role'),
  handleValidationErrors
];

// Login validation
const validateLogin = [
  validateEmail,
  body('password').notEmpty().withMessage('Password is required'),
  handleValidationErrors
];

// Course validation
const validateCourse = [
  body('courseCode').trim().notEmpty().withMessage('Course code is required'),
  body('courseName').trim().notEmpty().withMessage('Course name is required'),
  handleValidationErrors
];

// Assignment validation
const validateAssignment = [
  body('courseId').isInt({ min: 1 }).withMessage('Valid course ID is required'),
  body('title').trim().notEmpty().withMessage('Title is required'),
  body('dueDate').isISO8601().withMessage('Valid due date is required'),
  handleValidationErrors
];

module.exports = {
  handleValidationErrors,
  validateRegistration,
  validateLogin,
  validateCourse,
  validateAssignment,
  validateId
};