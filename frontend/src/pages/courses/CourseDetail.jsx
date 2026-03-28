import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import courseService from '../../services/courseService';
import assignmentService from '../../services/assignmentService';
import PageLoader from '../../Components/common/PageLoader';

const IconBack = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>
);

// ── Minimalist vectors ────────────────────────────────────────────────────────

const EmptyAssignmentVector = () => (
  <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-5 opacity-70">
    <rect x="18" y="12" width="64" height="76" rx="7" stroke="#CF7249" strokeWidth="2.2" fill="#FEF3EC"/>
    <line x1="30" y1="34" x2="70" y2="34" stroke="#CF7249" strokeWidth="2" strokeLinecap="round"/>
    <line x1="30" y1="46" x2="62" y2="46" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <line x1="30" y1="58" x2="55" y2="58" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="72" cy="72" r="15" fill="#CF7249"/>
    <line x1="72" y1="65" x2="72" y2="79" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
    <line x1="65" y1="72" x2="79" y2="72" stroke="white" strokeWidth="2.5" strokeLinecap="round"/>
  </svg>
);

const EmptyStudentsVector = () => (
  <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-5 opacity-70">
    <circle cx="50" cy="36" r="16" stroke="#CF7249" strokeWidth="2.2" fill="#FEF3EC"/>
    <path d="M18 82c0-17.673 14.327-32 32-32s32 14.327 32 32" stroke="#CF7249" strokeWidth="2.2" strokeLinecap="round" fill="none"/>
    <circle cx="78" cy="38" r="10" stroke="#E8D5C8" strokeWidth="1.8" fill="white"/>
    <path d="M63 66c4-5 9-8 15-8" stroke="#E8D5C8" strokeWidth="1.8" strokeLinecap="round"/>
  </svg>
);

// Marker-hand style — "page not found"
const NotFoundVector = () => (
  <svg width="130" height="130" viewBox="0 0 130 130" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-6 opacity-60">
    {/* Notebook */}
    <rect x="24" y="20" width="82" height="90" rx="9" stroke="#CF7249" strokeWidth="2.5" fill="white"/>
    <rect x="24" y="20" width="18" height="90" rx="6" fill="#FEF3EC" stroke="#CF7249" strokeWidth="2.5"/>
    {/* Spiral binding dots */}
    <circle cx="33" cy="38" r="3" fill="#CF7249"/>
    <circle cx="33" cy="56" r="3" fill="#CF7249"/>
    <circle cx="33" cy="74" r="3" fill="#CF7249"/>
    <circle cx="33" cy="92" r="3" fill="#CF7249"/>
    {/* Lines on page */}
    <line x1="52" y1="44" x2="90" y2="44" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <line x1="52" y1="56" x2="84" y2="56" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    {/* Big ? */}
    <text x="56" y="94" fontFamily="Georgia, serif" fontSize="36" fontWeight="700" fill="#CF7249" opacity="0.35">?</text>
    {/* Marker squiggle at bottom */}
    <path d="M40 114 Q55 108 70 114 Q85 120 100 114" stroke="#CF7249" strokeWidth="2" strokeLinecap="round" fill="none" opacity="0.3"/>
  </svg>
);

// ── Duplicate warning badge in the assignment list ──────────────────────────
const DuplicateWarning = ({ count }) => (
  <div className="flex items-start gap-2.5 px-4 py-3 rounded-xl bg-amber-50 border border-amber-200 mb-3">
    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#D97706" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="flex-shrink-0 mt-0.5">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
    <p className="text-xs text-amber-700 leading-relaxed">
      <strong>{count} duplicate assignment title{count > 1 ? 's' : ''} detected.</strong>{' '}
      Use the <span className="font-semibold text-red-600">delete icon</span> on duplicate cards to remove them.
    </p>
  </div>
);

// ── Helper: normalise whatever shape the backend returns ──────────────────────
const normaliseCourse = (raw) => {
  if (!raw) return null;
  // unwrap { course: {...} } or { data: {...} }
  const c = raw?.course ?? raw?.data ?? raw;
  if (!c || typeof c !== 'object') return null;
  return {
    ...c,
    // accept any common field name for the primary key
    course_id: c.course_id ?? c.id ?? c.courseId ?? null,
  };
};

// ── Retry fetcher — handles race-condition for newly created courses ───────────
const fetchWithRetry = async (fn, maxAttempts = 3, delay = 900) => {
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await fn();
      return result;
    } catch (err) {
      if (attempt === maxAttempts) throw err;
      await new Promise(r => setTimeout(r, delay * attempt)); // 900ms, 1800ms
    }
  }
};

