import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';

const inputClass = `w-full px-4 py-3 rounded-xl border border-[#E8E1D8] bg-[#F7F3EE]
  text-sm text-[#1A1714] placeholder-[#A8A29E]
  focus:outline-none focus:ring-2 focus:ring-[#CF7249] focus:border-transparent transition-all`;

const CreateCourse = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [formData, setFormData] = useState({
    courseCode: '', courseName: '',
    semester: 'Fall', year: new Date().getFullYear(),
  });
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const handleChange = e => setFormData(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      const course = await courseService.createCourse(formData);
      navigate(`/courses/${course.course.course_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create course');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      <main className="max-w-2xl mx-auto px-6 pt-20 pb-12">
        <Link to="/courses" className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-6 transition-colors">
          ← Back to Courses
        </Link>

        <div className="mb-8">
          <p className="text-xs font-semibold tracking-[0.2em] uppercase text-[#CF7249] mb-1">Instructor</p>
          <h1 className="text-3xl font-bold text-[#1A1714]">Create a Course</h1>
          <p className="text-sm text-[#6B6560] mt-1">A join code will be generated automatically for students.</p>
        </div>

        <div className="bg-white rounded-2xl border border-[#E8E1D8] p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">{error}</div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">Course Code *</label>
                <input type="text" name="courseCode" required value={formData.courseCode}
                  onChange={handleChange} placeholder="e.g. CS301" className={inputClass} />
              </div>
              <div>
                <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">Year *</label>
                <input type="number" name="year" required min="2020" max="2030"
                  value={formData.year} onChange={handleChange} className={inputClass} />
              </div>
            </div>

            <div>
              <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">Course Name *</label>
              <input type="text" name="courseName" required value={formData.courseName}
                onChange={handleChange} placeholder="e.g. Data Structures & Algorithms" className={inputClass} />
            </div>

            <div>
              <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">Semester *</label>
              <select name="semester" value={formData.semester} onChange={handleChange}
                className={inputClass + ' cursor-pointer appearance-none'}>
                {['Spring', 'Summer', 'Fall', 'Winter'].map(s => <option key={s}>{s}</option>)}
              </select>
            </div>

            <div className="flex gap-3 pt-2">
              <Link to="/courses" className="btn-ghost flex-1 justify-center">Cancel</Link>
              <button type="submit" disabled={loading}
                className="btn-orange flex-1 justify-center disabled:opacity-50">
                {loading ? 'Creating…' : 'Create Course'}
              </button>
            </div>
          </form>
        </div>
      </main>
    </div>
  );
};

export default CreateCourse;
