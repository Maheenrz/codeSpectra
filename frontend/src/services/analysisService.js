import api from '../utils/api';

const analysisService = {
  async analyzeSubmission(submissionId) {
    const response = await api.post(`/analysis/submission/${submissionId}`);
    return response.data;
  },

  async analyzeAssignment(assignmentId) {
    const response = await api.post(`/analysis/assignment/${assignmentId}`);
    return response.data;
  },

  async getSubmissionResults(submissionId) {
    const response = await api.get(`/analysis/results/submission/${submissionId}`);
    return response.data;
  },

  async getAssignmentResults(assignmentId, threshold) {
    const url = threshold 
      ? `/analysis/results/assignment/${assignmentId}?threshold=${threshold}`
      : `/analysis/results/assignment/${assignmentId}`;
    const response = await api.get(url);
    return response.data;
  },

  // Direct file upload — generic analysis, no assignment needed
  // Calls /api/analyze/detailed on the engine, returns all_pairs with fragment data
  async analyzeFiles(formData) {
    const response = await api.post('/analysis/files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,
    });
    return response.data;
  },

  async checkHealth() {
    const response = await api.get('/analysis/health');
    return response.data;
  },
};

export default analysisService;