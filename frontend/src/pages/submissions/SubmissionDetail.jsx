import React, { useState, useEffect, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import submissionService from '../../services/submissionService';
import analysisService from '../../services/analysisService';

const norm   = (v) => v == null ? 0 : v > 1 ? v / 100 : v;
const pct    = (v) => `${Math.round(norm(v) * 100)}%`;
const EXT_LANG = { '.cpp':'C++','.c':'C','.h':'C/C++','.hpp':'C++','.java':'Java','.py':'Python','.js':'JavaScript','.jsx':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript' };
const LANG_CLR = { 'C++':'bg-blue-100 text-blue-700','C':'bg-sky-100 text-sky-700','Java':'bg-orange-100 text-orange-700','Python':'bg-yellow-100 text-yellow-700','JavaScript':'bg-amber-100 text-amber-700','TypeScript':'bg-indigo-100 text-indigo-700' };
const getExt   = (n) => '.' + n.split('.').pop().toLowerCase();
const fmtSize  = (b) => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(1)} KB`;

const STATUS_ST = {
  completed:  { badge:'bg-emerald-50 text-emerald-700 border-emerald-200', dot:'bg-emerald-500',            label:'Completed' },
  processing: { badge:'bg-blue-50 text-blue-700 border-blue-200',         dot:'bg-blue-500 animate-pulse', label:'Analyzing' },
  failed:     { badge:'bg-red-50 text-red-600 border-red-200',            dot:'bg-red-500',                label:'Failed'    },
  pending:    { badge:'bg-[#FEF3EC] text-[#CF7249] border-[#F4C9AA]',    dot:'bg-[#CF7249]',              label:'Pending'   },
};

/* ── Soft SVG icons ── */
const Ico = {
  ArrowLeft: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M19 12H5M12 5l-7 7 7 7"/>
    </svg>
  ),
  File: () => (
    <svg width="18" height="18" fill="none" stroke="#CF7249" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/>
      <polyline points="13 2 13 9 20 9"/>
    </svg>
  ),
  Files: () => (
    <svg width="17" height="17" fill="none" stroke="#CF7249" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  ),
  Shield: () => (
    <svg width="17" height="17" fill="none" stroke="#CF7249" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  ),
  User: () => (
    <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/>
      <circle cx="12" cy="7" r="4"/>
    </svg>
  ),
  Calendar: () => (
    <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <rect x="3" y="4" width="18" height="18" rx="2"/>
      <line x1="16" y1="2" x2="16" y2="6"/>
      <line x1="8" y1="2" x2="8" y2="6"/>
      <line x1="3" y1="10" x2="21" y2="10"/>
    </svg>
  ),
  Book: () => (
    <svg width="13" height="13" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/>
      <path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
    </svg>
  ),
  ExternalLink: () => (
    <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
  ),
};

function ScoreBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-2">
        <span className="text-[#6B6560] font-medium">{label}</span>
        <span className="font-black text-[#1A1714]">{pct(value)}</span>
      </div>
      <div className="h-2.5 bg-[#F0EBE3] rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color} transition-all duration-700`} style={{ width: pct(value) }} />
      </div>
    </div>
  );
}

