import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import submissionService from '../../services/submissionService';
import PageLoader from '../../Components/common/PageLoader';

const IconLogOut = () => (<svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>);

const STATUS_STYLE = {
  completed:  { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500', label: 'Done' },
  processing: { bg: 'bg-blue-50',    text: 'text-blue-700',    dot: 'bg-blue-500',    label: 'Analyzing' },
  failed:     { bg: 'bg-red-50',     text: 'text-red-600',     dot: 'bg-red-500',     label: 'Failed' },
  pending:    { bg: 'bg-[#F7F3EE]',  text: 'text-[#6B6560]',  dot: 'bg-[#A8A29E]',  label: 'Pending' },
};

const StudentDashboard = () => {
  const { user, logout } = useAuth();
  const [courses, setCourses] = useState([]);
  const [submissions, setSubmissions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const [c, s] = await Promise.all([
        courseService.getStudentCourses(),
        submissionService.getStudentSubmissions(),
      ]);
      setCourses(c);
      setSubmissions(s);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  if (loading) return <PageLoader message="Loading your courses…" />;

  const pending = submissions.filter(s => s.analysis_status === 'pending' || s.analysis_status === 'processing').length;

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      <main className="max-w-6xl mx-auto px-6 pt-20 pb-12">
        <div className="mb-10">
          <p className="text-xs font-semibold tracking-[0.2em] uppercase text-[#2D6A6A] mb-1">Student Dashboard</p>
          <h1 className="text-3xl font-bold text-[#1A1714]">Welcome, {user?.firstName}</h1>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-5 mb-10">
          {[
            { label: 'Courses',     value: courses.length,     accent: '#CF7249', bg: '#FEF3EC' },
            { label: 'Submissions', value: submissions.length, accent: '#2D6A6A', bg: '#EBF4F4' },
            { label: 'Processing',  value: pending,            accent: '#C4827A', bg: '#FAEDEC' },
          ].map(({ label, value, accent, bg }) => (
            <div key={label} className="bg-white rounded-2xl border border-[#E8E1D8] p-6">
              <p className="text-sm text-[#6B6560] mb-2">{label}</p>
              <p className="text-4xl font-bold" style={{ color: accent }}>{value}</p>
            </div>
          ))}
        </div>

        {/* Quick actions */}
        <div className="grid grid-cols-2 gap-4 mb-10">
          <Link to="/courses" className="bg-white rounded-2xl border border-[#E8E1D8] p-5 hover:shadow-md hover:border-transparent transition-all">
            <p className="text-xs font-bold uppercase tracking-widest text-[#CF7249] mb-1">My Courses</p>
            <p className="text-sm text-[#6B6560]">View all enrolled courses</p>
          </Link>
          <Link to="/courses/join" className="bg-white rounded-2xl border border-[#E8E1D8] p-5 hover:shadow-md hover:border-transparent transition-all">
            <p className="text-xs font-bold uppercase tracking-widest text-[#2D6A6A] mb-1">Join Course</p>
            <p className="text-sm text-[#6B6560]">Enter a course join code</p>
          </Link>
        </div>

        {/* Recent submissions */}
        <h2 className="text-lg font-bold text-[#1A1714] mb-4">Recent Submissions</h2>
        {submissions.length === 0 ? (
          <div className="bg-white rounded-2xl border border-[#E8E1D8] p-12 text-center">
            <p className="text-[#6B6560]">No submissions yet.</p>
          </div>
        ) : (
          <div className="bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden">
            {submissions.slice(0, 8).map((sub, i) => {
              const S = STATUS_STYLE[sub.analysis_status] || STATUS_STYLE.pending;
              return (
                <Link key={sub.submission_id} to={`/submissions/${sub.submission_id}`}
                  className={`flex items-center justify-between px-6 py-4 hover:bg-[#F7F3EE] transition-colors ${i !== 0 ? 'border-t border-[#F0EBE3]' : ''}`}>
                  <div>
                    <p className="text-sm font-semibold text-[#1A1714]">{sub.assignment_title}</p>
                    <p className="text-xs text-[#A8A29E] mt-0.5">{sub.course_code} · {new Date(sub.submitted_at).toLocaleDateString()}</p>
                  </div>
                  <span className={`inline-flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full ${S.bg} ${S.text}`}>
                    <span className={`w-1.5 h-1.5 rounded-full ${S.dot}`} />
                    {S.label}
                  </span>
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
};

export default StudentDashboard;
