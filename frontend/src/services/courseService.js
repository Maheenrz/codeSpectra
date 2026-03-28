import api from '../utils/api';

const courseService = {
  async getAllCourses() {
    const response = await api.get('/courses');
    return response.data;
  },

  async getCourseById(courseId) {
    const response = await api.get(`/courses/${courseId}`);
    return response.data;
  },

  async getInstructorCourses() {
    const response = await api.get('/courses/my-courses');
    return response.data;
  },

  async getStudentCourses() {
    const response = await api.get('/courses/enrolled');
    return response.data;
  },

  async createCourse(courseData) {
    const response = await api.post('/courses', courseData);
    return response.data;
  },

  async updateCourse(courseId, updates) {
    const response = await api.put(`/courses/${courseId}`, updates);
    return response.data;
  },

  async deleteCourse(courseId) {
    const response = await api.delete(`/courses/${courseId}`);
    return response.data;
  },

  async getCourseStudents(courseId) {
    const response = await api.get(`/courses/${courseId}/students`);
    return response.data;
  },

  async enrollStudent(courseId, studentId) {
    const response = await api.post(`/courses/${courseId}/enroll`, { studentId });
    return response.data;
  },

  async unenrollStudent(courseId, studentId) {
    const response = await api.delete(`/courses/${courseId}/students/${studentId}`);
    return response.data;
  },

  async getCourseByJoinCode(joinCode) {
    const response = await api.get(`/courses/join/${joinCode}`);
    return response.data;
  },

  async enrollWithJoinCode(joinCode) {
    const response = await api.post('/courses/join', { joinCode });
    return response.data;
  },

  async regenerateJoinCode(courseId) {
    const response = await api.post(`/courses/${courseId}/regenerate-code`);
    return response.data;
  },
};

export default courseService;
