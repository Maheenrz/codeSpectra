import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import Card from '../../components/common/Card';

const JoinCourse = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [joinCode, setJoinCode] = useState('');
  const [coursePreview, setCoursePreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handlePreview = async () => {
    if (!joinCode.trim()) {
      setError('Please enter a join code');
      return;
    }

    setError('');
    setLoading(true);

    try {
      const course = await courseService.getCourseByJoinCode(joinCode.trim());
      setCoursePreview(course);
    } catch (err) {
      setError('Invalid join code. Please check and try again.');
      setCoursePreview(null);
    } finally {
      setLoading(false);
    }
  };

  const handleJoin = async () => {
    setError('');
    setLoading(true);

    try {
      const result = await courseService.enrollWithJoinCode(joinCode.trim());
      setSuccess('Successfully enrolled in course!');
      
      setTimeout(() => {
        navigate(`/courses/${result.courseId}`);
      }, 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to join course');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <Link to="/courses" className="text-purple-600 hover:text-purple-700 mb-4 inline-block">
            ← Back to Courses
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Join a Course</h1>
          <p className="text-gray-600 mt-2">Enter the join code provided by your instructor</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 text-green-700 rounded-lg">
            {success}
          </div>
        )}

        <Card>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                Course Join Code
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={joinCode}
                  onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
                  placeholder="e.g., ABC123XY"
                  maxLength="10"
                  className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent uppercase font-mono text-lg"
                  onKeyPress={(e) => e.key === 'Enter' && handlePreview()}
                />
                <button
                  onClick={handlePreview}
                  disabled={loading || !joinCode.trim()}
                  className="btn-secondary disabled:bg-gray-400"
                >
                  {loading ? 'Checking...' : 'Preview'}
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-2">
                Ask your instructor for the course join code
              </p>
            </div>

            {coursePreview && (
              <div className="border-t pt-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Course Preview</h3>
                <div className="bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg p-6">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h4 className="text-2xl font-bold text-gray-900 mb-2">
                        {coursePreview.course_code}
                      </h4>
                      <p className="text-lg text-gray-700 mb-2">{coursePreview.course_name}</p>
                      <p className="text-gray-600">
                        Instructor: {coursePreview.instructor_name}
                      </p>
                    </div>
                    <span className="px-4 py-2 bg-purple-600 text-white rounded-lg font-semibold">
                      {coursePreview.semester} {coursePreview.year}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-purple-200">
                    <div>
                      <p className="text-sm text-gray-600">Students Enrolled</p>
                      <p className="text-2xl font-bold text-purple-600">
                        {coursePreview.student_count || 0}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Join Code</p>
                      <p className="text-2xl font-bold text-purple-600 font-mono">
                        {coursePreview.join_code}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end gap-3 mt-6">
                  <button
                    onClick={() => {
                      setCoursePreview(null);
                      setJoinCode('');
                    }}
                    className="btn-secondary"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleJoin}
                    disabled={loading}
                    className="btn-primary disabled:bg-gray-400"
                  >
                    {loading ? 'Joining...' : 'Join This Course'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Instructions */}
        <Card className="mt-6">
          <h3 className="font-bold text-gray-900 mb-3">How to join a course</h3>
          <ol className="space-y-2 text-gray-700">
            <li className="flex gap-3">
              <span className="font-bold text-purple-600">1.</span>
              <span>Get the join code from your instructor (email, LMS, or in class)</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-purple-600">2.</span>
              <span>Enter the code above and click "Preview"</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-purple-600">3.</span>
              <span>Verify the course details and click "Join This Course"</span>
            </li>
            <li className="flex gap-3">
              <span className="font-bold text-purple-600">4.</span>
              <span>You'll be redirected to the course page</span>
            </li>
          </ol>
        </Card>
      </div>
    </div>
  );
};

export default JoinCourse;