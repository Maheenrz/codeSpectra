import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import PageLoader from '../../Components/common/PageLoader';

const ACCENTS = [
  { accent: '#CF7249', bg: '#FEF3EC' },
  { accent: '#2D6A6A', bg: '#EBF4F4' },
  { accent: '#C4827A', bg: '#FAEDEC' },
  { accent: '#8B9BB4', bg: '#EFF2F7' },
];

const IconLogOut = () => (<svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>);

const CourseList = () => {
  const { user, isInstructor, logout } = useAuth();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchCourses(); }, []);

  const fetchCourses = async () => {
    try {
      const data = isInstructor
        ? await courseService.getInstructorCourses()
        : await courseService.getStudentCourses();
      setCourses(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  if (loading) return <PageLoader message="Loading courses…" />;

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      <main className="max-w-6xl mx-auto px-6 pt-20 pb-12">
        <div className="flex items-end justify-between mb-10">
          <div>
            <p className="text-xs font-semibold tracking-[0.2em] uppercase text-[#CF7249] mb-2">
              {isInstructor ? 'Teaching' : 'Enrolled in'}
            </p>
            <h1 className="text-4xl font-bold text-[#1A1714]">My Courses</h1>
            <p className="text-[#6B6560] mt-1">{courses.length} course{courses.length !== 1 ? 's' : ''}</p>
          </div>
          {isInstructor
            ? <Link to="/courses/create" className="btn-orange">+ New course</Link>
            : <Link to="/courses/join" className="btn-orange">+ Join course</Link>}
        </div>

        {courses.length === 0 ? (
          <div className="bg-white rounded-3xl border border-[#E8E1D8] py-24 text-center">
            <h2 className="text-xl font-bold text-[#1A1714] mb-3">
              {isInstructor ? 'Create your first course' : 'Join your first course'}
            </h2>
            <p className="text-[#6B6560] mb-8 max-w-sm mx-auto">
              {isInstructor ? 'Set up a course and invite students.' : 'Enter a join code from your instructor.'}
            </p>
            {isInstructor
              ? <Link to="/courses/create" className="btn-orange">Create course</Link>
              : <Link to="/courses/join" className="btn-orange">Join course</Link>}
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {courses.map((c, idx) => {
              const A = ACCENTS[idx % ACCENTS.length];
              return (
                <Link key={c.course_id} to={`/courses/${c.course_id}`}
                  className="group bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden hover:shadow-md hover:border-transparent transition-all">
                  <div className="h-1.5 w-full" style={{ background: A.accent }} />
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-4">
                      <span className="text-[11px] font-bold px-2.5 py-1 rounded-full" style={{ background: A.bg, color: A.accent }}>
                        {c.course_code}
                      </span>
                      <span className="text-[10px] text-[#A8A29E]">{c.semester} {c.year}</span>
                    </div>
                    <h3 className="text-lg font-bold text-[#1A1714] mb-1">{c.course_name}</h3>
                    <p className="text-xs text-[#A8A29E] mb-5">{isInstructor ? 'You are teaching' : c.instructor_name}</p>
                    <div className="flex items-center gap-5 pt-4 border-t border-[#F0EBE3] text-xs text-[#6B6560]">
                      <span><strong className="text-[#1A1714]">{c.student_count || 0}</strong> students</span>
                      <span><strong className="text-[#1A1714]">{c.assignment_count || 0}</strong> assignments</span>
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>
        )}
      </main>
    </div>
  );
};

export default CourseList;
