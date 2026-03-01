import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import assignmentService from '../../services/assignmentService';
import submissionService from '../../services/submissionService';
import analysisService from '../../services/analysisService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Card from '../../components/common/Card';

const AssignmentDetail = () => {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const { user, isStudent, isInstructor } = useAuth();
  const [assignment, setAssignment] = useState(null);
  const [submissions, setSubmissions] = useState([]);
  const [mySubmission, setMySubmission] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    fetchAssignmentData();
  }, [assignmentId]);

  const fetchAssignmentData = async () => {
    try {
      const assignmentData = await assignmentService.getAssignmentById(assignmentId);
      setAssignment(assignmentData);

      if (isInstructor) {
        const submissionsData = await assignmentService.getAssignmentSubmissions(assignmentId);
        setSubmissions(submissionsData);
      } else if (isStudent) {
        const studentSubmissions = await submissionService.getStudentSubmissions();
        const mySubm = studentSubmissions.find(s => s.assignment_id === parseInt(assignmentId));
        setMySubmission(mySubm);
      }
    } catch (error) {
      console.error('Error fetching assignment:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnalyzeAll = async () => {
    if (!window.confirm('Start plagiarism analysis for all submissions?')) return;
    
    setAnalyzing(true);
    try {
      await analysisService.analyzeAssignment(assignmentId);
      alert('Analysis started! Results will be available shortly.');
      fetchAssignmentData();
    } catch (error) {
      alert('Failed to start analysis: ' + error.message);
    } finally {
      setAnalyzing(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading assignment..." />;
  if (!assignment) return <div>Assignment not found</div>;

  const isPastDue = new Date(assignment.due_date) < new Date();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <Link 
            to={`/courses/${assignment.course_id}`} 
            className="text-purple-600 hover:text-purple-700 mb-4 inline-block"
          >
            ← Back to Course
          </Link>
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{assignment.title}</h1>
              <div className="flex items-center gap-4 text-gray-600">
                <span>{assignment.course_code} - {assignment.course_name}</span>
                <span>•</span>
                <span>Due: {new Date(assignment.due_date).toLocaleString()}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  isPastDue ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                }`}>
                  {isPastDue ? 'Closed' : 'Open'}
                </span>
              </div>
            </div>
            {isStudent && !isPastDue && (
              <Link to={`/submissions/submit?assignmentId=${assignmentId}`} className="btn-primary">
                {mySubmission ? 'Resubmit' : 'Submit Assignment'}
              </Link>
            )}
            {isInstructor && (
              <button 
                onClick={handleAnalyzeAll}
                disabled={analyzing}
                className="btn-primary disabled:bg-gray-400"
              >
                {analyzing ? 'Analyzing...' : '🔍 Analyze All Submissions'}
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">Description</h2>
              <p className="text-gray-700 whitespace-pre-wrap">{assignment.description}</p>
            </Card>

            {/* Student View - My Submission */}
            {isStudent && mySubmission && (
              <Card>
                <h2 className="text-xl font-bold text-gray-900 mb-4">My Submission</h2>
                <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                  <div>
                    <p className="font-semibold text-gray-900">Submitted on {new Date(mySubmission.submitted_at).toLocaleString()}</p>
                    <p className="text-sm text-gray-600">{mySubmission.file_count || 0} files uploaded</p>
                    <span className={`inline-block mt-2 px-3 py-1 rounded-full text-xs font-semibold ${
                      mySubmission.analysis_status === 'completed' ? 'bg-green-100 text-green-700' :
                      mySubmission.analysis_status === 'processing' ? 'bg-blue-100 text-blue-700' :
                      mySubmission.analysis_status === 'failed' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    }`}>
                      {mySubmission.analysis_status}
                    </span>
                  </div>
                  <Link 
                    to={`/submissions/${mySubmission.submission_id}`}
                    className="btn-secondary"
                  >
                    View Details
                  </Link>
                </div>
              </Card>
            )}

            {/* Instructor View - Submissions List */}
            {isInstructor && (
              <Card>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-xl font-bold text-gray-900">
                    Submissions ({submissions.length})
                  </h2>
                  <Link 
                    to={`/analysis/assignment/${assignmentId}`}
                    className="text-purple-600 hover:text-purple-700 font-semibold"
                  >
                    View Analysis Report →
                  </Link>
                </div>

                {submissions.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No submissions yet</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b">
                          <th className="text-left py-3 px-4 font-semibold text-gray-900">Student</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-900">Submitted</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-900">Files</th>
                          <th className="text-left py-3 px-4 font-semibold text-gray-900">Status</th>
                          <th className="text-right py-3 px-4 font-semibold text-gray-900">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {submissions.map((submission) => (
                          <tr key={submission.submission_id} className="border-b last:border-0 hover:bg-gray-50">
                            <td className="py-3 px-4">
                              <p className="font-medium text-gray-900">{submission.student_name}</p>
                              <p className="text-sm text-gray-600">{submission.student_email}</p>
                            </td>
                            <td className="py-3 px-4 text-gray-600">
                              {new Date(submission.submitted_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 px-4 text-gray-600">
                              {submission.file_count || 0}
                            </td>
                            <td className="py-3 px-4">
                              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                submission.analysis_status === 'completed' ? 'bg-green-100 text-green-700' :
                                submission.analysis_status === 'processing' ? 'bg-blue-100 text-blue-700' :
                                submission.analysis_status === 'failed' ? 'bg-red-100 text-red-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {submission.analysis_status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right">
                              <Link 
                                to={`/submissions/${submission.submission_id}`}
                                className="text-purple-600 hover:text-purple-700 text-sm font-semibold"
                              >
                                View
                              </Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Settings */}
            <Card>
              <h3 className="font-bold text-gray-900 mb-4">Settings</h3>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Language</span>
                  <span className="font-semibold text-gray-900">{assignment.primary_language}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Max File Size</span>
                  <span className="font-semibold text-gray-900">{assignment.max_file_size_mb} MB</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Extensions</span>
                  <span className="font-semibold text-gray-900">{assignment.allowed_extensions}</span>
                </div>
              </div>
            </Card>

            {/* Detection Types */}
            <Card>
              <h3 className="font-bold text-gray-900 mb-4">Detection Types</h3>
              <div className="space-y-2">
                {assignment.enable_type1 && (
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Type-1 (Exact Copy)
                  </div>
                )}
                {assignment.enable_type2 && (
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Type-2 (Renamed)
                  </div>
                )}
                {assignment.enable_type3 && (
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Type-3 (Modified)
                  </div>
                )}
                {assignment.enable_type4 && (
                  <div className="flex items-center gap-2 text-sm text-gray-700">
                    <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                    Type-4 (AI Semantic)
                  </div>
                )}
              </div>
            </Card>

            {/* Thresholds */}
            <Card>
              <h3 className="font-bold text-gray-900 mb-4">Similarity Thresholds</h3>
              <div className="space-y-3">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-red-600 font-semibold">High</span>
                    <span className="text-gray-900 font-bold">{assignment.high_similarity_threshold}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-red-600 h-2 rounded-full" 
                      style={{ width: `${assignment.high_similarity_threshold}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-orange-600 font-semibold">Medium</span>
                    <span className="text-gray-900 font-bold">{assignment.medium_similarity_threshold}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-orange-600 h-2 rounded-full" 
                      style={{ width: `${assignment.medium_similarity_threshold}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignmentDetail;