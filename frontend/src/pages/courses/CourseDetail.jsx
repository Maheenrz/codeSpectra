import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import assignmentService from '../../services/assignmentService';
import PageLoader from '../../Components/common/PageLoader';

const IconBack = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
);
const IconLogOut = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
);

const CourseDetail = () => {
  const { courseId } = useParams();
  const { user, isInstructor, logout } = useAuth();
  const [course, setCourse]           = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents]       = useState([]);
  const [activeTab, setActiveTab]     = useState('assignments');
  const [loading, setLoading]         = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied]           = useState(false);

  useEffect(() => { fetchData(); }, [courseId]);

  const fetchData = async () => {
    try {
      const [courseData, assignmentsData] = await Promise.all([
        courseService.getCourseById(courseId),
        assignmentService.getCourseAssignments(courseId),
      ]);
      setCourse(courseData);
      setAssignments(assignmentsData);
      if (isInstructor) {
        const s = await courseService.getCourseStudents(courseId);
        setStudents(s);
      }
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const handleCopyCode = () => {
    if (course?.join_code) {
      navigator.clipboard.writeText(course.join_code);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleRegenerateCode = async () => {
    if (!window.confirm('Generate a new join code? The old code will stop working.')) return;
    setRegenerating(true);
    try {
      const result = await courseService.regenerateJoinCode(courseId);
      setCourse(c => ({ ...c, join_code: result.joinCode }));
    } catch (e) { console.error(e); }
    finally { setRegenerating(false); }
  };

  if (loading) return <PageLoader message="Loading course…" />;
  if (!course)  return <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center"><p className="text-[#6B6560]">Course not found.</p></div>;

  const isPastDue = (date) => new Date(date) < new Date();

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      {/* Sub-header */}
      <div className="bg-white border-b border-[#E8E1D8] pt-16">
        <div className="max-w-6xl mx-auto px-6 py-6">
          <Link to="/courses" className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-4 transition-colors">
            <IconBack /> All Courses
          </Link>
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#FEF3EC] text-[#CF7249]">{course.course_code}</span>
                <span className="text-xs text-[#A8A29E]">{course.semester} {course.year}</span>
              </div>
              <h1 className="text-2xl font-bold text-[#1A1714]">{course.course_name}</h1>
              <p className="text-sm text-[#6B6560] mt-1">
                {isInstructor ? `${students.length} students enrolled` : `Instructor: ${course.instructor_name}`}
              </p>
            </div>
            {isInstructor && (
              <Link to={`/assignments/create?courseId=${courseId}`} className="btn-orange flex-shrink-0">
                + New Assignment
              </Link>
            )}
          </div>

          {/* Tabs */}
          <div className="flex gap-6 mt-6">
            {['assignments', isInstructor && 'students'].filter(Boolean).map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={`pb-3 text-sm font-semibold capitalize border-b-2 transition-colors
                  ${activeTab === tab ? 'border-[#CF7249] text-[#CF7249]' : 'border-transparent text-[#6B6560] hover:text-[#1A1714]'}`}>
                {tab} {tab === 'assignments' ? `(${assignments.length})` : `(${students.length})`}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">

          {/* Main content */}
          <div className="lg:col-span-2">

            {/* Assignments tab */}
            {activeTab === 'assignments' && (
              <div className="space-y-3">
                {assignments.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-[#E8E1D8] p-12 text-center">
                    <p className="text-[#6B6560] mb-4">No assignments yet.</p>
                    {isInstructor && (
                      <Link to={`/assignments/create?courseId=${courseId}`} className="btn-orange">
                        Create First Assignment
                      </Link>
                    )}
                  </div>
                ) : assignments.map(a => (
                  <Link key={a.assignment_id} to={`/assignments/${a.assignment_id}`}
                    className="block bg-white rounded-2xl border border-[#E8E1D8] p-5 hover:shadow-md hover:border-transparent transition-all">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-[#1A1714] mb-1">{a.title}</h3>
                        <p className="text-sm text-[#6B6560] line-clamp-2 mb-3">{a.description}</p>
                        <div className="flex items-center gap-4 text-xs text-[#A8A29E]">
                          <span>Due {new Date(a.due_date).toLocaleDateString()}</span>
                          <span>{a.submission_count || 0} submissions</span>
                        </div>
                      </div>
                      <span className={`flex-shrink-0 text-[10px] font-bold px-2.5 py-1 rounded-full
                        ${isPastDue(a.due_date) ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-700'}`}>
                        {isPastDue(a.due_date) ? 'Closed' : 'Open'}
                      </span>
                    </div>
                  </Link>
                ))}
              </div>
            )}

            {/* Students tab */}
            {activeTab === 'students' && isInstructor && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden">
                {students.length === 0 ? (
                  <div className="p-12 text-center">
                    <p className="text-[#6B6560]">No students enrolled yet.</p>
                    <p className="text-xs text-[#A8A29E] mt-1">Share the join code from the sidebar.</p>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-[#F0EBE3]">
                        {['Name', 'Email', 'Enrolled', ''].map(h => (
                          <th key={h} className="py-3 px-5 text-left text-[10px] font-bold uppercase tracking-widest text-[#A8A29E]">{h}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {students.map(s => (
                        <tr key={s.user_id} className="border-b border-[#F0EBE3] last:border-0 hover:bg-[#F7F3EE]/50 transition-colors">
                          <td className="py-3.5 px-5 text-sm font-semibold text-[#1A1714]">{s.first_name} {s.last_name}</td>
                          <td className="py-3.5 px-5 text-sm text-[#6B6560]">{s.email}</td>
                          <td className="py-3.5 px-5 text-xs text-[#A8A29E]">{new Date(s.enrolled_at).toLocaleDateString()}</td>
                          <td className="py-3.5 px-5 text-right">
                            <span className="text-xs text-[#A8A29E]">—</span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            {/* Join code card */}
            {isInstructor && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] p-5">
                <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Join Code</p>
                <div className="bg-[#F7F3EE] rounded-xl p-4 text-center mb-4">
                  <p className="text-xs text-[#A8A29E] mb-2">Share with students</p>
                  <p className="font-mono text-3xl font-bold text-[#CF7249] tracking-widest select-all">
                    {course.join_code || '———'}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button onClick={handleCopyCode}
                    className="flex-1 py-2 rounded-xl border border-[#E8E1D8] text-xs font-bold text-[#1A1714] hover:bg-[#F7F3EE] transition-colors">
                    {copied ? '✓ Copied' : 'Copy'}
                  </button>
                  <button onClick={handleRegenerateCode} disabled={regenerating}
                    className="flex-1 py-2 rounded-xl bg-[#CF7249] text-white text-xs font-bold hover:bg-[#B85E38] transition-colors disabled:opacity-50">
                    {regenerating ? 'Generating…' : 'Regenerate'}
                  </button>
                </div>
              </div>
            )}

            {/* Course info */}
            <div className="bg-white rounded-2xl border border-[#E8E1D8] p-5">
              <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Course Info</p>
              <div className="space-y-3 text-sm">
                {[
                  ['Code',     course.course_code],
                  ['Semester', `${course.semester} ${course.year}`],
                  ['Students', students.length || course.student_count || 0],
                  ['Assignments', assignments.length],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-[#A8A29E]">{label}</span>
                    <span className="font-semibold text-[#1A1714]">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
