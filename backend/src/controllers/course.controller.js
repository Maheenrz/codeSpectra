const { Course, Enrollment } = require('../models');

class CourseController {
  // Create new course
  static async createCourse(req, res) {
    try {
      const { courseCode, courseName, semester, year } = req.body;
      const instructorId = req.user.userId;

      if (!courseCode || !courseName) {
        return res.status(400).json({ error: 'Course code and name are required' });
      }

      const course = await Course.create({
        courseCode,
        courseName,
        instructorId,
        semester,
        year
      });

      // Auto-generate join code after creation
      const joinCodeResult = await Course.generateJoinCode(course.course_id);
      course.join_code = joinCodeResult.join_code;

      res.status(201).json({
        message: 'Course created successfully',
        course
      });
    } catch (error) {
      console.error('Create course error:', error);
      if (error.code === '23505') {
        return res.status(409).json({ error: 'Course code already exists' });
      }
      res.status(500).json({ error: 'Failed to create course', details: error.message });
    }
  }

  // Get all courses
  static async getAllCourses(req, res) {
    try {
      const courses = await Course.findAll();
      res.json(courses);
    } catch (error) {
      console.error('Get courses error:', error);
      res.status(500).json({ error: 'Failed to get courses', details: error.message });
    }
  }

  // Get course by ID
  static async getCourseById(req, res) {
    try {
      const { courseId } = req.params;
      const course = await Course.findById(courseId);

      if (!course) {
        return res.status(404).json({ error: 'Course not found' });
      }

      res.json(course);
    } catch (error) {
      console.error('Get course error:', error);
      res.status(500).json({ error: 'Failed to get course', details: error.message });
    }
  }

  // Get instructor's courses
  static async getInstructorCourses(req, res) {
    try {
      const instructorId = req.user.userId;
      const courses = await Course.findByInstructor(instructorId);
      res.json(courses);
    } catch (error) {
      console.error('Get instructor courses error:', error);
      res.status(500).json({ error: 'Failed to get courses', details: error.message });
    }
  }

  // Get student's enrolled courses
  static async getStudentCourses(req, res) {
    try {
      const studentId = req.user.userId;
      const courses = await Enrollment.getStudentCourses(studentId);
      res.json(courses);
    } catch (error) {
      console.error('Get student courses error:', error);
      res.status(500).json({ error: 'Failed to get courses', details: error.message });
    }
  }

  // Update course
  static async updateCourse(req, res) {
    try {
      const { courseId } = req.params;
      const updates = req.body;

      const course = await Course.update(courseId, updates);
      if (!course) {
        return res.status(404).json({ error: 'Course not found' });
      }

      res.json({
        message: 'Course updated successfully',
        course
      });
    } catch (error) {
      console.error('Update course error:', error);
      res.status(500).json({ error: 'Failed to update course', details: error.message });
    }
  }

  // Delete course
  static async deleteCourse(req, res) {
    try {
      const { courseId } = req.params;

      const course = await Course.delete(courseId);
      if (!course) {
        return res.status(404).json({ error: 'Course not found' });
      }

      res.json({ message: 'Course deleted successfully' });
    } catch (error) {
      console.error('Delete course error:', error);
      res.status(500).json({ error: 'Failed to delete course', details: error.message });
    }
  }

  // Get course students
  static async getCourseStudents(req, res) {
    try {
      const { courseId } = req.params;
      const students = await Course.getStudents(courseId);
      res.json(students);
    } catch (error) {
      console.error('Get course students error:', error);
      res.status(500).json({ error: 'Failed to get students', details: error.message });
    }
  }

  // Manual enrollment by instructor
  static async enrollStudent(req, res) {
    try {
      const { courseId } = req.params;
      const { studentId } = req.body;

      const enrollment = await Enrollment.enroll(studentId, courseId);
      
      if (!enrollment) {
        return res.status(409).json({ error: 'Student already enrolled' });
      }

      res.status(201).json({
        message: 'Student enrolled successfully',
        enrollment
      });
    } catch (error) {
      console.error('Enroll student error:', error);
      res.status(500).json({ error: 'Failed to enroll student', details: error.message });
    }
  }

  // ========== JOIN CODE METHODS ==========

  // Get course by join code (preview before joining)
  static async getCourseByJoinCode(req, res) {
    try {
      const { joinCode } = req.params;
      const course = await Course.findByJoinCode(joinCode);
      
      if (!course) {
        return res.status(404).json({ error: 'Invalid join code' });
      }

      res.json(course);
    } catch (error) {
      console.error('Find by join code error:', error);
      res.status(500).json({ error: 'Failed to find course' });
    }
  }

  // Enroll using join code (student self-enrollment)
  static async enrollWithJoinCode(req, res) {
    try {
      const { joinCode } = req.body;
      const studentId = req.user.userId;

      if (!joinCode) {
        return res.status(400).json({ error: 'Join code is required' });
      }

      const result = await Course.enrollWithCode(studentId, joinCode);
      
      res.json({
        message: 'Successfully enrolled in course',
        enrollment: result.enrollment,
        courseId: result.courseId
      });
    } catch (error) {
      console.error('Enroll with code error:', error);
      res.status(400).json({ error: error.message });
    }
  }

  // Regenerate join code (instructor only)
  static async regenerateJoinCode(req, res) {
    try {
      const { courseId } = req.params;
      const result = await Course.generateJoinCode(courseId);
      
      res.json({
        message: 'Join code regenerated',
        joinCode: result.join_code
      });
    } catch (error) {
      console.error('Regenerate code error:', error);
      res.status(500).json({ error: 'Failed to regenerate code' });
    }
  }

  // Unenroll student
  static async unenrollStudent(req, res) {
    try {
      const { courseId, studentId } = req.params;

      const enrollment = await Enrollment.unenroll(studentId, courseId);
      if (!enrollment) {
        return res.status(404).json({ error: 'Enrollment not found' });
      }

      res.json({ message: 'Student unenrolled successfully' });
    } catch (error) {
      console.error('Unenroll student error:', error);
      res.status(500).json({ error: 'Failed to unenroll student', details: error.message });
    }
  }
}

module.exports = CourseController;