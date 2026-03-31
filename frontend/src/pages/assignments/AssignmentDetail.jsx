import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import assignmentService from '../../services/assignmentService';
import submissionService from '../../services/submissionService';
import analysisService from '../../services/analysisService';
import PageLoader from '../../Components/common/PageLoader';

const IconBack   = () => <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="15 18 9 12 15 6"/></svg>;
const IconScan   = () => <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/><line x1="7" y1="12" x2="17" y2="12"/></svg>;
const IconChart  = () => <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>;
const IconUpload = () => <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>;
const Spin = ({ size=14 }) => <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" className="animate-spin"><path d="M12 2a10 10 0 0110 10" opacity="0.3"/><path d="M12 2a10 10 0 0110 10"/></svg>;

// Minimalist "not found" vector
const NotFoundVector = () => (
  <svg width="100" height="100" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-5 opacity-60">
    <rect x="15" y="12" width="70" height="76" rx="8" stroke="#CF7249" strokeWidth="2.2" fill="#FEF3EC"/>
    <line x1="28" y1="36" x2="72" y2="36" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <line x1="28" y1="48" x2="62" y2="48" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <line x1="28" y1="60" x2="54" y2="60" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="70" cy="72" r="14" fill="white" stroke="#CF7249" strokeWidth="2.2"/>
    <line x1="66" y1="68" x2="74" y2="76" stroke="#CF7249" strokeWidth="2.2" strokeLinecap="round"/>
    <line x1="74" y1="68" x2="66" y2="76" stroke="#CF7249" strokeWidth="2.2" strokeLinecap="round"/>
  </svg>
);

const STATUS = {
  completed:  { bg:'bg-emerald-50', text:'text-emerald-700', dot:'bg-emerald-500',            label:'Done'      },
  processing: { bg:'bg-blue-50',    text:'text-blue-700',    dot:'bg-blue-500 animate-pulse', label:'Analyzing' },
  failed:     { bg:'bg-red-50',     text:'text-red-600',     dot:'bg-red-500',                label:'Failed'    },
  pending:    { bg:'bg-[#F7F3EE]',  text:'text-[#6B6560]',  dot:'bg-[#A8A29E]',             label:'Pending'   },
};

