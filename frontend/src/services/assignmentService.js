import api from '../utils/api';

const assignmentService = {
  async getAssignmentById(assignmentId) {
    const response = await api.get(`/assignments/${assignmentId}`);
    return response.data;
  },

  async getCourseAssignments(courseId) {
    const response = await api.get(`/assignments/course/${courseId}`);
    return response.data;
  },

  async createAssignment(assignmentData) {
    const response = await api.post('/assignments', assignmentData);
    return response.data;
  },

  async updateAssignment(assignmentId, updates) {
    const response = await api.put(`/assignments/${assignmentId}`, updates);
    return response.data;
  },

  async deleteAssignment(assignmentId) {
    const response = await api.delete(`/assignments/${assignmentId}`);
    return response.data;
  },

  async getAssignmentSubmissions(assignmentId) {
    const response = await api.get(`/assignments/${assignmentId}/submissions`);
    return response.data;
  },
};

export default assignmentService;