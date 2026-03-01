import React, { useState, useEffect } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';  // ⭐ ADD THIS IMPORT
import assignmentService from '../../services/assignmentService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Card from '../../components/common/Card';

const CourseDetail = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  const { isInstructor } = useAuth();
  const [course, setCourse] = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents] = useState([]);
  const [activeTab, setActiveTab] = useState('assignments');
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);  // ⭐ ADD THIS

  useEffect(() => {
    fetchCourseData();
  }, [courseId]);

  const fetchCourseData = async () => {
    try {
      const [courseData, assignmentsData] = await Promise.all([
        courseService.getCourseById(courseId),
        assignmentService.getCourseAssignments(courseId),
      ]);
      
      setCourse(courseData);
      setAssignments(assignmentsData);

      if (isInstructor) {
        const studentsData = await courseService.getCourseStudents(courseId);
        setStudents(studentsData);
      }
    } catch (error) {
      console.error('Error fetching course:', error);
    } finally {
      setLoading(false);
    }
  };

  // ⭐ ADD THIS FUNCTION
  const handleRegenerateCode = async () => {
    if (!window.confirm('Generate a new join code? The old code will stop working.')) return;
    
    setRegenerating(true);
    try {
      const result = await courseService.regenerateJoinCode(courseId);
      setCourse({ ...course, join_code: result.joinCode });
      alert('✅ New join code generated!');
    } catch (error) {
      console.error('Regenerate error:', error);
      alert('❌ Failed to regenerate code: ' + (error.response?.data?.error || error.message));
    } finally {
      setRegenerating(false);
    }
  };

  // ⭐ ADD THIS FUNCTION
  const handleCopyCode = () => {
    if (course?.join_code) {
      navigator.clipboard.writeText(course.join_code);
      alert('✅ Join code copied to clipboard!');
    }
  };

  if (loading) return <LoadingSpinner message="Loading course..." />;
  if (!course) return <div>Course not found</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 text-white">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <Link to="/courses" className="text-purple-100 hover:text-white mb-4 inline-block">
            ← Back to Courses
          </Link>
          <h1 className="text-4xl font-bold mb-2">
            {course.course_code} - {course.course_name}
          </h1>
          <div className="flex items-center gap-6 text-purple-100">
            <span>{course.instructor_name}</span>
            <span>•</span>
            <span>{course.semester} {course.year}</span>
            <span>•</span>
            <span>{students.length} Students</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Tabs */}
        <div className="mb-6 border-b">
          <div className="flex gap-8">
            <button
              onClick={() => setActiveTab('assignments')}
              className={`pb-4 px-2 font-semibold transition-colors border-b-2 ${
                activeTab === 'assignments'
                  ? 'border-purple-600 text-purple-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900'
              }`}
            >
              Assignments ({assignments.length})
            </button>
            {isInstructor && (
              <button
                onClick={() => setActiveTab('students')}
                className={`pb-4 px-2 font-semibold transition-colors border-b-2 ${
                  activeTab === 'students'
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                Students ({students.length})
              </button>
            )}
          </div>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content Area */}
          <div className="lg:col-span-2">
            {/* Assignments Tab */}
            {activeTab === 'assignments' && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Assignments</h2>
                  {isInstructor && (
                    <Link
                      to={`/assignments/create?courseId=${courseId}`}
                      className="btn-primary"
                    >
                      + Create Assignment
                    </Link>
                  )}
                </div>

                {assignments.length === 0 ? (
                  <Card className="text-center py-12">
                    <p className="text-gray-500 mb-4">No assignments yet</p>
                    {isInstructor && (
                      <Link
                        to={`/assignments/create?courseId=${courseId}`}
                        className="btn-primary"
                      >
                        Create First Assignment
                      </Link>
                    )}
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {assignments.map((assignment) => (
                      <Card key={assignment.assignment_id} hover>
                        <Link to={`/assignments/${assignment.assignment_id}`}>
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h3 className="text-xl font-bold text-gray-900 mb-2">
                                {assignment.title}
                              </h3>
                              <p className="text-gray-600 mb-3 line-clamp-2">
                                {assignment.description}
                              </p>
                              <div className="flex items-center gap-6 text-sm text-gray-500">
                                <span className="flex items-center gap-1">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                  </svg>
                                  Due: {new Date(assignment.due_date).toLocaleDateString()}
                                </span>
                                <span className="flex items-center gap-1">
                                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                                  </svg>
                                  {assignment.submission_count || 0} submissions
                                </span>
                              </div>
                            </div>
                            <div className="ml-4">
                              <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                                new Date(assignment.due_date) > new Date()
                                  ? 'bg-green-100 text-green-700'
                                  : 'bg-red-100 text-red-700'
                              }`}>
                                {new Date(assignment.due_date) > new Date() ? 'Open' : 'Closed'}
                              </span>
                            </div>
                          </div>
                        </Link>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Students Tab */}
            {activeTab === 'students' && isInstructor && (
              <div>
                <div className="flex justify-between items-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900">Enrolled Students</h2>
                </div>

                {students.length === 0 ? (
                  <Card className="text-center py-12">
                    <p className="text-gray-500">No students enrolled yet</p>
                    <p className="text-sm text-gray-400 mt-2">Share your join code with students</p>
                  </Card>
                ) : (
                  <Card>
                    <div className="overflow-x-auto">
                      <table className="w-full">
                        <thead>
                          <tr className="border-b">
                            <th className="text-left py-3 px-4 font-semibold text-gray-900">Name</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-900">Email</th>
                            <th className="text-left py-3 px-4 font-semibold text-gray-900">Enrolled</th>
                            <th className="text-right py-3 px-4 font-semibold text-gray-900">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          {students.map((student) => (
                            <tr key={student.user_id} className="border-b last:border-0 hover:bg-gray-50">
                              <td className="py-3 px-4">
                                {student.first_name} {student.last_name}
                              </td>
                              <td className="py-3 px-4 text-gray-600">{student.email}</td>
                              <td className="py-3 px-4 text-gray-600">
                                {new Date(student.enrolled_at).toLocaleDateString()}
                              </td>
                              <td className="py-3 px-4 text-right">
                                <button className="text-purple-600 hover:text-purple-700 text-sm font-semibold">
                                  View Profile
                                </button>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </Card>
                )}
              </div>
            )}
          </div>

          {/* ⭐⭐⭐ SIDEBAR - ADD JOIN CODE CARD HERE ⭐⭐⭐ */}
          <div className="space-y-6">
            {/* JOIN CODE CARD (Instructor Only) */}
            {isInstructor && (
              <Card>
                <h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
                  </svg>
                  Course Join Code
                </h3>
                
                <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6 text-center">
                  <p className="text-sm text-gray-600 mb-3">Share this code with students</p>
                  
                  {/* Join Code Display */}
                  <div className="font-mono text-4xl font-bold text-purple-600 mb-4 tracking-wider select-all">
                    {course.join_code || 'LOADING...'}
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex gap-2">
                    <button
                      onClick={handleCopyCode}
                      className="flex-1 bg-white hover:bg-gray-50 text-purple-600 font-semibold py-2 px-4 rounded-lg border-2 border-purple-600 transition-colors"
                    >
                      📋 Copy Code
                    </button>
                    <button
                      onClick={handleRegenerateCode}
                      disabled={regenerating}
                      className="flex-1 bg-purple-600 hover:bg-purple-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors disabled:bg-gray-400"
                    >
                      {regenerating ? '⏳' : '🔄'} Regenerate
                    </button>
                  </div>
                </div>
                
                {/* Instructions */}
                <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-xs text-blue-800">
                    💡 <strong>How it works:</strong> Students enter this code on the "Join Course" page to enroll in your class.
                  </p>
                </div>
              </Card>
            )}

            {/* Other sidebar cards... */}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;