const StatusBadge = ({ status }) => {
  const S = STATUS[status] || STATUS.pending;
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-semibold ${S.bg} ${S.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${S.dot}`} />{S.label}
    </span>
  );
};

const AssignmentDetail = () => {
  const { assignmentId } = useParams();
  const { user, isStudent, isInstructor } = useAuth();
  const [assignment,   setAssignment]   = useState(null);
  const [submissions,  setSubmissions]  = useState([]);
  const [mySubmission, setMySubmission] = useState(null);
  const [loading,      setLoading]      = useState(true);
  const [notFound,     setNotFound]     = useState(false);
  const [analyzing,    setAnalyzing]    = useState(false);
  const [analyzeMsg,   setAnalyzeMsg]   = useState('');
  const [analyzeError, setAnalyzeError] = useState('');
  const pollRef = useRef(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setNotFound(false);
    try {
      const asgn = await assignmentService.getAssignmentById(assignmentId);
      if (!asgn) { setNotFound(true); return; }
      setAssignment(asgn);

      if (isInstructor) {
        const subs = await assignmentService.getAssignmentSubmissions(assignmentId);
        setSubmissions(Array.isArray(subs) ? subs : []);
      } else if (isStudent) {
        const all  = await submissionService.getStudentSubmissions();
        const mine = all.find(s => s.assignment_id === parseInt(assignmentId));
        setMySubmission(mine || null);
      }
    } catch (e) {
      console.error(e);
      if (e?.response?.status === 404) setNotFound(true);
    } finally {
      setLoading(false);
    }
  }, [assignmentId, isInstructor, isStudent]);

  useEffect(() => {
    fetchData();
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [fetchData]);

  const handleAnalyzeAll = async () => {
    if (analyzing) return;
    setAnalyzing(true); setAnalyzeMsg('Starting analysis…'); setAnalyzeError('');
    try {
      await analysisService.analyzeAssignment(assignmentId);
      setAnalyzeMsg('Analysis running…');
      let attempts = 0;
      pollRef.current = setInterval(async () => {
        attempts++;
        const subs = await assignmentService.getAssignmentSubmissions(assignmentId);
        setSubmissions(subs);
        const done   = subs.filter(s => s.analysis_status === 'completed').length;
        const failed = subs.filter(s => s.analysis_status === 'failed').length;
        setAnalyzeMsg(`Analyzing… ${done}/${subs.length} complete`);
        const allDone = subs.every(s => ['completed','failed'].includes(s.analysis_status));
        if (allDone || attempts > 60) {
          clearInterval(pollRef.current);
          setAnalyzing(false);
          setAnalyzeMsg(done > 0 ? `Done — ${done} submission${done > 1 ? 's' : ''} processed.` : 'Finished.');
          if (failed > 0 && done === 0) { setAnalyzeMsg(''); setAnalyzeError(`Failed for ${failed} submission${failed > 1 ? 's' : ''}.`); }
        }
      }, 4000);
    } catch (err) {
      setAnalyzing(false); setAnalyzeMsg('');
      setAnalyzeError(err.response?.data?.error || 'Failed to start analysis. Is the engine running?');
    }
  };

  // ── Loading → always shows full CodeSpectra landing style ─────────────────
  if (loading) return <PageLoader message="Loading assignment…" />;

  // ── Not found ─────────────────────────────────────────────────────────────
  if (notFound || !assignment) return (
    <div className="min-h-screen bg-[#F7F3EE] flex flex-col items-center justify-center gap-3 px-6 text-center">
      <NotFoundVector />
      <p className="text-lg font-bold text-[#1A1714]">Assignment not found.</p>
      <p className="text-sm text-[#A8A29E] max-w-xs">
        This assignment may have been deleted or you may not have access.
      </p>
      <Link to="/courses" className="mt-3 inline-flex items-center gap-1.5 text-sm font-semibold text-white bg-[#CF7249] px-5 py-2.5 rounded-xl hover:bg-[#B85E38] transition-colors">
        ← Back to Courses
      </Link>
    </div>
  );

  const isPastDue      = new Date(assignment.due_date) < new Date();
  const completedCount = submissions.filter(s => s.analysis_status === 'completed').length;

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      {/* Sub-header */}
      <div className="bg-white border-b border-[#E8E1D8] pt-16">
        <div className="max-w-6xl mx-auto px-6 py-5">
          <Link to={`/courses/${assignment.course_id}`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-4 transition-colors">
            <IconBack /> {assignment.course_code} — {assignment.course_name}
          </Link>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <div className="flex items-center gap-2 mb-1.5">
                <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${isPastDue ? 'bg-red-50 text-red-600' : 'bg-emerald-50 text-emerald-700'}`}>
                  {isPastDue ? 'Closed' : 'Open'}
                </span>
              </div>
              <h1 className="text-xl font-bold text-[#1A1714]">{assignment.title}</h1>
              <p className="text-xs text-[#A8A29E] mt-1">Due {new Date(assignment.due_date).toLocaleString()}</p>
            </div>
            {isInstructor && (
              <div className="flex flex-wrap gap-2">
                <button onClick={handleAnalyzeAll} disabled={analyzing || submissions.length < 2}
                  className="btn-teal gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
                  {analyzing ? <><Spin /> Analyzing…</> : <><IconScan /> Analyze all</>}
                </button>
                <Link to={`/analysis/assignment/${assignmentId}`} className="btn-ghost gap-2">
                  <IconChart /> View report
                </Link>
                <Link to={`/assignments/edit/${assignmentId}`} className="btn-ghost gap-2">
                  ✏️ Edit
                </Link>
              </div>
            )}
            {isStudent && !isPastDue && (
              <Link to={`/submissions/submit?assignmentId=${assignmentId}`} className="btn-orange gap-2">
                <IconUpload /> {mySubmission ? 'Resubmit' : 'Submit'}
              </Link>
            )}
          </div>

          {analyzeMsg && (
            <div className="mt-4 flex items-center gap-2.5 px-4 py-3 rounded-xl bg-[#EBF4F4] border border-[#2D6A6A]/20">
              {analyzing && <Spin />}
              <p className="text-sm text-[#2D6A6A] font-medium">{analyzeMsg}</p>
            </div>
          )}
          {analyzeError && (
            <div className="mt-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200">
              <p className="text-sm text-red-700 font-medium">{analyzeError}</p>
            </div>
          )}
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-5">

            {/* Description */}
            <div className="bg-white rounded-2xl border border-[#E8E1D8] p-6">
              <h2 className="text-sm font-bold text-[#1A1714] mb-4">Description</h2>
              <p className="text-[#1A1714] text-base leading-relaxed whitespace-pre-wrap">{assignment.description}</p>
            </div>

            {/* Questions */}
            {assignment.questions?.length > 0 && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] p-6">
                <h2 className="text-sm font-bold text-[#1A1714] mb-4">Questions ({assignment.questions.length})</h2>
                <div className="space-y-4">
                  {assignment.questions.map((q, i) => (
                    <div key={i} className="flex gap-4 p-4 bg-[#F7F3EE] rounded-xl">
                      <div className="w-7 h-7 rounded-full bg-[#CF7249] text-white text-xs font-bold flex items-center justify-center flex-shrink-0 mt-0.5">{i + 1}</div>
                      <div className="flex-1">
                        <p className="font-bold text-[#1A1714] mb-1">{q.title}</p>
                        <p className="text-sm text-[#6B6560] leading-relaxed">{q.description}</p>
                        {q.expectedFiles?.length > 0 && (
                          <p className="text-xs font-mono text-[#A8A29E] mt-2">Expected: {q.expectedFiles.join(', ')}</p>
                        )}
                      </div>
                      <span className="text-sm font-bold text-[#CF7249] flex-shrink-0">{(q.maxMarks !== undefined && q.maxMarks !== null) ? q.maxMarks : '—'} pts</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Student — my submission */}
            {isStudent && mySubmission && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] p-6">
                <h2 className="text-sm font-bold text-[#1A1714] mb-4">My Submission</h2>
                <div className="flex items-center justify-between p-4 bg-[#F7F3EE] rounded-xl">
                  <div>
                    <p className="text-sm font-semibold text-[#1A1714]">Submitted {new Date(mySubmission.submitted_at).toLocaleString()}</p>
                    <p className="text-xs text-[#A8A29E] mt-0.5">{mySubmission.file_count || 0} files</p>
                    <div className="mt-2"><StatusBadge status={mySubmission.analysis_status} /></div>
                  </div>
                  <Link to={`/submissions/${mySubmission.submission_id}`} className="btn-ghost text-xs px-3 py-2">View details</Link>
                </div>
              </div>
            )}

            {isStudent && !mySubmission && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] p-10 text-center">
                <div className="w-12 h-12 rounded-2xl bg-[#FEF3EC] text-[#CF7249] flex items-center justify-center mx-auto mb-4">
                  <IconUpload />
                </div>
                <p className="text-sm font-semibold text-[#1A1714] mb-1">No submission yet</p>
                {!isPastDue
                  ? <Link to={`/submissions/submit?assignmentId=${assignmentId}`} className="btn-orange mt-4 inline-flex">Submit now</Link>
                  : <p className="text-xs text-red-500 mt-2">Assignment is past due.</p>}
              </div>
            )}

            {/* Instructor — submissions table */}
            {isInstructor && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden">
                <div className="flex items-center justify-between px-6 py-4 border-b border-[#F0EBE3]">
                  <div>
                    <h2 className="text-sm font-bold text-[#1A1714]">
                      Submissions{' '}
                      <span className="text-[10px] font-semibold text-[#A8A29E] bg-[#F7F3EE] px-1.5 py-0.5 rounded-full ml-1">
                        {submissions.length}
                      </span>
                    </h2>
                    {submissions.length > 0 && (
                      <p className="text-[11px] text-[#A8A29E] mt-0.5">
                        {completedCount} done · {submissions.filter(s=>s.analysis_status==='processing').length} analyzing · {submissions.filter(s=>s.analysis_status==='pending').length} pending
                      </p>
                    )}
                  </div>
                </div>
                {submissions.length === 0 ? (
                  <div className="px-6 py-14 text-center">
                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-4 opacity-40">
                      <rect x="8" y="6" width="32" height="36" rx="4" stroke="#CF7249" strokeWidth="1.8" fill="#FEF3EC"/>
                      <line x1="14" y1="18" x2="34" y2="18" stroke="#E8D5C8" strokeWidth="1.5" strokeLinecap="round"/>
                      <line x1="14" y1="24" x2="28" y2="24" stroke="#E8D5C8" strokeWidth="1.5" strokeLinecap="round"/>
                      <line x1="14" y1="30" x2="22" y2="30" stroke="#E8D5C8" strokeWidth="1.5" strokeLinecap="round"/>
                    </svg>
                    <p className="text-sm text-[#6B6560]">No submissions yet.</p>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-[#F0EBE3]">
                          {['Student','Submitted','Files','Status',''].map(h => (
                            <th key={h} className={`py-3 ${h===''?'pr-6 text-right':'pl-6 text-left'} text-[10px] font-bold uppercase tracking-widest text-[#A8A29E]`}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {submissions.map(sub => (
                          <tr key={sub.submission_id} className="border-b border-[#F0EBE3] last:border-0 hover:bg-[#F7F3EE]/50 transition-colors">
                            <td className="py-3.5 pl-6">
                              <p className="text-sm font-semibold text-[#1A1714]">{sub.student_name}</p>
                              <p className="text-[11px] text-[#A8A29E]">{sub.student_email}</p>
                            </td>
                            <td className="py-3.5 pl-6 text-xs text-[#6B6560]">{new Date(sub.submitted_at).toLocaleDateString()}</td>
                            <td className="py-3.5 pl-6 text-xs text-[#6B6560]">{sub.file_count||0}</td>
                            <td className="py-3.5 pl-6"><StatusBadge status={sub.analysis_status} /></td>
                            <td className="py-3.5 pr-6 text-right">
                              <Link to={`/submissions/${sub.submission_id}`} className="text-xs font-semibold text-[#CF7249] hover:underline">View</Link>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-[#E8E1D8] p-5">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Settings</h3>
              <div className="space-y-3">
                {[
                  ['Language',  assignment.primary_language],
                  ['Max size',  `${assignment.max_file_size_mb} MB`],
                  ['Extensions',assignment.allowed_extensions],
                  ['Submission',assignment.submission_mode||'files'],
                ].map(([label,value])=>(
                  <div key={label} className="flex justify-between items-start gap-2">
                    <span className="text-xs text-[#A8A29E]">{label}</span>
                    <span className="text-xs font-semibold text-[#1A1714] text-right">{value||'—'}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white rounded-2xl border border-[#E8E1D8] p-5">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Detection</h3>
              <div className="space-y-2">
                {[
                  [assignment.enable_type1,'Type-1','Exact copy','#C4827A','#FAEDEC'],
                  [assignment.enable_type2,'Type-2','Renamed variables','#CF7249','#FEF3EC'],
                  [assignment.enable_type3,'Type-3','Near-miss','#2D6A6A','#EBF4F4'],
                  [assignment.enable_type4,'Type-4','Semantic (beta)','#8B9BB4','#EFF2F7'],
                ].map(([enabled,label,desc,accent,bg])=>(
                  <div key={label} className={`flex items-center gap-2.5 px-3 py-2 rounded-lg ${enabled?'':'opacity-40'}`} style={{background:enabled?bg:'#F7F3EE'}}>
                    <span className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{background:enabled?accent:'#A8A29E'}} />
                    <span className="text-[11px] font-bold" style={{color:enabled?accent:'#A8A29E'}}>{label}</span>
                    <span className="text-[11px] text-[#6B6560]">{desc}</span>
                  </div>
                ))}
              </div>
            </div>

            {isInstructor && completedCount > 0 && (
              <div className="bg-[#1A1714] rounded-2xl p-5">
                <p className="text-xs font-bold text-[#CF7249] uppercase tracking-widest mb-2">Analysis ready</p>
                <p className="text-xs text-[#6B6560] mb-4">{completedCount} submission{completedCount>1?'s':''} processed.</p>
                <Link to={`/analysis/assignment/${assignmentId}`}
                  className="flex items-center justify-center gap-2 w-full py-2.5 rounded-xl bg-[#CF7249] text-white text-sm font-semibold hover:bg-[#B85E38] transition-colors">
                  <IconChart /> View report
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AssignmentDetail;
