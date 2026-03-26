import React, { useState, useEffect, useRef } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import submissionService from '../../services/submissionService';
import analysisService from '../../services/analysisService';

const norm = (v) => v == null ? 0 : v > 1 ? v / 100 : v;
const pct  = (v) => `${Math.round(norm(v) * 100)}%`;
const EXT_LANG  = { '.cpp':'C++','.c':'C','.h':'C/C++','.hpp':'C++','.java':'Java','.py':'Python','.js':'JavaScript','.jsx':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript' };
const LANG_CLR  = { 'C++':'bg-blue-100 text-blue-700','C':'bg-sky-100 text-sky-700','Java':'bg-orange-100 text-orange-700','Python':'bg-yellow-100 text-yellow-700','JavaScript':'bg-amber-100 text-amber-700','TypeScript':'bg-indigo-100 text-indigo-700' };
const getExt    = n => '.' + n.split('.').pop().toLowerCase();
const fmtSize   = b => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(1)} KB`;
const STATUS_ST = {
  completed:  { badge:'bg-emerald-50 text-emerald-700', dot:'bg-emerald-500',             label:'Done'      },
  processing: { badge:'bg-blue-50 text-blue-700',       dot:'bg-blue-500 animate-pulse',  label:'Analyzing' },
  failed:     { badge:'bg-red-50 text-red-600',         dot:'bg-red-500',                 label:'Failed'    },
  pending:    { badge:'bg-[#F7F3EE] text-[#6B6560]',   dot:'bg-[#A8A29E]',              label:'Pending'   },
};

function ScoreBar({ label, value, color }) {
  return (
    <div>
      <div className="flex justify-between text-xs mb-1.5">
        <span className="text-[#6B6560]">{label}</span>
        <span className="font-bold text-[#1A1714]">{pct(value)}</span>
      </div>
      <div className="h-2 bg-[#F0EBE3] rounded-full overflow-hidden">
        <div className={`h-full rounded-full ${color}`} style={{ width: pct(value) }} />
      </div>
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
      <div className="bg-white border-b border-[#E8E1D8] sticky top-16 z-40 pt-0">
        <div className="max-w-5xl mx-auto px-6 py-5">
          <Link to={`/assignments/${submission.assignment_id}`}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-4 transition-colors">
            ← {submission.assignment_title}
          </Link>
          <div className="flex items-start justify-between gap-3">
            <div>
              <h1 className="text-xl font-bold text-[#1A1714]">Submission Details</h1>
              <p className="text-xs text-[#A8A29E] mt-1">{submission.student_name} · {submission.course_code} · {new Date(submission.submitted_at).toLocaleString()}</p>
            </div>
            <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[11px] font-semibold ${S.badge}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${S.dot}`} />{S.label}
            </span>
          </div>
          {status === 'processing' && (
            <div className="mt-4 flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-50 border border-blue-200">
              <span className="w-3.5 h-3.5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin flex-shrink-0" />
              <p className="text-sm text-blue-800 font-medium">Analysis is running — page will update automatically.</p>
            </div>
          )}
        </div>
      </div>

      <div className="max-w-5xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-5">

            {/* Files */}
            <div className="bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden">
              <div className="px-6 py-4 border-b border-[#F0EBE3]">
                <h2 className="text-sm font-bold text-[#1A1714]">Submitted Files ({submission.files?.length || 0})</h2>
              </div>
              <div className="p-4 space-y-2">
                {!submission.files?.length
                  ? <p className="text-sm text-[#A8A29E] text-center py-6">No files found.</p>
                  : submission.files.map((file, i) => {
                    const lang = EXT_LANG[getExt(file.filename)];
                    return (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-[#F7F3EE]">
                        <svg width="18" height="18" fill="none" stroke="#CF7249" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M13 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V9z"/><polyline points="13 2 13 9 20 9"/></svg>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-[#1A1714] truncate">{file.filename}</p>
                          <div className="flex items-center gap-2 mt-0.5">
                            <span className="text-xs text-[#A8A29E]">{fmtSize(file.file_size)}</span>
                            {lang && <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${LANG_CLR[lang]||'bg-gray-100 text-gray-600'}`}>{lang}</span>}
                          </div>
                        </div>
                      </div>
                    );
                  })
                }
              </div>
            </div>

            {/* Analysis */}
            {status === 'completed' && analysis && (
              <div className="bg-white rounded-2xl border border-[#E8E1D8] overflow-hidden">
                <div className="px-6 py-4 border-b border-[#F0EBE3] flex items-center justify-between">
                  <h2 className="text-sm font-bold text-[#1A1714]">Analysis Results</h2>
                  {isInstructor && <Link to={`/analysis/assignment/${submission.assignment_id}`} className="text-xs font-bold text-[#CF7249] hover:underline">Full Report →</Link>}
                </div>
                <div className="p-6 space-y-6">
                  <div className="flex items-center gap-5 p-5 bg-[#F7F3EE] rounded-2xl">
                    <div className={`text-4xl font-bold ${riskClr}`}>{overallPct}%</div>
                    <div className="flex-1">
                      <div className="h-3 bg-[#E8E1D8] rounded-full overflow-hidden mb-2">
                        <div className={`h-full rounded-full ${barClr}`} style={{ width: `${overallPct}%` }} />
                      </div>
                      <p className="text-xs text-[#6B6560] font-medium">
                        {overallPct >= 85 ? 'High similarity — review recommended' : overallPct >= 70 ? 'Moderate similarity' : 'Low similarity — looks original'}
                      </p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <ScoreBar label="Type-1 (Exact)"      value={analysis.type1_score} color="bg-blue-400"   />
                    <ScoreBar label="Type-2 (Renamed)"    value={analysis.type2_score} color="bg-violet-400" />
                    <ScoreBar label="Type-3 (Structural)" value={analysis.type3_score} color="bg-[#CF7249]"  />
                    <ScoreBar label="Type-4 (Semantic)"   value={analysis.type4_score} color="bg-[#8B9BB4]"  />
                  </div>
                  {analysis.clonePairs?.length > 0 && (
                    <div>
                      <h3 className="text-sm font-bold text-[#1A1714] mb-3">Similar Submissions ({analysis.clonePairs.length})</h3>
                      <div className="space-y-2">
                        {analysis.clonePairs.map((pair, i) => {
                          const s  = Math.round(norm(pair.similarity) * 100);
                          const rc = s>=85 ? 'bg-[#FAEDEC] border-[#E8B5B0] text-[#C4827A]' : s>=70 ? 'bg-[#FEF3EC] border-[#F4C9AA] text-[#CF7249]' : 'bg-[#F7F3EE] border-[#E8E1D8] text-[#6B6560]';
                          return (
                            <div key={i} className={`flex items-center justify-between px-4 py-3 rounded-xl border ${rc}`}>
                              <div>
                                <p className="text-sm font-bold">{pair.student_b_name || `Submission #${pair.submission_b_id}`}</p>
                                <p className="text-xs opacity-70 mt-0.5">{pair.clone_type} clone</p>
                              </div>
                              <span className="text-base font-bold">{s}%</span>
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
              <div className="bg-white rounded-2xl border border-red-200 p-6">
                <p className="text-sm font-bold text-red-700 mb-1">Analysis Failed</p>
                <p className="text-xs text-red-600">The analysis engine could not process this submission.</p>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-4">
            <div className="bg-white rounded-2xl border border-[#E8E1D8] p-5">
              <h3 className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Info</h3>
              <div className="space-y-3">
                {[['Student',submission.student_name],['Course',`${submission.course_code} — ${submission.course_name}`],['Submitted',new Date(submission.submitted_at).toLocaleDateString()],['Files',submission.files?.length||0]].map(([label,value])=>(
                  <div key={label}>
                    <p className="text-[10px] font-bold text-[#A8A29E] uppercase tracking-wider">{label}</p>
                    <p className="text-sm font-semibold text-[#1A1714] mt-0.5">{value}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="bg-white rounded-2xl border border-[#E8E1D8] p-5 space-y-2">
              <Link to={`/assignments/${submission.assignment_id}`} className="block w-full text-center py-2 rounded-xl border border-[#E8E1D8] text-xs font-bold text-[#1A1714] hover:bg-[#F7F3EE] transition-colors">
                View Assignment
              </Link>
              {isInstructor && (
                <Link to={`/analysis/assignment/${submission.assignment_id}`} className="block w-full text-center py-2 rounded-xl bg-[#CF7249] text-white text-xs font-bold hover:bg-[#B85E38] transition-colors">
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
