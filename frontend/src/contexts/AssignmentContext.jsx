import React, { createContext, useContext, useState, useEffect } from 'react';

const AssignmentContext = createContext();

export const useAssignment = () => {
  const context = useContext(AssignmentContext);
  if (!context) {
    throw new Error('useAssignment must be used within AssignmentProvider');
  }
  return context;
};

export const AssignmentProvider = ({ children }) => {
  // Load from localStorage on init
  const [assignments, setAssignments] = useState(() => {
    const saved = localStorage.getItem('codespectra_assignments');
    return saved ? JSON.parse(saved) : [];
  });

  const [currentAssignment, setCurrentAssignment] = useState(null);

  // Save to localStorage whenever assignments change
  useEffect(() => {
    localStorage.setItem('codespectra_assignments', JSON.stringify(assignments));
  }, [assignments]);

  // Generate unique assignment code
  const generateCode = () => {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let code = '';
    for (let i = 0; i < 6; i++) {
      code += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return code;
  };

  // Create new assignment
  const createAssignment = (assignmentData) => {
    const newAssignment = {
      id: Date.now().toString(),
      code: generateCode(),
      createdAt: new Date().toISOString(),
      status: 'open',
      submissions: [],
      results: null,
      ...assignmentData
    };
    
    setAssignments(prev => [...prev, newAssignment]);
    return newAssignment;
  };

  // Get assignment by code
  const getAssignmentByCode = (code) => {
    return assignments.find(a => a.code === code);
  };

  // Get assignment by ID
  const getAssignmentById = (id) => {
    return assignments.find(a => a.id === id);
  };

  // Add student submission
  const addSubmission = (assignmentCode, submission) => {
    setAssignments(prev => prev.map(assignment => {
      if (assignment.code === assignmentCode) {
        return {
          ...assignment,
          submissions: [...assignment.submissions, {
            id: Date.now().toString(),
            submittedAt: new Date().toISOString(),
            ...submission
          }]
        };
      }
      return assignment;
    }));
  };

  // Update assignment results
  const updateResults = (assignmentId, results) => {
    setAssignments(prev => prev.map(assignment => {
      if (assignment.id === assignmentId) {
        return { ...assignment, results, status: 'analyzed' };
      }
      return assignment;
    }));
  };

  // Close assignment
  const closeAssignment = (assignmentId) => {
    setAssignments(prev => prev.map(assignment => {
      if (assignment.id === assignmentId) {
        return { ...assignment, status: 'closed' };
      }
      return assignment;
    }));
  };

  // Delete assignment
  const deleteAssignment = (assignmentId) => {
    setAssignments(prev => prev.filter(a => a.id !== assignmentId));
  };

  const value = {
    assignments,
    currentAssignment,
    setCurrentAssignment,
    createAssignment,
    getAssignmentByCode,
    getAssignmentById,
    addSubmission,
    updateResults,
    closeAssignment,
    deleteAssignment
  };

  return (
    <AssignmentContext.Provider value={value}>
      {children}
    </AssignmentContext.Provider>
  );
};