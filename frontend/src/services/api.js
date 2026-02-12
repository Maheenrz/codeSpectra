const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

export const api = {
  // Analyze assignment
  analyzeAssignment: async (assignmentId, submissions, problems) => {
    try {
      // Create FormData with all files grouped by problem
      const formData = new FormData();
      
      // Add assignment metadata
      formData.append('assignment_id', assignmentId);
      formData.append('problems', JSON.stringify(problems));
      
      // Group files by problem
      const groupedFiles = {};
      problems.forEach((_, index) => {
        groupedFiles[`problem_${index + 1}`] = [];
      });
      
      // Add each student's files
      submissions.forEach(submission => {
        submission.files.forEach((file, index) => {
          if (file) {
            const problemKey = `problem_${index + 1}`;
            // Rename file to include student ID
            const renamedFile = new File(
              [file], 
              `${submission.studentId}_${file.name}`,
              { type: file.type }
            );
            formData.append(problemKey, renamedFile);
          }
        });
      });
      
      const response = await fetch(`${API_BASE_URL}/api/assignment/analyze`, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) {
        throw new Error('Analysis failed');
      }
      
      return await response.json();
    } catch (error) {
      console.error('API Error:', error);
      throw error;
    }
  },

  // Health check
  healthCheck: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      return response.ok;
    } catch {
      return false;
    }
  }
};