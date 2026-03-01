import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import submissionService from '../../services/submissionService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Card from '../../components/common/Card';

const StudentDashboard = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [coursesData, submissionsData] = await Promise.all([
        courseService.getStudentCourses(),
        submissionService.getStudentSubmissions(),
      ]);
      setCourses(coursesData);
      setSubmissions(submissionsData.slice(0, 5)); // Latest 5
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading dashboard..." />;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user?.firstName}!
              </h1>
              <p className="text-gray-600 mt-1">Student Dashboard</p>
            </div>
            <Link to="/" className="font-pixelify text-2xl text-purple-600">
              CodeSpectra
            </Link>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Enrolled Courses</p>
                <p className="text-3xl font-bold text-purple-600">{courses.length}</p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Submissions</p>
                <p className="text-3xl font-bold text-purple-600">{submissions.length}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Pending Analysis</p>
                <p className="text-3xl font-bold text-purple-600">
                  {submissions.filter(s => s.analysis_status === 'pending').length}
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
          </Card>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* My Courses */}
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">My Courses</h2>
              <Link to="/courses" className="text-purple-600 hover:text-purple-700 font-semibold">
                View All →
              </Link>
            </div>

            <div className="space-y-4">
              {courses.length === 0 ? (
                <Card>
                  <p className="text-gray-500 text-center py-8">No courses enrolled yet</p>
                </Card>
              ) : (
                courses.map((course) => (
                  <Card key={course.course_id} hover>
                    <Link to={`/courses/${course.course_id}`}>
                      <h3 className="font-bold text-lg text-gray-900 mb-2">
                        {course.course_code} - {course.course_name}
                      </h3>
                      <p className="text-gray-600 text-sm mb-3">
                        {course.instructor_name} • {course.semester} {course.year}
                      </p>
                      <div className="flex gap-4 text-sm text-gray-500">
                        <span>{course.assignment_count || 0} assignments</span>
                      </div>
                    </Link>
                  </Card>
                ))
              )}
            </div>
          </div>

          {/* Recent Submissions */}
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-900">Recent Submissions</h2>
              <Link to="/submissions" className="text-purple-600 hover:text-purple-700 font-semibold">
                View All →
              </Link>
            </div>

            <div className="space-y-4">
              {submissions.length === 0 ? (
                <Card>
                  <p className="text-gray-500 text-center py-8">No submissions yet</p>
                </Card>
              ) : (
                submissions.map((submission) => (
                  <Card key={submission.submission_id} hover>
                    <Link to={`/submissions/${submission.submission_id}`}>
                      <div className="flex justify-between items-start mb-2">
                        <h3 className="font-bold text-gray-900">{submission.assignment_title}</h3>
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                          submission.analysis_status === 'completed' ? 'bg-green-100 text-green-700' :
                          submission.analysis_status === 'processing' ? 'bg-blue-100 text-blue-700' :
                          submission.analysis_status === 'failed' ? 'bg-red-100 text-red-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {submission.analysis_status}
                        </span>
                      </div>
                      <p className="text-gray-600 text-sm mb-2">{submission.course_name}</p>
                      <p className="text-gray-500 text-xs">
                        Submitted {new Date(submission.submitted_at).toLocaleDateString()}
                      </p>
                    </Link>
                  </Card>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentDashboard;