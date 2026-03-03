// frontend/src/services/analysisService.js
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
    const t   = threshold ?? 50;
    const url = `/analysis/results/assignment/${assignmentId}?threshold=${t}`;
    const response = await api.get(url);
    return response.data;
  },

  // ── Fetch single pair detail — returns fragments with source code ────────
  async getPairDetail(pairId) {
    const response = await api.get(`/analysis/pair/${pairId}`);
    return response.data;
  },

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