// ── Detect duplicate titles ────────────────────────────────────────────────────
const findDuplicateTitles = (list) => {
  const seen = {};
  list.forEach(a => {
    const t = (a.title || '').trim().toLowerCase();
    seen[t] = (seen[t] || 0) + 1;
  });
  return Object.values(seen).filter(n => n > 1).reduce((a, b) => a + b - 1, 0);
};

const CourseDetail = () => {
  const { courseId } = useParams();
  const { user, isInstructor } = useAuth();
  const [course, setCourse]           = useState(null);
  const [assignments, setAssignments] = useState([]);
  const [students, setStudents]       = useState([]);
  const [activeTab, setActiveTab]     = useState('assignments');
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState('');
  const [regenerating, setRegenerating] = useState(false);
  const [copied, setCopied]           = useState(false);
  const [deletingId, setDeletingId]   = useState(null);

  useEffect(() => { fetchData(); }, [courseId]);

  const fetchData = async () => {
    setCourse(null);
    setAssignments([]);
    setStudents([]);
    setLoading(true);
    setError('');

    try {
      // Retry handles race-condition right after course creation
      const rawCourse = await fetchWithRetry(
        () => courseService.getCourseById(courseId),
        3,
        800,
      );

      const normalizedCourse = normaliseCourse(rawCourse);

      if (!normalizedCourse?.course_id) {
        setError('Course not found.');
        setLoading(false);
        return;
      }
      setCourse(normalizedCourse);

      // Assignments — failure here must NOT break the page
      try {
        const assignmentsData = await assignmentService.getCourseAssignments(
          normalizedCourse.course_id,
        );
        setAssignments(Array.isArray(assignmentsData) ? assignmentsData : []);
      } catch {
        setAssignments([]);
      }

      // Students — instructor only
      if (isInstructor) {
        try {
          const s = await courseService.getCourseStudents(normalizedCourse.course_id);
          setStudents(Array.isArray(s) ? s : []);
        } catch {
          setStudents([]);
        }
      }
    } catch (e) {
      console.error(e);
      setError('Course not found or you do not have access.');
    } finally {
      setLoading(false);
    }
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

  const handleDeleteAssignment = async (e, assignmentId, title) => {
    e.preventDefault();
    e.stopPropagation();
    if (!window.confirm(`Delete "${title}"?\n\nThis cannot be undone and will remove all associated submissions.`)) return;
    setDeletingId(assignmentId);
    try {
      await assignmentService.deleteAssignment(assignmentId);
      setAssignments(prev => prev.filter(a => (a.assignment_id ?? a.id) !== assignmentId));
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to delete assignment.');
    } finally {
      setDeletingId(null);
    }
  };

  if (loading) return <PageLoader message="Loading course…" />;

  if (error || !course) return (
    <div className="min-h-screen bg-[#F7F3EE] flex flex-col items-center justify-center gap-3 px-6 text-center">
      <NotFoundVector />
      <p className="text-lg font-bold text-[#1A1714]">{error || 'Course not found.'}</p>
      <p className="text-sm text-[#A8A29E] max-w-xs">
        This course may have been deleted or you may not have access to it.
      </p>
      <Link to="/courses" className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-white bg-[#CF7249] px-5 py-2.5 rounded-xl hover:bg-[#B85E38] transition-colors">
        ← Back to Courses
      </Link>
    </div>
  );

  const isPastDue = (date) => new Date(date) < new Date();
  const duplicateCount = isInstructor ? findDuplicateTitles(assignments) : 0;

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
                {isInstructor
                  ? `${students.length} student${students.length !== 1 ? 's' : ''} enrolled`
                  : `Instructor: ${course.instructor_name}`}
              </p>
            </div>
            {isInstructor && (
              <Link to={`/assignments/create?courseId=${course.course_id}`} className="btn-orange flex-shrink-0">
                + New Assignment
              </Link>
            )}
          </div>

          {/* Tabs */}
          <div className="flex gap-6 mt-6">
            {['assignments', isInstructor && 'students'].filter(Boolean).map(tab => (
              <button key={tab} onClick={() => setActiveTab(tab)}
                className={`pb-3 text-sm font-semibold capitalize border-b-2 transition-colors
                  ${activeTab === tab
                    ? 'border-[#CF7249] text-[#CF7249]'
                    : 'border-transparent text-[#6B6560] hover:text-[#1A1714]'}`}>
                {tab}{' '}
                {tab === 'assignments' ? `(${assignments.length})` : `(${students.length})`}
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">

          {/* Main content */}
          <div className="lg:col-span-2">

            {/* ── Assignments tab ── */}
            {activeTab === 'assignments' && (
              <div className="space-y-3">
                {assignments.length === 0 ? (
                  <div className="bg-white rounded-2xl border border-[#E8E1D8] py-20 px-8 text-center">
                    <EmptyAssignmentVector />
                    <p className="text-base font-bold text-[#1A1714] mb-2">No assignments yet</p>
                    <p className="text-sm text-[#6B6560] mb-6 max-w-xs mx-auto">
                      {isInstructor
                        ? 'Create the first assignment for this course.'
                        : "Your instructor hasn't posted any assignments yet."}
                    </p>
                    {isInstructor && (
                      <Link to={`/assignments/create?courseId=${course.course_id}`} className="btn-orange">
                        Create First Assignment
                      </Link>
                    )}
                  </div>
                ) : (
                  <>
                    {/* Duplicate warning — auto-detected */}
                    {isInstructor && duplicateCount > 0 && (
                      <DuplicateWarning count={duplicateCount} />
                    )}

                    {/* Hint for instructors */}
                    {isInstructor && (
                      <p className="text-xs text-[#A8A29E] text-right mb-1">
                        Click the{' '}
                        <span className="text-[#C4827A] font-semibold">delete icon</span>{' '}
                        on any assignment to remove it
                      </p>
                    )}

                    {assignments.map(a => {
                      const aId = a.assignment_id ?? a.id;
                      return (
                        <div key={aId} className="relative">
                          <Link
                            to={`/assignments/${aId}`}
                            className={`block bg-white rounded-2xl border border-[#E8E1D8] p-5 hover:shadow-md hover:border-transparent transition-all ${isInstructor ? 'pr-14' : ''}`}
                          >
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

                          {/* Delete button — instructor only */}
                          {isInstructor && (
                            <button
                              onClick={(e) => handleDeleteAssignment(e, aId, a.title)}
                              disabled={deletingId === aId}
                              title="Delete assignment"
                              className="absolute top-1/2 -translate-y-1/2 right-4
                                w-8 h-8 rounded-xl flex items-center justify-center transition-all
                                bg-white border border-[#F0C4C0] text-[#C4827A]
                                hover:bg-[#FAEDEC] hover:border-[#C4827A] hover:scale-110
                                disabled:opacity-40 disabled:cursor-not-allowed"
                            >
                              {deletingId === aId ? (
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="animate-spin">
                                  <path d="M12 2a10 10 0 0110 10" opacity="0.3"/><path d="M12 2a10 10 0 0110 10"/>
                                </svg>
                              ) : (
                                <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                                  <polyline points="3 6 5 6 21 6"/>
                                  <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                                  <path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/>
                                </svg>
                              )}
                            </button>
                          )}
                        </div>
                      );
                    })}
                  </>
                )}
              </div>
            )}

            {/* ── Students tab ── */}
            {activeTab === 'students' && isInstructor && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden">
                {students.length === 0 ? (
                  <div className="py-20 px-8 text-center">
                    <EmptyStudentsVector />
                    <p className="text-base font-bold text-[#1A1714] mb-2">No students enrolled yet</p>
                    <p className="text-xs text-[#A8A29E] mt-1">Share the join code so students can join.</p>
                  </div>
                ) : (
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-[#F0EBE3]">
                        {['Name', 'Email', 'Enrolled'].map(h => (
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
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            )}
          </div>

          {/* ── Sidebar ── */}
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
                  ['Code',        course.course_code],
                  ['Semester',    `${course.semester} ${course.year}`],
                  ['Students',    students.length || course.student_count || 0],
                  ['Assignments', assignments.length],
                ].map(([label, value]) => (
                  <div key={label} className="flex justify-between">
                    <span className="text-[#A8A29E]">{label}</span>
                    <span className="font-semibold text-[#1A1714]">{value}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Duplicate / delete hint — shown when instructor has assignments */}
            {isInstructor && assignments.length > 0 && (
              <div className="rounded-2xl border border-[#F0C4C0] bg-[#FAEDEC]/60 p-4">
                <div className="flex items-start gap-2.5">
                  <svg width="14" height="14" fill="none" stroke="#C4827A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24" className="flex-shrink-0 mt-0.5">
                    <polyline points="3 6 5 6 21 6"/>
                    <path d="M19 6l-1 14a2 2 0 01-2 2H8a2 2 0 01-2-2L5 6"/>
                    <path d="M9 6V4h6v2"/>
                  </svg>
                  <p className="text-xs text-[#C4827A] leading-relaxed">
                    Use the delete icon on each assignment card to remove duplicates or unwanted entries.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;
