const express = require('express');
const router = express.Router();
const courseController = require('../controllers/course.controller');
const { authenticate, isInstructor } = require('../middleware/auth.middleware');

// All routes require authentication
router.use(authenticate);

// Get all courses for current user
router.get('/', courseController.getAllCourses);

// Create course (instructor only)
router.post('/', isInstructor, courseController.createCourse);

// Get single course
router.get('/:id', courseController.getCourseById);

// Update course (instructor only)
router.put('/:id', isInstructor, courseController.updateCourse);

// Delete course (instructor only)
router.delete('/:id', isInstructor, courseController.deleteCourse);

// Get assignments for course
router.get('/:id/assignments', courseController.getCourseAssignments);

// Enroll student in course (instructor only)
router.post('/:id/enroll', isInstructor, courseController.enrollStudent);

module.exports = router;