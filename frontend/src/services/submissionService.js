import api from '../utils/api';

const submissionService = {
  async createSubmission(formData) {
    const response = await api.post('/submissions', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getSubmissionById(submissionId) {
    const response = await api.get(`/submissions/${submissionId}`);
    return response.data;
  },

  async getStudentSubmissions() {
    const response = await api.get('/submissions/my-submissions');
    return response.data;
  },

  async getAssignmentSubmissions(assignmentId) {
    const response = await api.get(`/submissions/assignment/${assignmentId}`);
    return response.data;
  },

  async deleteSubmission(submissionId) {
    const response = await api.delete(`/submissions/${submissionId}`);
    return response.data;
  },
};

export default submissionService;