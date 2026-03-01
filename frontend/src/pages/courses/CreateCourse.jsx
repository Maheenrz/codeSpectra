import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import courseService from '../../services/courseService';
import Card from '../../components/common/Card';

const CreateCourse = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    courseCode: '',
    courseName: '',
    semester: 'Fall',
    year: new Date().getFullYear(),
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const course = await courseService.createCourse(formData);
      navigate(`/courses/${course.course.course_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create course');
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
          <h1 className="text-3xl font-bold text-gray-900">Create New Course</h1>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        <Card>
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Course Code *
                </label>
                <input
                  type="text"
                  name="courseCode"
                  required
                  value={formData.courseCode}
                  onChange={handleChange}
                  placeholder="e.g., CS101"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Course Name *
                </label>
                <input
                  type="text"
                  name="courseName"
                  required
                  value={formData.courseName}
                  onChange={handleChange}
                  placeholder="e.g., Introduction to Programming"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Semester *
                </label>
                <select
                  name="semester"
                  value={formData.semester}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                >
                  <option value="Spring">Spring</option>
                  <option value="Summer">Summer</option>
                  <option value="Fall">Fall</option>
                  <option value="Winter">Winter</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Year *
                </label>
                <input
                  type="number"
                  name="year"
                  required
                  min="2020"
                  max="2030"
                  value={formData.year}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>
            </div>

            <div className="flex justify-end gap-4 pt-6 border-t">
              <Link to="/courses" className="btn-secondary">
                Cancel
              </Link>
              <button
                type="submit"
                disabled={loading}
                className="btn-primary disabled:bg-gray-400"
              >
                {loading ? 'Creating...' : 'Create Course'}
              </button>
            </div>
          </form>
        </Card>
      </div>
    </div>
  );
};

export default CreateCourse;