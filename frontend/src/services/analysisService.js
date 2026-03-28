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
    const t = threshold ?? 50;
    const response = await api.get(`/analysis/results/assignment/${assignmentId}?threshold=${t}`);
    return response.data;
  },

  async getPairDetail(pairId) {
    const response = await api.get(`/analysis/pair/${pairId}`);
    return response.data;
  },

  async analyzeFiles(formData) {
    const response = await api.post('/analysis/files', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 600000,
    });
    return response.data;
  },

  // Upload a class ZIP and return the job_id for polling.
  // The engine extracts the ZIP synchronously then runs pair analysis
  // in a background thread, so this call returns quickly.
  async analyzeClassZip(zipFile) {
    const form = new FormData();
    form.append('file', zipFile);
    const response = await api.post('/analysis/zip', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000,  // 2 minutes for upload + ZIP extraction
    });
    return response.data;  // { job_id, status, total_students, ... }
  },

  // Poll /analysis/zip/results/:jobId until the job finishes or we give up.
  async pollJobResults(jobId, onProgress) {
    const MAX_ATTEMPTS   = 600;  // 10 minutes at 1-second intervals
    const POLL_INTERVAL  = 1000;
    let attempts = 0;

    while (attempts < MAX_ATTEMPTS) {
      await new Promise(resolve => setTimeout(resolve, POLL_INTERVAL));
      attempts++;

      const response = await api.get(`/analysis/zip/results/${jobId}`);
      const data = response.data;

      if (onProgress && typeof data.progress === 'number') {
        onProgress(data.progress);
      }

      if (data.status === 'completed' || data.status === 'partial') {
        return data;
      }
      if (data.status === 'failed') {
        throw new Error(data.error || 'Analysis failed on the engine');
      }
    }
    throw new Error('Analysis timed out after 10 minutes');
  },

  async checkHealth() {
    const response = await api.get('/analysis/health');
    return response.data;
  },
};

export default analysisService;
