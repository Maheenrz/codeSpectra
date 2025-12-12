const express = require('express');
const router = express.Router();
const courseController = require('../controllers/courseController');
const authMiddleware = require('../middleware/auth');
const instructorMiddleware = require('../middleware/instructor');

// All routes require authentication
router.use(authMiddleware);

// Get all courses for current user
router.get('/', courseController.getAllCourses);

// Create course (instructor only)
router.post('/', instructorMiddleware, courseController.createCourse);

// Get single course
router.get('/:id', courseController.getCourseById);

// Update course (instructor only)
router.put('/:id', instructorMiddleware, courseController.updateCourse);

// Delete course (instructor only)
router.delete('/:id', instructorMiddleware, courseController.deleteCourse);

// Get assignments for course
router.get('/:id/assignments', courseController.getCourseAssignments);

// Enroll student in course (instructor only)
router.post('/:id/enroll', instructorMiddleware, courseController.enrollStudent);

module.exports = router;