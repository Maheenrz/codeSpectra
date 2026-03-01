import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import courseService from "../../services/courseService";
import LoadingSpinner from "../../components/common/LoadingSpinner";
import Card from "../../components/common/Card";

const CourseList = () => {
  const { user, isInstructor } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const data = isInstructor
        ? await courseService.getInstructorCourses()
        : await courseService.getStudentCourses();
      setCourses(data);
    } catch (error) {
      console.error("Error fetching courses:", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading courses..." />;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Courses</h1>
              <p className="text-gray-600 mt-1">
                {isInstructor ? "Manage your courses" : "Your enrolled courses"}
              </p>
            </div>
            
            <div className="flex gap-3">
              <Link to="/dashboard" className="btn-secondary">
                ← Dashboard
              </Link>
              {isInstructor ? (
                <Link to="/courses/create" className="btn-primary">
                  + Create Course
                </Link>
              ) : (
                <Link to="/courses/join" className="btn-primary">
                  + Join Course
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {courses.length === 0 ? (
          <Card className="text-center py-12">
            <svg
              className="w-16 h-16 text-gray-400 mx-auto mb-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
              />
            </svg>
            <h3 className="text-xl font-bold text-gray-900 mb-2">
              No courses yet
            </h3>
            <p className="text-gray-600 mb-6">
              {isInstructor
                ? "Create your first course to get started"
                : "You are not enrolled in any courses yet"}
            </p>
            {isInstructor ? (
              <Link to="/courses/create" className="btn-primary">
                Create Your First Course
              </Link>
            ) : (
              <Link to="/courses/join" className="btn-primary">
                Join a Course
              </Link>
            )}
          </Card>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {courses.map((course) => (
              <Card key={course.course_id} hover className="flex flex-col">
                <Link to={`/courses/${course.course_id}`} className="flex-1">
                  <div className="mb-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-bold text-gray-900">
                        {course.course_code}
                      </h3>
                      <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                        {course.semester} {course.year}
                      </span>
                    </div>
                    <p className="text-gray-700 font-medium mb-2">
                      {course.course_name}
                    </p>
                    <p className="text-gray-600 text-sm">
                      {isInstructor ? "Instructor" : course.instructor_name}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div>
                      <p className="text-gray-500 text-xs">Students</p>
                      <p className="text-xl font-bold text-purple-600">
                        {course.student_count || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-500 text-xs">Assignments</p>
                      <p className="text-xl font-bold text-purple-600">
                        {course.assignment_count || 0}
                      </p>
                    </div>
                  </div>
                </Link>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CourseList;