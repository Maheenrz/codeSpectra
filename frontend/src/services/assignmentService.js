import api from '../utils/api';

const assignmentService = {
  async createAssignment(assignmentData) {
    const response = await api.post('/assignments', assignmentData);
    return response.data;
  },

  async getAssignmentById(assignmentId) {
    const response = await api.get(`/assignments/${assignmentId}`);
    return response.data;
  },

  async getCourseAssignments(courseId) {
    const response = await api.get(`/assignments/course/${courseId}`);
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

  async getQuestionById(questionId) {
    const response = await api.get(`/assignments/questions/${questionId}`);
    return response.data;
  },

  async updateQuestion(questionId, updates) {
    const response = await api.put(`/assignments/questions/${questionId}`, updates);
    return response.data;
  },

  async deleteQuestion(questionId) {
    const response = await api.delete(`/assignments/questions/${questionId}`);
    return response.data;
  },

  async getQuestionSubmissions(questionId) {
    const response = await api.get(`/assignments/questions/${questionId}/submissions`);
    return response.data;
  },

  // Returns the default file extensions we allow for a given primary language.
  getExtensionsForLanguage(language) {
    const extensionMap = {
      cpp:        ['.cpp', '.c', '.h', '.hpp', '.cc', '.cxx'],
      c:          ['.c', '.h'],
      java:       ['.java'],
      python:     ['.py'],
      javascript: ['.js', '.jsx', '.ts', '.tsx'],
      mixed:      ['.cpp', '.c', '.h', '.java', '.py', '.js'],
    };
    return extensionMap[language] || extensionMap.mixed;
  },

  formatExtensionsDisplay(extensions) {
    if (!extensions || extensions.length === 0) return 'Any file type';
    return extensions.join(', ');
  },
};

export default assignmentService;
