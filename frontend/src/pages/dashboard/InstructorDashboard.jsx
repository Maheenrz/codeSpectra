import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import PageLoader from '../../Components/common/PageLoader';

const StatCard = ({ label, value, accent, bg, icon }) => (
  <div className="bg-white rounded-2xl border border-[#E8E1D8] p-6">
    <div className="flex items-center justify-between mb-4">
      <p className="text-sm text-[#6B6560] font-medium">{label}</p>
      <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: bg, color: accent }}>
        {icon}
      </div>
    </div>
    <p className="text-4xl font-bold" style={{ color: accent }}>{value}</p>
  </div>
);

const InstructorDashboard = () => {
  const { user } = useAuth();
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState({ totalCourses: 0, totalStudents: 0, totalAssignments: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      const data = await courseService.getInstructorCourses();
      setCourses(data);
      setStats({
        totalCourses: data.length,
        totalStudents: data.reduce((s, c) => s + (parseInt(c.student_count) || 0), 0),
        totalAssignments: data.reduce((s, c) => s + (parseInt(c.assignment_count) || 0), 0),
      });
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  if (loading) return <PageLoader message="Loading dashboard…" />;

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      <main className="max-w-6xl mx-auto px-6 pt-20 pb-12">
        <div className="mb-10">
          <p className="text-xs font-semibold tracking-[0.2em] uppercase text-[#CF7249] mb-1">Instructor Dashboard</p>
          <h1 className="text-3xl font-bold text-[#1A1714]">Welcome back, {user?.firstName}</h1>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-5 mb-10">
          <StatCard label="Total Courses" value={stats.totalCourses} accent="#CF7249" bg="#FEF3EC"
            icon={<svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/></svg>} />
          <StatCard label="Total Students" value={stats.totalStudents} accent="#2D6A6A" bg="#EBF4F4"
            icon={<svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75"/></svg>} />
          <StatCard label="Assignments" value={stats.totalAssignments} accent="#8B9BB4" bg="#EFF2F7"
            icon={<svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="2"/></svg>} />
        </div>

        {/* Quick actions */}
        <div className="mb-10">
          <h2 className="text-lg font-bold text-[#1A1714] mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { to: '/courses/create',    label: 'Create Course',     accent: '#CF7249', bg: '#FEF3EC' },
              { to: '/assignments/create',label: 'New Assignment',    accent: '#2D6A6A', bg: '#EBF4F4' },
              { to: '/courses',           label: 'My Courses',        accent: '#C4827A', bg: '#FAEDEC' },
              { to: '/analyze',           label: 'Analysis Tool',     accent: '#8B9BB4', bg: '#EFF2F7' },
            ].map(({ to, label, accent, bg }) => (
              <Link key={to} to={to}
                className="bg-white rounded-2xl border border-[#E8E1D8] p-5 text-center hover:shadow-md hover:border-transparent transition-all">
                <div className="w-10 h-10 rounded-xl mx-auto mb-3 flex items-center justify-center text-base font-bold"
                  style={{ background: bg, color: accent }}>
                  →
                </div>
                <p className="text-sm font-semibold text-[#1A1714]">{label}</p>
              </Link>
            ))}
          </div>
        </div>

        {/* Courses */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-bold text-[#1A1714]">My Courses</h2>
          <Link to="/courses/create" className="btn-orange text-xs px-4 py-2">+ New course</Link>
        </div>
        <div className="grid md:grid-cols-2 gap-4">
          {courses.length === 0 ? (
            <div className="col-span-2 bg-white rounded-2xl border border-[#E8E1D8] p-12 text-center">
              <p className="text-[#6B6560]">No courses yet. <Link to="/courses/create" className="text-[#CF7249] font-semibold underline">Create one</Link></p>
            </div>
          ) : courses.map((c, i) => {
            const accents = ['#CF7249','#2D6A6A','#C4827A','#8B9BB4'];
            const bgs     = ['#FEF3EC','#EBF4F4','#FAEDEC','#EFF2F7'];
            const a = accents[i % 4], b = bgs[i % 4];
            return (
              <Link key={c.course_id} to={`/courses/${c.course_id}`}
                className="bg-white rounded-2xl border border-[#E8E1D8] p-6 hover:shadow-md hover:border-transparent transition-all">
                <div className="flex items-start justify-between mb-3">
                  <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background: b, color: a }}>{c.course_code}</span>
                  <span className="text-xs text-[#A8A29E]">{c.semester} {c.year}</span>
                </div>
                <h3 className="font-bold text-[#1A1714] mb-3">{c.course_name}</h3>
                <div className="flex gap-5 text-xs text-[#6B6560]">
                  <span><strong className="text-[#1A1714]">{c.student_count || 0}</strong> students</span>
                  <span><strong className="text-[#1A1714]">{c.assignment_count || 0}</strong> assignments</span>
                </div>
              </Link>
            );
          })}
        </div>
      </main>
    </div>
  );
};

export default InstructorDashboard;
