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
      timeout: 600000,   // 10 min — large batches of files take time
    });
    return response.data;
  },

  // ── Class ZIP async flow ───────────────────────────────────────────────
  // Upload a single class ZIP (containing student ZIPs or folders).
  // Returns {job_id, status, total_students, student_names}.
  async analyzeClassZip(zipFile) {
    const form = new FormData();
    form.append('file', zipFile);
    const response = await api.post('/analysis/zip', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,    // 2 min for large ZIP uploads
    });
    return response.data;
  },

  // Poll a class-ZIP analysis job until complete.
  async pollZipResults(jobId) {
    const response = await api.get(`/analysis/zip/results/${jobId}`);
    return response.data;
  },

  async checkHealth() {
    const response = await api.get('/analysis/health');
    return response.data;
  },
};

export default analysisService;
