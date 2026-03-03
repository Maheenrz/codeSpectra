const express = require('express');
const router = express.Router();
const CourseController = require('../controllers/course.controller');
const { authenticateToken, requireInstructor, requireRole } = require('../middleware/auth');
const { validateCourse } = require('../middleware/validation');

// All routes require authentication
router.use(authenticateToken);

// ========== COURSE CRUD ==========

// Create course (instructor only)
router.post('/', requireInstructor, validateCourse, CourseController.createCourse);

// Get all courses
router.get('/', CourseController.getAllCourses);

// Get instructor's courses
router.get('/my-courses', requireInstructor, CourseController.getInstructorCourses);

// Get student's enrolled courses
router.get('/enrolled', requireRole('student'), CourseController.getStudentCourses);

// Get course by ID
router.get('/:courseId', CourseController.getCourseById);

// Update course (instructor only)
router.put('/:courseId', requireInstructor, CourseController.updateCourse);

// Delete course (instructor only)
router.delete('/:courseId', requireInstructor, CourseController.deleteCourse);

// ========== ENROLLMENT MANAGEMENT ==========

// Get course students
router.get('/:courseId/students', CourseController.getCourseStudents);

// Manual enrollment by instructor
router.post('/:courseId/enroll', requireInstructor, CourseController.enrollStudent);

// Unenroll student
router.delete('/:courseId/students/:studentId', requireInstructor, CourseController.unenrollStudent);

// ========== JOIN CODE ROUTES ==========

// Get course by join code (for preview)
router.get('/join/:joinCode', CourseController.getCourseByJoinCode);

// Enroll using join code (student self-enrollment)
router.post('/join', requireRole('student'), CourseController.enrollWithJoinCode);

// Regenerate join code (instructor only)
router.post('/:courseId/regenerate-code', requireInstructor, CourseController.regenerateJoinCode);

module.exports = router;