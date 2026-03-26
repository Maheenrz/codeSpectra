import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';

const inputClass = `w-full px-4 py-3 rounded-xl border border-[#E8E1D8] bg-[#F7F3EE]
  text-sm text-[#1A1714] placeholder-[#A8A29E]
  focus:outline-none focus:ring-2 focus:ring-[#CF7249] focus:border-transparent transition-all`;

const JoinCourse = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [joinCode, setJoinCode]         = useState('');
  const [coursePreview, setCoursePreview] = useState(null);
  const [loading, setLoading]           = useState(false);
  const [error, setError]               = useState('');
  const [success, setSuccess]           = useState('');

  const handlePreview = async () => {
    if (!joinCode.trim()) { setError('Please enter a join code'); return; }
    setError(''); setLoading(true);
    try {
      const course = await courseService.getCourseByJoinCode(joinCode.trim());
      setCoursePreview(course);
    } catch {
      setError('Invalid join code. Please check and try again.');
      setCoursePreview(null);
    } finally { setLoading(false); }
  };

  const handleJoin = async () => {
    setError(''); setLoading(true);
    try {
      const result = await courseService.enrollWithJoinCode(joinCode.trim());
      setSuccess('Successfully enrolled!');
      setTimeout(() => navigate(`/courses/${result.courseId}`), 1500);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to join course');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      <main className="max-w-xl mx-auto px-6 pt-20 pb-12">
        <Link to="/courses" className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-6 transition-colors">
          ← Back to Courses
        </Link>

        <div className="mb-8">
          <p className="text-xs font-semibold tracking-[0.2em] uppercase text-[#2D6A6A] mb-1">Student</p>
          <h1 className="text-3xl font-bold text-[#1A1714]">Join a Course</h1>
          <p className="text-sm text-[#6B6560] mt-1">Enter the join code from your instructor.</p>
        </div>

        {error   && <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">{error}</div>}
        {success && <div className="mb-4 px-4 py-3 rounded-xl bg-emerald-50 border border-emerald-200 text-sm text-emerald-700">{success}</div>}

        <div className="bg-white rounded-2xl border border-[#E8E1D8] p-8 space-y-6">
          <div>
            <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">Course Join Code</label>
            <div className="flex gap-3">
              <input type="text" value={joinCode}
                onChange={e => setJoinCode(e.target.value.toUpperCase())}
                onKeyDown={e => e.key === 'Enter' && handlePreview()}
                placeholder="e.g. ABC123XY" maxLength={10}
                className={inputClass + ' font-mono text-lg tracking-widest flex-1'} />
              <button onClick={handlePreview} disabled={loading || !joinCode.trim()}
                className="btn-ghost disabled:opacity-50 flex-shrink-0">
                {loading ? 'Checking…' : 'Preview'}
              </button>
            </div>
            <p className="text-xs text-[#A8A29E] mt-2">Ask your instructor for the course join code.</p>
          </div>

          {coursePreview && (
            <div className="border-t border-[#F0EBE3] pt-6">
              <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Course Preview</p>
              <div className="bg-[#F7F3EE] rounded-xl p-5 mb-5">
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#FEF3EC] text-[#CF7249]">
                    {coursePreview.course_code}
                  </span>
                  <span className="text-xs text-[#A8A29E]">{coursePreview.semester} {coursePreview.year}</span>
                </div>
                <h3 className="font-bold text-[#1A1714] text-lg mb-1">{coursePreview.course_name}</h3>
                <p className="text-sm text-[#6B6560]">Instructor: {coursePreview.instructor_name}</p>
                <div className="flex gap-5 mt-3 text-sm text-[#6B6560]">
                  <span><strong className="text-[#1A1714]">{coursePreview.student_count || 0}</strong> students</span>
                </div>
              </div>
              <div className="flex gap-3">
                <button onClick={() => { setCoursePreview(null); setJoinCode(''); }}
                  className="btn-ghost flex-1 justify-center">
                  Cancel
                </button>
                <button onClick={handleJoin} disabled={loading}
                  className="btn-teal flex-1 justify-center disabled:opacity-50">
                  {loading ? 'Joining…' : 'Join This Course'}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Steps */}
        <div className="bg-white rounded-2xl border border-[#E8E1D8] p-6 mt-4">
          <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">How it works</p>
          <ol className="space-y-3">
            {[
              'Get the join code from your instructor',
              'Enter the code above and click Preview',
              'Verify the course details and click Join',
              'You\'ll be redirected to the course page',
            ].map((step, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-[#6B6560]">
                <span className="w-5 h-5 rounded-full bg-[#EBF4F4] text-[#2D6A6A] text-[10px] font-bold flex items-center justify-center flex-shrink-0 mt-0.5">
                  {i + 1}
                </span>
                {step}
              </li>
            ))}
          </ol>
        </div>
      </main>
    </div>
  );
};

export default JoinCourse;
