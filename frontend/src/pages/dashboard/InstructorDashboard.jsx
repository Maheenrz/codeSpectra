import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Card from '../../components/common/Card';

const InstructorDashboard = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalStudents: 0,
    totalAssignments: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const coursesData = await courseService.getInstructorCourses();
      setCourses(coursesData);
      
      // Calculate stats
      const totalStudents = coursesData.reduce((sum, c) => sum + (parseInt(c.student_count) || 0), 0);
      const totalAssignments = coursesData.reduce((sum, c) => sum + (parseInt(c.assignment_count) || 0), 0);
      
      setStats({
        totalCourses: coursesData.length,
        totalStudents,
        totalAssignments,
      });
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
                Welcome, Professor {user?.lastName}
              </h1>
              <p className="text-gray-600 mt-1">Instructor Dashboard</p>
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
                <p className="text-gray-600 text-sm">Total Courses</p>
                <p className="text-3xl font-bold text-purple-600">{stats.totalCourses}</p>
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
                <p className="text-gray-600 text-sm">Total Students</p>
                <p className="text-3xl font-bold text-purple-600">{stats.totalStudents}</p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm">Total Assignments</p>
                <p className="text-3xl font-bold text-purple-600">{stats.totalAssignments}</p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
            </div>
          </Card>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid md:grid-cols-3 gap-4">
            <Link to="/courses/create">
              <Card hover className="text-center cursor-pointer">
                <div className="w-16 h-16 bg-purple-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
                <h3 className="font-bold text-lg">Create Course</h3>
                <p className="text-gray-600 text-sm mt-2">Start a new course</p>
              </Card>
            </Link>

            <Link to="/assignments/create">
              <Card hover className="text-center cursor-pointer">
                <div className="w-16 h-16 bg-blue-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <h3 className="font-bold text-lg">New Assignment</h3>
                <p className="text-gray-600 text-sm mt-2">Create an assignment</p>
              </Card>
            </Link>

            <Link to="/analysis">
              <Card hover className="text-center cursor-pointer">
                <div className="w-16 h-16 bg-green-600 rounded-lg mx-auto mb-4 flex items-center justify-center">
                  <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <h3 className="font-bold text-lg">View Analytics</h3>
                <p className="text-gray-600 text-sm mt-2">Check plagiarism reports</p>
              </Card>
            </Link>
          </div>
        </div>

        {/* Courses List */}
        <div>
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">My Courses</h2>
            <Link to="/courses/create" className="btn-primary">
              + Create Course
            </Link>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {courses.length === 0 ? (
              <Card className="col-span-2">
                <p className="text-gray-500 text-center py-8">No courses created yet</p>
              </Card>
            ) : (
              courses.map((course) => (
                <Card key={course.course_id} hover>
                  <Link to={`/courses/${course.course_id}`}>
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-xl text-gray-900">
                          {course.course_code}
                        </h3>
                        <p className="text-gray-600">{course.course_name}</p>
                      </div>
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm font-semibold">
                        {course.semester} {course.year}
                      </span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                      <div>
                        <p className="text-gray-500 text-sm">Students</p>
                        <p className="text-2xl font-bold text-purple-600">{course.student_count || 0}</p>
                      </div>
                      <div>
                        <p className="text-gray-500 text-sm">Assignments</p>
                        <p className="text-2xl font-bold text-purple-600">{course.assignment_count || 0}</p>
                      </div>
                    </div>
                  </Link>
                </Card>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default InstructorDashboard;