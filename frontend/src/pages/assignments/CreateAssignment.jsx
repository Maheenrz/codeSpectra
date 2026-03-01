import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import courseService from '../../services/courseService';
import assignmentService from '../../services/assignmentService';
import Card from '../../components/common/Card';

const CreateAssignment = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const preselectedCourseId = searchParams.get('courseId');

  const [courses, setCourses] = useState([]);
  const [formData, setFormData] = useState({
    courseId: preselectedCourseId || '',
    title: '',
    description: '',
    dueDate: '',
    primaryLanguage: 'cpp',
    allowedExtensions: '.cpp,.c,.h',
    maxFileSizeMb: 5,
    enableType1: true,
    enableType2: true,
    enableType3: true,
    enableType4: true,
    highSimilarityThreshold: 85,
    mediumSimilarityThreshold: 70,
    analysisMode: 'after_deadline',
    showResultsToStudents: false,
    generateFeedback: true,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const data = await courseService.getInstructorCourses();
      setCourses(data);
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const assignment = await assignmentService.createAssignment(formData);
      navigate(`/courses/${formData.courseId}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create assignment');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-5xl mx-auto px-6 py-6">
          <Link to="/dashboard" className="text-purple-600 hover:text-purple-700 mb-4 inline-block">
            ← Back to Dashboard
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Create New Assignment</h1>
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
              {error}
            </div>
          )}

          {/* Basic Information */}
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-6">Basic Information</h2>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Course *
                </label>
                <select
                  name="courseId"
                  required
                  value={formData.courseId}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                >
                  <option value="">Select a course</option>
                  {courses.map((course) => (
                    <option key={course.course_id} value={course.course_id}>
                      {course.course_code} - {course.course_name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Assignment Title *
                </label>
                <input
                  type="text"
                  name="title"
                  required
                  value={formData.title}
                  onChange={handleChange}
                  placeholder="e.g., Project 1: Binary Search Tree Implementation"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Description *
                </label>
                <textarea
                  name="description"
                  required
                  value={formData.description}
                  onChange={handleChange}
                  rows="4"
                  placeholder="Describe the assignment requirements..."
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Due Date *
                </label>
                <input
                  type="datetime-local"
                  name="dueDate"
                  required
                  value={formData.dueDate}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>
            </div>
          </Card>

          {/* File Settings */}
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-6">File Submission Settings</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Primary Language
                </label>
                <select
                  name="primaryLanguage"
                  value={formData.primaryLanguage}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                >
                  <option value="cpp">C++</option>
                  <option value="c">C</option>
                  <option value="java">Java</option>
                  <option value="python">Python</option>
                  <option value="javascript">JavaScript</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Max File Size (MB)
                </label>
                <input
                  type="number"
                  name="maxFileSizeMb"
                  min="1"
                  max="50"
                  value={formData.maxFileSizeMb}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
              </div>

              <div className="md:col-span-2">
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Allowed File Extensions
                </label>
                <input
                  type="text"
                  name="allowedExtensions"
                  value={formData.allowedExtensions}
                  onChange={handleChange}
                  placeholder=".cpp,.c,.h"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                />
                <p className="text-sm text-gray-500 mt-2">Comma-separated list of extensions</p>
              </div>
            </div>
          </Card>

          {/* Detection Settings */}
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-6">Plagiarism Detection Settings</h2>
            
            <div className="space-y-6">
              <div>
                <p className="text-sm font-semibold text-gray-700 mb-3">Enable Detection Types</p>
                <div className="space-y-3">
                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      name="enableType1"
                      checked={formData.enableType1}
                      onChange={handleChange}
                      className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-600"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Type-1 Detection</span>
                      <p className="text-sm text-gray-600">Exact copies with whitespace changes</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      name="enableType2"
                      checked={formData.enableType2}
                      onChange={handleChange}
                      className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-600"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Type-2 Detection</span>
                      <p className="text-sm text-gray-600">Renamed variables and literals</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      name="enableType3"
                      checked={formData.enableType3}
                      onChange={handleChange}
                      className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-600"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Type-3 Detection</span>
                      <p className="text-sm text-gray-600">Modified statements and structure</p>
                    </div>
                  </label>

                  <label className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      name="enableType4"
                      checked={formData.enableType4}
                      onChange={handleChange}
                      className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-600"
                    />
                    <div>
                      <span className="font-medium text-gray-900">Type-4 Detection (AI)</span>
                      <p className="text-sm text-gray-600">Semantic similarity detection</p>
                    </div>
                  </label>
                </div>
              </div>

              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    High Similarity Threshold (%)
                  </label>
                  <input
                    type="number"
                    name="highSimilarityThreshold"
                    min="50"
                    max="100"
                    value={formData.highSimilarityThreshold}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Medium Similarity Threshold (%)
                  </label>
                  <input
                    type="number"
                    name="mediumSimilarityThreshold"
                    min="30"
                    max="100"
                    value={formData.mediumSimilarityThreshold}
                    onChange={handleChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">
                  Analysis Mode
                </label>
                <select
                  name="analysisMode"
                  value={formData.analysisMode}
                  onChange={handleChange}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-600 focus:border-transparent"
                >
                  <option value="immediate">Immediate (Analyze on submission)</option>
                  <option value="after_deadline">After Deadline</option>
                  <option value="manual">Manual (Instructor triggers)</option>
                </select>
              </div>

              <div className="space-y-3">
                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    name="showResultsToStudents"
                    checked={formData.showResultsToStudents}
                    onChange={handleChange}
                    className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-600"
                  />
                  <span className="font-medium text-gray-900">Show results to students</span>
                </label>

                <label className="flex items-center gap-3">
                  <input
                    type="checkbox"
                    name="generateFeedback"
                    checked={formData.generateFeedback}
                    onChange={handleChange}
                    className="w-5 h-5 text-purple-600 rounded focus:ring-2 focus:ring-purple-600"
                  />
                  <span className="font-medium text-gray-900">Generate feedback reports</span>
                </label>
              </div>
            </div>
          </Card>

          {/* Submit Buttons */}
          <div className="flex justify-end gap-4">
            <Link to="/dashboard" className="btn-secondary">
              Cancel
            </Link>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary disabled:bg-gray-400"
            >
              {loading ? 'Creating Assignment...' : 'Create Assignment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateAssignment;