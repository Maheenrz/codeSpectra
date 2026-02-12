import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAssignment } from '../contexts/AssignmentContext';

const CreateAssignment = () => {
  const navigate = useNavigate();
  const { createAssignment } = useAssignment();
  
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    numProblems: 1,
    problems: [{ name: 'Problem 1', description: '' }]
  });
  
  const [errors, setErrors] = useState({});
  const [createdAssignment, setCreatedAssignment] = useState(null);

  // Handle number of problems change
  const handleNumProblemsChange = (num) => {
    const newNum = Math.max(1, Math.min(10, parseInt(num) || 1));
    
    // Adjust problems array
    let newProblems = [...formData.problems];
    
    if (newNum > formData.problems.length) {
      // Add new problems
      for (let i = formData.problems.length; i < newNum; i++) {
        newProblems.push({ name: `Problem ${i + 1}`, description: '' });
      }
    } else {
      // Remove extra problems
      newProblems = newProblems.slice(0, newNum);
    }
    
    setFormData({
      ...formData,
      numProblems: newNum,
      problems: newProblems
    });
  };

  // Handle problem field change
  const handleProblemChange = (index, field, value) => {
    const newProblems = [...formData.problems];
    newProblems[index] = { ...newProblems[index], [field]: value };
    setFormData({ ...formData, problems: newProblems });
  };

  // Validate form
  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name.trim()) {
      newErrors.name = 'Assignment name is required';
    }
    
    formData.problems.forEach((problem, index) => {
      if (!problem.name.trim()) {
        newErrors[`problem_${index}`] = 'Problem name is required';
      }
    });
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle form submit
  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    const assignment = createAssignment({
      name: formData.name.trim(),
      description: formData.description.trim(),
      problems: formData.problems.map((p, i) => ({
        id: `problem_${i + 1}`,
        number: i + 1,
        name: p.name.trim(),
        description: p.description.trim()
      }))
    });
    
    setCreatedAssignment(assignment);
  };

  // Success view after creation
  if (createdAssignment) {
    return (
      <div className="create-assignment success-view">
        <div className="success-card">
          <div className="success-icon">✅</div>
          <h2>Assignment Created!</h2>
          
          <div className="assignment-details">
            <h3>{createdAssignment.name}</h3>
            <p>{createdAssignment.problems.length} problem(s)</p>
          </div>
          
          <div className="assignment-code-display">
            <label>Share this code with your students:</label>
            <div className="code-box">
              <span className="code">{createdAssignment.code}</span>
              <button 
                className="copy-btn"
                onClick={() => navigator.clipboard.writeText(createdAssignment.code)}
              >
                📋 Copy
              </button>
            </div>
          </div>
          
          <div className="share-link">
            <label>Or share this link:</label>
            <div className="link-box">
              <input 
                type="text" 
                readOnly 
                value={`${window.location.origin}/submit/${createdAssignment.code}`}
              />
              <button 
                className="copy-btn"
                onClick={() => navigator.clipboard.writeText(
                  `${window.location.origin}/submit/${createdAssignment.code}`
                )}
              >
                📋 Copy
              </button>
            </div>
          </div>
          
          <div className="success-actions">
            <button 
              className="btn btn-outline"
              onClick={() => navigate('/teacher')}
            >
              ← Back to Dashboard
            </button>
            <button 
              className="btn btn-primary"
              onClick={() => navigate(`/submit/${createdAssignment.code}`)}
            >
              View Submission Page →
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="create-assignment">
      <div className="page-header">
        <button className="back-btn" onClick={() => navigate('/teacher')}>
          ← Back
        </button>
        <h1>📝 Create New Assignment</h1>
      </div>

      <form onSubmit={handleSubmit} className="assignment-form">
        {/* Basic Info */}
        <section className="form-section">
          <h2>Basic Information</h2>
          
          <div className="form-group">
            <label htmlFor="name">Assignment Name *</label>
            <input
              type="text"
              id="name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., CS101 Week 5 Assignment"
              className={errors.name ? 'error' : ''}
            />
            {errors.name && <span className="error-text">{errors.name}</span>}
          </div>
          
          <div className="form-group">
            <label htmlFor="description">Description (Optional)</label>
            <textarea
              id="description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Any instructions for students..."
              rows={3}
            />
          </div>
        </section>

        {/* Number of Problems */}
        <section className="form-section">
          <h2>Problems</h2>
          
          <div className="form-group">
            <label htmlFor="numProblems">Number of Problems *</label>
            <div className="number-input-group">
              <button 
                type="button"
                className="num-btn"
                onClick={() => handleNumProblemsChange(formData.numProblems - 1)}
                disabled={formData.numProblems <= 1}
              >
                −
              </button>
              <input
                type="number"
                id="numProblems"
                value={formData.numProblems}
                onChange={(e) => handleNumProblemsChange(e.target.value)}
                min={1}
                max={10}
              />
              <button 
                type="button"
                className="num-btn"
                onClick={() => handleNumProblemsChange(formData.numProblems + 1)}
                disabled={formData.numProblems >= 10}
              >
                +
              </button>
            </div>
            <span className="help-text">Students will upload one file per problem</span>
          </div>
        </section>

        {/* Problem Details */}
        <section className="form-section">
          <h2>Problem Details</h2>
          
          <div className="problems-list">
            {formData.problems.map((problem, index) => (
              <div key={index} className="problem-card">
                <div className="problem-header">
                  <span className="problem-number">#{index + 1}</span>
                </div>
                
                <div className="form-group">
                  <label>Problem Name *</label>
                  <input
                    type="text"
                    value={problem.name}
                    onChange={(e) => handleProblemChange(index, 'name', e.target.value)}
                    placeholder={`e.g., Factorial, Fibonacci, etc.`}
                    className={errors[`problem_${index}`] ? 'error' : ''}
                  />
                  {errors[`problem_${index}`] && (
                    <span className="error-text">{errors[`problem_${index}`]}</span>
                  )}
                </div>
                
                <div className="form-group">
                  <label>Description (Optional)</label>
                  <input
                    type="text"
                    value={problem.description}
                    onChange={(e) => handleProblemChange(index, 'description', e.target.value)}
                    placeholder="Brief description of the problem"
                  />
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Submit */}
        <div className="form-actions">
          <button type="button" className="btn btn-outline" onClick={() => navigate('/teacher')}>
            Cancel
          </button>
          <button type="submit" className="btn btn-primary btn-lg">
            ✨ Create Assignment
          </button>
        </div>
      </form>
    </div>
  );
};

export default CreateAssignment;