function InfoRow({ icon, label, value }) {
  return (
    <div className="flex flex-col gap-0.5">
      <span className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest text-[#A8A29E]">
        {icon}{label}
      </span>
      <span className="text-sm font-bold text-[#1A1714] pl-5">{value}</span>
    </div>
  );
}

const SubmissionDetail = () => {
  const { submissionId } = useParams();
  const { isInstructor } = useAuth();
  const [submission, setSubmission] = useState(null);
  const [analysis,   setAnalysis]   = useState(null);
  const [loading,    setLoading]    = useState(true);
  const pollRef = useRef(null);

  const fetchAll = async () => {
    try {
      const sub = await submissionService.getSubmissionById(submissionId);
      setSubmission(sub);
      if (sub.analysis_status === 'completed') {
        try { const res = await analysisService.getSubmissionResults(submissionId); setAnalysis(res); } catch (_) {}
      }
      return sub.analysis_status;
    } catch (e) { console.error(e); return null; }
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchAll().then(status => {
      if (status === 'processing' || status === 'pending') {
        pollRef.current = setInterval(async () => {
          const s = await fetchAll();
          if (s === 'completed' || s === 'failed' || !s) { clearInterval(pollRef.current); pollRef.current = null; }
        }, 5000);
      }
    });
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, [submissionId]);

  if (loading) return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#CF7249] border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!submission) return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center">
      <p className="text-[#6B6560]">Submission not found.</p>
    </div>
  );

  const status     = submission.analysis_status || 'pending';
  const S          = STATUS_ST[status] || STATUS_ST.pending;
  const overallPct = analysis ? Math.round(norm(analysis.overall_similarity) * 100) : 0;
  const riskClr    = overallPct >= 85 ? 'text-[#C4827A]' : overallPct >= 70 ? 'text-[#CF7249]' : 'text-[#2D6A6A]';
  const barClr     = overallPct >= 85 ? 'bg-[#C4827A]'   : overallPct >= 70 ? 'bg-[#CF7249]'   : 'bg-[#2D6A6A]';

  return (
    <div className="min-h-screen bg-[#F7F3EE]">
      <div className="pt-16" />

      {/* ── Sticky breadcrumb bar ── */}
      <div className="bg-white border-b border-[#E8E1D8] sticky top-16 z-40">
        <div className="max-w-5xl mx-auto px-6 py-2 flex items-center">
          <Link
            to={`/assignments/${submission.assignment_id}`}
            className="inline-flex items-center gap-2 text-xs font-semibold text-[#A8A29E] hover:text-[#CF7249] transition-colors"
          >
            <Ico.ArrowLeft />
            {submission.assignment_title}
          </Link>
        </div>
      </div>

      {/*  Hero header  */}
      <div className="bg-white border-b border-[#E8E1D8]">
        <div className="max-w-5xl mx-auto px-6 pt-6 pb-4">
          <div className="flex items-start justify-between gap-6 flex-wrap">
            <div className="space-y-2">
              <h1 className="text-2xl font-black text-[#CF7249] tracking-tight leading-none">
                Submission Details
              </h1>
              <p className="text-xs text-[#A8A29E] flex flex-wrap items-center gap-x-3 gap-y-1">
                <span className="flex items-center gap-1.5"><Ico.User />{submission.student_name}</span>
                <span className="text-[#D4CEC8]"> b7</span>
                <span className="flex items-center gap-1.5"><Ico.Book />{submission.course_code}</span>
                <span className="text-[#D4CEC8]"> b7</span>
                <span className="flex items-center gap-1.5"><Ico.Calendar />{new Date(submission.submitted_at).toLocaleString()}</span>
              </p>
            </div>
            <span className={`self-start inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-black border ${S.badge}`}>
              <span className={`w-2 h-2 rounded-full ${S.dot}`} />
              {S.label}
            </span>
          </div>

          {status === 'processing' && (
            <div className="mt-4 flex items-center gap-3 px-5 py-3 rounded-2xl bg-blue-50 border border-blue-200">
              <span className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
              <p className="text-xs text-blue-800 font-semibold">Analysis is running — page will update automatically.</p>
            </div>
          )}
        </div>
      </div>

      {/* ── Content ── */}
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="grid lg:grid-cols-3 gap-6">

          {/* ── Main column ── */}
          <div className="lg:col-span-2 space-y-6">

            {/* Submitted files */}
            <div className="bg-white rounded-3xl border border-[#E8E1D8] overflow-hidden shadow-sm">
              <div className="px-7 py-5 border-b border-[#F0EBE3] flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-[#FEF3EC] flex items-center justify-center flex-shrink-0">
                  <Ico.Files />
                </div>
                <div>
                  <h2 className="text-base font-black text-[#1A1714]">Submitted Files</h2>
                  <p className="text-xs text-[#A8A29E]">{submission.files?.length || 0} file{submission.files?.length !== 1 ? 's' : ''} uploaded</p>
                </div>
              </div>
              <div className="p-5 space-y-3">
                {!submission.files?.length
                  ? <p className="text-sm text-[#A8A29E] text-center py-10">No files found.</p>
                  : submission.files.map((file, i) => {
                    const lang = EXT_LANG[getExt(file.filename)];
                    return (
                      <div key={i} className="flex items-center gap-4 p-4 rounded-2xl bg-[#F7F3EE] hover:bg-[#F0EBE3] transition-colors group">
                        <div className="w-10 h-10 rounded-xl bg-white border border-[#E8E1D8] flex items-center justify-center flex-shrink-0 group-hover:border-[#CF7249]/30 transition-colors">
                          <Ico.File />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-bold text-[#1A1714] truncate">{file.filename}</p>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-[#A8A29E]">{fmtSize(file.file_size)}</span>
                            {lang && (
                              <span className={`text-[10px] font-black px-2 py-0.5 rounded-lg ${LANG_CLR[lang] || 'bg-gray-100 text-gray-600'}`}>
                                {lang}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    );
                  })
                }
              </div>
            </div>

            {/* Analysis results */}
            {status === 'completed' && analysis && (
              <div className="bg-white rounded-3xl border border-[#E8E1D8] overflow-hidden shadow-sm">
                <div className="px-7 py-5 border-b border-[#F0EBE3] flex items-center justify-between gap-4">
                  <div className="flex items-center gap-3">
                    <div className="w-9 h-9 rounded-xl bg-[#FEF3EC] flex items-center justify-center flex-shrink-0">
                      <Ico.Shield />
                    </div>
                    <div>
                      <h2 className="text-base font-black text-[#1A1714]">Analysis Results</h2>
                      <p className="text-xs text-[#A8A29E]">Plagiarism detection breakdown</p>
                    </div>
                  </div>
                  {isInstructor && (
                    <Link
                      to={`/analysis/assignment/${submission.assignment_id}`}
                      className="inline-flex items-center gap-1.5 text-xs font-black text-[#CF7249] hover:text-[#B85E38] transition-colors"
                    >
                      Full Report <Ico.ExternalLink />
                    </Link>
                  )}
                </div>

                <div className="p-7 space-y-7">
                  {/* Big score ring */}
                  <div className="flex items-center gap-6 p-6 bg-[#F7F3EE] rounded-2xl">
                    <div className={`text-5xl font-black leading-none ${riskClr}`}>{overallPct}%</div>
                    <div className="flex-1">
                      <div className="h-3 bg-[#E8E1D8] rounded-full overflow-hidden mb-2.5">
                        <div className={`h-full rounded-full ${barClr} transition-all duration-700`} style={{ width: `${overallPct}%` }} />
                      </div>
                      <p className="text-xs font-semibold text-[#6B6560]">
                        {overallPct >= 85
                          ? 'High similarity — review recommended'
                          : overallPct >= 70
                          ? 'Moderate similarity — worth checking'
                          : 'Low similarity — looks original'}
                      </p>
                    </div>
                  </div>

                  {/* 4-type breakdown */}
                  <div className="grid grid-cols-2 gap-5">
                    <ScoreBar label="Type-1 (Exact)"      value={analysis.type1_score} color="bg-blue-400"   />
                    <ScoreBar label="Type-2 (Renamed)"    value={analysis.type2_score} color="bg-violet-400" />
                    <ScoreBar label="Type-3 (Structural)" value={analysis.type3_score} color="bg-[#CF7249]"  />
                    <ScoreBar label="Type-4 (Semantic)"   value={analysis.type4_score} color="bg-[#8B9BB4]"  />
                  </div>

                  {/* Similar submissions */}
                  {analysis.clonePairs?.length > 0 && (
                    <div>
                      <h3 className="text-sm font-black text-[#1A1714] mb-4">
                        Similar Submissions
                        <span className="ml-2 text-[#A8A29E] font-bold">({analysis.clonePairs.length})</span>
                      </h3>
                      <div className="space-y-2.5">
                        {analysis.clonePairs.map((pair, i) => {
                          const s  = Math.round(norm(pair.similarity) * 100);
                          const rc = s >= 85
                            ? 'bg-[#FAEDEC] border-[#E8B5B0] text-[#C4827A]'
                            : s >= 70
                            ? 'bg-[#FEF3EC] border-[#F4C9AA] text-[#CF7249]'
                            : 'bg-[#F7F3EE] border-[#E8E1D8] text-[#6B6560]';
                          return (
                            <div key={i} className={`flex items-center justify-between px-5 py-4 rounded-2xl border ${rc}`}>
                              <div>
                                <p className="text-sm font-black">{pair.student_b_name || `Submission #${pair.submission_b_id}`}</p>
                                <p className="text-xs opacity-60 mt-0.5 capitalize">{pair.clone_type} clone</p>
                              </div>
                              <span className="text-lg font-black">{s}%</span>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {status === 'failed' && (
              <div className="bg-white rounded-3xl border border-red-200 p-7">
                <p className="text-sm font-black text-red-700 mb-1">Analysis Failed</p>
                <p className="text-xs text-red-500">The analysis engine could not process this submission.</p>
              </div>
            )}
          </div>

          {/* ── Sidebar ── */}
          <div className="space-y-4">
            {/* Info card */}
            <div className="bg-white rounded-3xl border border-[#E8E1D8] p-6 shadow-sm space-y-5">
              <h3 className="text-xs font-black uppercase tracking-widest text-[#A8A29E]">Submission Info</h3>
              <InfoRow icon={<Ico.User />}     label="Student"   value={submission.student_name} />
              <div className="w-full h-px bg-[#F0EBE3]" />
              <InfoRow icon={<Ico.Book />}     label="Course"    value={`${submission.course_code} — ${submission.course_name}`} />
              <div className="w-full h-px bg-[#F0EBE3]" />
              <InfoRow icon={<Ico.Calendar />} label="Submitted" value={new Date(submission.submitted_at).toLocaleDateString()} />
              <div className="w-full h-px bg-[#F0EBE3]" />
              <InfoRow icon={<Ico.Files />}    label="Files"     value={submission.files?.length || 0} />
            </div>

            {/* Actions card */}
            <div className="bg-white rounded-3xl border border-[#E8E1D8] p-5 shadow-sm space-y-3">
              <Link
                to={`/assignments/${submission.assignment_id}`}
                className="flex items-center justify-center gap-2 w-full py-3 rounded-2xl border border-[#E8E1D8] text-xs font-black text-[#1A1714] hover:bg-[#F7F3EE] transition-colors"
              >
                View Assignment
              </Link>
              {isInstructor && (
                <Link
                  to={`/analysis/assignment/${submission.assignment_id}`}
                  className="flex items-center justify-center gap-2 w-full py-3 rounded-2xl bg-[#CF7249] text-white text-xs font-black hover:bg-[#B85E38] transition-colors shadow-sm"
                >
                  <Ico.Shield />
                  Plagiarism Report
                </Link>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default SubmissionDetail;
