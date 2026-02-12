import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAssignment } from '../contexts/AssignmentContext';

const AssignmentResults = () => {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const { getAssignmentById, updateResults } = useAssignment();
  
  const [assignment, setAssignment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [selectedProblem, setSelectedProblem] = useState(null);
  const [error, setError] = useState(null);

  // Load assignment
  useEffect(() => {
    const found = getAssignmentById(assignmentId);
    setAssignment(found);
    setLoading(false);
    
    if (found && found.problems.length > 0) {
      setSelectedProblem(found.problems[0].id);
    }
  }, [assignmentId, getAssignmentById]);

  // Run analysis (mock for now - connect to your backend)
  const runAnalysis = async () => {
    setAnalyzing(true);
    setError(null);
    
    try {
      // Simulate analysis delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Generate mock results
      const mockResults = generateMockResults(assignment);
      updateResults(assignmentId, mockResults);
      
      // Refresh assignment
      setAssignment(getAssignmentById(assignmentId));
    } catch (err) {
      setError('Analysis failed. Please try again.');
      console.error(err);
    } finally {
      setAnalyzing(false);
    }
  };

  // Generate mock results for demo
  const generateMockResults = (assignment) => {
    const results = {};
    
    assignment.problems.forEach(problem => {
      const submissions = assignment.submissions.map(s => ({
        studentId: s.studentId,
        studentName: s.studentName
      }));
      
      // Generate pairs
      const pairs = [];
      for (let i = 0; i < submissions.length; i++) {
        for (let j = i + 1; j < submissions.length; j++) {
          const structuralScore = Math.random() * 0.5 + 0.3;
          const semanticScore = Math.random() * 0.5 + 0.4;
          
          pairs.push({
            studentA: submissions[i],
            studentB: submissions[j],
            structuralScore: structuralScore,
            semanticScore: semanticScore,
            similarityLevel: semanticScore > 0.8 ? 'HIGH' : semanticScore > 0.6 ? 'MEDIUM' : 'LOW',
            isOutlier: structuralScore > 0.7 && semanticScore > 0.8
          });
        }
      }
      
      // Sort by semantic score
      pairs.sort((a, b) => b.semanticScore - a.semanticScore);
      
      results[problem.id] = {
        problemName: problem.name,
        totalSubmissions: submissions.length,
        totalComparisons: pairs.length,
        averageStructural: pairs.reduce((acc, p) => acc + p.structuralScore, 0) / pairs.length,
        averageSemantic: pairs.reduce((acc, p) => acc + p.semanticScore, 0) / pairs.length,
        outlierCount: pairs.filter(p => p.isOutlier).length,
        pairs: pairs
      };
    });
    
    return {
      analyzedAt: new Date().toISOString(),
      results
    };
  };

  if (loading) {
    return (
      <div className="results-page loading">
        <div className="loader"></div>
        <p>Loading assignment...</p>
      </div>
    );
  }

  if (!assignment) {
    return (
      <div className="results-page not-found">
        <div className="error-card">
          <h2>Assignment Not Found</h2>
          <button className="btn btn-primary" onClick={() => navigate('/teacher')}>
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const results = assignment.results;
  const currentProblemResults = results?.results?.[selectedProblem];

  return (
    <div className="results-page">
      <div className="results-header">
        <button className="back-btn" onClick={() => navigate('/teacher')}>
          ← Back to Dashboard
        </button>
        <h1>📊 {assignment.name}</h1>
        <span className="submission-count">
          {assignment.submissions.length} submissions
        </span>
      </div>

      {/* No submissions */}
      {assignment.submissions.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📭</div>
          <h3>No Submissions Yet</h3>
          <p>Share the assignment code with your students to collect submissions.</p>
          <div className="code-display">
            <span>Code: </span>
            <code>{assignment.code}</code>
          </div>
        </div>
      ) : (
        <>
          {/* Submissions Overview */}
          <section className="submissions-overview">
            <h2>📋 Submissions</h2>
            <div className="submissions-grid">
              {assignment.submissions.map((sub, index) => (
                <div key={sub.id || index} className="submission-card">
                  <div className="student-info">
                    <span className="student-name">{sub.studentName}</span>
                    <span className="student-id">{sub.studentId}</span>
                  </div>
                  <div className="submission-time">
                    {new Date(sub.submittedAt).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Analysis Section */}
          <section className="analysis-section">
            <div className="analysis-header">
              <h2>🔬 Similarity Analysis</h2>
              {assignment.submissions.length >= 2 ? (
                <button 
                  className="btn btn-primary"
                  onClick={runAnalysis}
                  disabled={analyzing}
                >
                  {analyzing ? (
                    <>
                      <span className="spinner"></span>
                      Analyzing...
                    </>
                  ) : results ? (
                    '🔄 Re-run Analysis'
                  ) : (
                    '▶️ Run Analysis'
                  )}
                </button>
              ) : (
                <span className="help-text">Need at least 2 submissions to analyze</span>
              )}
            </div>

            {error && <div className="error-message">{error}</div>}

            {/* Results Display */}
            {results && (
              <div className="results-content">
                <p className="analyzed-time">
                  Last analyzed: {new Date(results.analyzedAt).toLocaleString()}
                </p>

                {/* Problem Tabs */}
                <div className="problem-tabs">
                  {assignment.problems.map(problem => {
                    const probResults = results.results[problem.id];
                    return (
                      <button
                        key={problem.id}
                        className={`tab ${selectedProblem === problem.id ? 'active' : ''}`}
                        onClick={() => setSelectedProblem(problem.id)}
                      >
                        <span className="tab-name">{problem.name}</span>
                        {probResults && probResults.outlierCount > 0 && (
                          <span className="outlier-badge">
                            {probResults.outlierCount} 🔴
                          </span>
                        )}
                      </button>
                    );
                  })}
                </div>

                {/* Problem Results */}
                {currentProblemResults && (
                  <div className="problem-results">
                    {/* Stats */}
                    <div className="stats-grid">
                      <div className="stat-card">
                        <span className="stat-value">{currentProblemResults.totalSubmissions}</span>
                        <span className="stat-label">Submissions</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-value">{currentProblemResults.totalComparisons}</span>
                        <span className="stat-label">Comparisons</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-value">
                          {(currentProblemResults.averageStructural * 100).toFixed(0)}%
                        </span>
                        <span className="stat-label">Avg Structural</span>
                      </div>
                      <div className="stat-card">
                        <span className="stat-value">
                          {(currentProblemResults.averageSemantic * 100).toFixed(0)}%
                        </span>
                        <span className="stat-label">Avg Semantic</span>
                      </div>
                      <div className="stat-card highlight">
                        <span className="stat-value">{currentProblemResults.outlierCount}</span>
                        <span className="stat-label">Outliers 🔴</span>
                      </div>
                    </div>

                    {/* Pairs Table */}
                    <div className="pairs-table-container">
                      <h3>Similarity Pairs</h3>
                      <table className="pairs-table">
                        <thead>
                          <tr>
                            <th>Student A</th>
                            <th>Student B</th>
                            <th>Structural</th>
                            <th>Semantic</th>
                            <th>Level</th>
                            <th>Flag</th>
                          </tr>
                        </thead>
                        <tbody>
                          {currentProblemResults.pairs.map((pair, index) => (
                            <tr 
                              key={index}
                              className={pair.isOutlier ? 'outlier-row' : ''}
                            >
                              <td>
                                <span className="student-name">{pair.studentA.studentName}</span>
                                <span className="student-id">{pair.studentA.studentId}</span>
                              </td>
                              <td>
                                <span className="student-name">{pair.studentB.studentName}</span>
                                <span className="student-id">{pair.studentB.studentId}</span>
                              </td>
                              <td>
                                <span className={`score ${getScoreClass(pair.structuralScore)}`}>
                                  {(pair.structuralScore * 100).toFixed(0)}%
                                </span>
                              </td>
                              <td>
                                <span className={`score ${getScoreClass(pair.semanticScore)}`}>
                                  {(pair.semanticScore * 100).toFixed(0)}%
                                </span>
                              </td>
                              <td>
                                <span className={`level-badge level-${pair.similarityLevel.toLowerCase()}`}>
                                  {pair.similarityLevel}
                                </span>
                              </td>
                              <td>
                                {pair.isOutlier && <span className="outlier-flag">🔴</span>}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>
            )}
          </section>
        </>
      )}
    </div>
  );
};

// Helper function for score styling
const getScoreClass = (score) => {
  if (score >= 0.8) return 'high';
  if (score >= 0.6) return 'medium';
  return 'low';
};

export default AssignmentResults;