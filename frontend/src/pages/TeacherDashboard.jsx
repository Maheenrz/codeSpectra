import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAssignment } from '../contexts/AssignmentContext';

const TeacherDashboard = () => {
  const { assignments, deleteAssignment, closeAssignment } = useAssignment();
  const navigate = useNavigate();
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  const handleDelete = (id) => {
    deleteAssignment(id);
    setDeleteConfirm(null);
  };

  const getStatusBadge = (status) => {
    const badges = {
      open: { class: 'badge-success', text: '🟢 Open' },
      closed: { class: 'badge-warning', text: '🟡 Closed' },
      analyzed: { class: 'badge-info', text: '🔵 Analyzed' }
    };
    return badges[status] || badges.open;
  };

  return (
    <div className="teacher-dashboard">
      <div className="dashboard-header">
        <h1>👨‍🏫 Teacher Dashboard</h1>
        <Link to="/teacher/create" className="btn btn-primary">
          ➕ Create New Assignment
        </Link>
      </div>

      {assignments.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📋</div>
          <h3>No Assignments Yet</h3>
          <p>Create your first assignment to get started.</p>
          <Link to="/teacher/create" className="btn btn-primary">
            Create Assignment
          </Link>
        </div>
      ) : (
        <div className="assignments-list">
          <h2>Your Assignments</h2>
          
          <div className="assignments-table-container">
            <table className="assignments-table">
              <thead>
                <tr>
                  <th>Assignment</th>
                  <th>Code</th>
                  <th>Problems</th>
                  <th>Submissions</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {assignments.map((assignment) => {
                  const status = getStatusBadge(assignment.status);
                  return (
                    <tr key={assignment.id}>
                      <td>
                        <strong>{assignment.name}</strong>
                      </td>
                      <td>
                        <code className="assignment-code">{assignment.code}</code>
                        <button 
                          className="copy-btn"
                          onClick={() => {
                            navigator.clipboard.writeText(assignment.code);
                          }}
                          title="Copy code"
                        >
                          📋
                        </button>
                      </td>
                      <td>{assignment.problems.length}</td>
                      <td>
                        <span className="submissions-count">
                          {assignment.submissions.length}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${status.class}`}>
                          {status.text}
                        </span>
                      </td>
                      <td>
                        {new Date(assignment.createdAt).toLocaleDateString()}
                      </td>
                      <td className="actions-cell">
                        <button
                          className="btn btn-sm btn-outline"
                          onClick={() => navigate(`/submit/${assignment.code}`)}
                          title="View submission page"
                        >
                          👁️
                        </button>
                        
                        {assignment.submissions.length > 0 && (
                          <button
                            className="btn btn-sm btn-primary"
                            onClick={() => navigate(`/teacher/results/${assignment.id}`)}
                            title="View/Analyze results"
                          >
                            📊
                          </button>
                        )}
                        
                        {assignment.status === 'open' && (
                          <button
                            className="btn btn-sm btn-warning"
                            onClick={() => closeAssignment(assignment.id)}
                            title="Close submissions"
                          >
                            🔒
                          </button>
                        )}
                        
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => setDeleteConfirm(assignment.id)}
                          title="Delete assignment"
                        >
                          🗑️
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirm && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>⚠️ Delete Assignment?</h3>
            <p>This will permanently delete the assignment and all submissions.</p>
            <div className="modal-actions">
              <button 
                className="btn btn-outline"
                onClick={() => setDeleteConfirm(null)}
              >
                Cancel
              </button>
              <button 
                className="btn btn-danger"
                onClick={() => handleDelete(deleteConfirm)}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TeacherDashboard;