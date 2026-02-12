import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAssignment } from '../contexts/AssignmentContext';
import FileUploader from '../Components/FileUploader';

const StudentSubmission = () => {
  const { assignmentCode } = useParams();
  const navigate = useNavigate();
  const { getAssignmentByCode, addSubmission } = useAssignment();
  
  const [assignment, setAssignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [studentId, setStudentId] = useState('');
  const [studentName, setStudentName] = useState('');
  const [files, setFiles] = useState([]);
  const [errors, setErrors] = useState({});
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Load assignment
  useEffect(() => {
    const found = getAssignmentByCode(assignmentCode?.toUpperCase());
    setAssignment(found);
    setLoading(false);
    
    if (found) {
      // Initialize files array with null values
      setFiles(new Array(found.problems.length).fill(null));
    }
  }, [assignmentCode, getAssignmentByCode]);

  // Handle file selection for a problem
  const handleFileSelect = (index, file) => {
    const newFiles = [...files];
    newFiles[index] = file;
    setFiles(newFiles);
    
    // Clear error for this field
    if (errors[`file_${index}`]) {
      const newErrors = { ...errors };
      delete newErrors[`file_${index}`];
      setErrors(newErrors);
    }
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!studentId.trim()) {
      newErrors.studentId = 'Student ID is required';
    }
    
    if (!studentName.trim()) {
      newErrors.studentName = 'Name is required';
    }
    
    files.forEach((file, index) => {
      if (!file) {
        newErrors[`file_${index}`] = `Please upload file for Problem ${index + 1}`;
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSubmitting(true);
    
    try {
      // Create submission object with file data
      const filesData = await Promise.all(
        files.map((file, index) =>
          fileToBase64(file).then((fileData) => ({
            problemId: assignment.problems[index].id,
            problemName: assignment.problems[index].name,
            fileName: file.name,
            fileSize: file.size,
            // Store file content as base64 for localStorage
            fileData: fileData
          }))
        )
      );

      const submission = {
        studentId: studentId.trim(),
        studentName: studentName.trim(),
        files: filesData
      };
      
      addSubmission(assignmentCode.toUpperCase(), submission);
      setSubmitted(true);
    } catch (error) {
      console.error('Submission error:', error);
      setErrors({ submit: 'Failed to submit. Please try again.' });
    } finally {
      setSubmitting(false);
    }
  };

  // Convert file to base64
  const fileToBase64 = (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result);
      reader.onerror = (error) => reject(error);
    });
  };

  // Loading state
  if (loading) {
    return (
      <div className="student-submission loading">
        <div className="loader"></div>
        <p>Loading assignment...</p>
      </div>
    );
  }

  // Assignment not found
  if (!assignment) {
    return (
      <div className="student-submission not-found">
        <div className="error-card">
          <div className="error-icon">❌</div>
          <h2>Assignment Not Found</h2>
          <p>The code <strong>{assignmentCode}</strong> doesn't match any assignment.</p>
          <p>Please check the code and try again.</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            ← Go Home
          </button>
        </div>
      </div>
    );
  }

  // Assignment closed
  if (assignment.status === 'closed') {
    return (
      <div className="student-submission closed">
        <div className="warning-card">
          <div className="warning-icon">🔒</div>
          <h2>Submissions Closed</h2>
          <p>This assignment is no longer accepting submissions.</p>
          <p>Please contact your instructor if you need to submit.</p>
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            ← Go Home
          </button>
        </div>
      </div>
    );
  }

  // Success view after submission
  if (submitted) {
    return (
      <div className="student-submission success">
        <div className="success-card">
          <div className="success-icon">✅</div>
          <h2>Submission Successful!</h2>
          
          <div className="submission-summary">
            <p><strong>Student:</strong> {studentName} ({studentId})</p>
            <p><strong>Assignment:</strong> {assignment.name}</p>
            <p><strong>Files Submitted:</strong> {files.length}</p>
          </div>
          
          <div className="files-summary">
            {files.map((file, index) => (
              <div key={index} className="file-item">
                <span className="problem-name">#{index + 1} {assignment.problems[index].name}</span>
                <span className="file-name">📄 {file.name}</span>
              </div>
            ))}
          </div>
          
          <p className="timestamp">
            Submitted at {new Date().toLocaleString()}
          </p>
          
          <button className="btn btn-primary" onClick={() => navigate('/')}>
            Done
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="student-submission">
      <div className="submission-header">
        <h1>📤 Submit Assignment</h1>
        <div className="assignment-info">
          <h2>{assignment.name}</h2>
          {assignment.description && <p>{assignment.description}</p>}
          <span className="problem-count">
            {assignment.problems.length} problem{assignment.problems.length > 1 ? 's' : ''} to submit
          </span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="submission-form">
        {/* Student Info */}
        <section className="form-section">
          <h3>👤 Your Information</h3>
          
          <div className="form-row">
            <div className="form-group">
              <label htmlFor="studentId">Student ID *</label>
              <input
                type="text"
                id="studentId"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                placeholder="e.g., STU001"
                className={errors.studentId ? 'error' : ''}
              />
              {errors.studentId && <span className="error-text">{errors.studentId}</span>}
            </div>
            
            <div className="form-group">
              <label htmlFor="studentName">Your Name *</label>
              <input
                type="text"
                id="studentName"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                placeholder="e.g., John Doe"
                className={errors.studentName ? 'error' : ''}
              />
              {errors.studentName && <span className="error-text">{errors.studentName}</span>}
            </div>
          </div>
        </section>

        {/* File Uploads */}
        <section className="form-section">
          <h3>📁 Upload Your Solutions</h3>
          <p className="section-description">
            Upload one file for each problem. Accepted formats: .c, .cpp, .py, .java, .js, .ts
          </p>
          
          <div className="problems-upload-list">
            {assignment.problems.map((problem, index) => (
              <div 
                key={problem.id} 
                className={`problem-upload-card ${errors[`file_${index}`] ? 'has-error' : ''}`}
              >
                <div className="problem-info">
                  <span className="problem-number">#{index + 1}</span>
                  <div className="problem-details">
                    <h4>{problem.name}</h4>
                    {problem.description && <p>{problem.description}</p>}
                  </div>
                </div>
                
                <FileUploader
                  onFileSelect={(file) => handleFileSelect(index, file)}
                  currentFile={files[index]}
                  label={`Upload solution for ${problem.name}`}
                  helpText="Drag & drop or click to browse"
                />
                
                {errors[`file_${index}`] && (
                  <span className="error-text">{errors[`file_${index}`]}</span>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* Submit Error */}
        {errors.submit && (
          <div className="submit-error">
            <span className="error-text">{errors.submit}</span>
          </div>
        )}

        {/* Submit Button */}
        <div className="form-actions">
          <div className="files-status">
            {files.filter(f => f !== null).length} of {files.length} files selected
          </div>
          
          <button 
            type="submit" 
            className="btn btn-primary btn-lg"
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                Submitting...
              </>
            ) : (
              <>
                📤 Submit Assignment
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default StudentSubmission;