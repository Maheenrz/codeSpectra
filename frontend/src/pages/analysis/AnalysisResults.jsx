// frontend/src/pages/analysis/AnalysisResults.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import analysisService from '../../services/analysisService';

const norm   = (v) => v == null ? 0 : v > 1 ? v / 100 : v;
const pctFmt = (v) => `${Math.round(norm(v) * 100)}%`;

const RISK = {
  CRITICAL: { label:'Critical', bg:'bg-red-100',          text:'text-red-700',    bar:'bg-red-500',    dot:'bg-red-500',    ring:'border-red-200'    },
  HIGH:     { label:'High',     bg:'bg-[#FEF3EC]',        text:'text-[#CF7249]',  bar:'bg-[#CF7249]',  dot:'bg-[#CF7249]',  ring:'border-[#F4C9AA]'  },
  MEDIUM:   { label:'Medium',   bg:'bg-amber-50',         text:'text-amber-700',  bar:'bg-amber-400',  dot:'bg-amber-400',  ring:'border-amber-200'  },
  LOW:      { label:'Low',      bg:'bg-blue-50',          text:'text-blue-700',   bar:'bg-blue-400',   dot:'bg-blue-400',   ring:'border-blue-200'   },
  NONE:     { label:'Clean',    bg:'bg-[#F7F3EE]',        text:'text-[#6B6560]',  bar:'bg-[#D4CEC8]',  dot:'bg-[#D4CEC8]',  ring:'border-[#E8E1D8]'  },
};

function getRisk(raw) {
  const s = norm(raw);
  if (s >= 0.85) return 'CRITICAL';
  if (s >= 0.70) return 'HIGH';
  if (s >= 0.50) return 'MEDIUM';
  if (s >= 0.30) return 'LOW';
  return 'NONE';
}

function parseBlocks(raw) {
  try {
    const p = typeof raw === 'string' ? JSON.parse(raw) : raw;
    if (!p) return { meta:{}, fragments:[] };
    if (Array.isArray(p)) return { meta:{}, fragments:p };
    if (p.fragments) return { meta:p, fragments:p.fragments };
    return { meta:p, fragments:[] };
  } catch { return { meta:{}, fragments:[] }; }
}

/* ── SVG icons ── */
const Ico = {
  ArrowLeft: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M19 12H5M12 5l-7 7 7 7"/>
    </svg>
  ),
  Shield: () => (
    <svg width="17" height="17" fill="none" stroke="#CF7249" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  ),
  Play: () => (
    <svg width="14" height="14" fill="currentColor" viewBox="0 0 24 24"><polygon points="5 3 19 12 5 21 5 3"/></svg>
  ),
  Download: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/>
      <polyline points="7 10 12 15 17 10"/>
      <line x1="12" y1="15" x2="12" y2="3"/>
    </svg>
  ),
  ChevronDown: () => (
    <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="6 9 12 15 18 9"/>
    </svg>
  ),
  ExternalLink: () => (
    <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
  ),
  AlertBell: () => (
    <svg width="18" height="18" fill="none" stroke="#DC2626" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
      <path d="M13.73 21a2 2 0 01-3.46 0"/>
    </svg>
  ),
  Filter: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
    </svg>
  ),
  BarChart: () => (
    <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <line x1="18" y1="20" x2="18" y2="10"/>
      <line x1="12" y1="20" x2="12" y2="4"/>
      <line x1="6" y1="20" x2="6" y2="14"/>
    </svg>
  ),
  Users: () => (
    <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/>
      <circle cx="9" cy="7" r="4"/>
      <path d="M23 21v-2a4 4 0 00-3-3.87"/>
      <path d="M16 3.13a4 4 0 010 7.75"/>
    </svg>
  ),
};

/* ── Stat block ── */
const Stat = ({ label, value, sub, accent }) => (
  <div className="bg-white rounded-3xl border border-[#E8E1D8] px-6 py-6 shadow-sm">
    <p className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E] mb-3">{label}</p>
    <p className={`text-4xl font-black tracking-tight ${accent || 'text-[#1A1714]'}`}>{value}</p>
    {sub && <p className="text-xs text-[#A8A29E] mt-2">{sub}</p>}
  </div>
);

/* ── Risk badge ── */
const RiskBadge = ({ score }) => {
  const R = RISK[getRisk(score)];
  return (
    <span className={`inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full ${R.bg} ${R.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${R.dot}`} />
      {R.label}
    </span>
  );
};

/* ── Score bar ── */
const ScoreBar = ({ label, val, color }) => (
  <div className="flex items-center gap-3">
    <span className="text-xs text-[#6B6560] w-20 flex-shrink-0">{label}</span>
    <div className="flex-1 h-2 bg-[#F0EBE3] rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.round(norm(val) * 100)}%` }} />
    </div>
    <span className="text-xs font-black text-[#1A1714] w-10 text-right">{Math.round(norm(val) * 100)}%</span>
  </div>
);

/* ── Pair card ── */
const PairCard = ({ pair, rank }) => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  const score  = norm(pair.similarity ?? pair.combined_score ?? 0);
  const R      = RISK[getRisk(score)];
  const pctVal = Math.round(score * 100);
  const { meta, fragments } = parseBlocks(pair.matching_blocks);
  const t1 = norm(pair.type1_score ?? meta.type1_score ?? 0);
  const t2 = norm(pair.type2_score ?? meta.type2_score ?? 0);
  const t3 = norm(pair.type3_score ?? pair.structural_score ?? meta.structural_score ?? 0);
  const t4 = norm(pair.type4_score ?? pair.semantic_score   ?? meta.semantic_score   ?? 0);
  const nameA = pair.student_a_name || meta.student_a_name || 'Student A';
  const nameB = pair.student_b_name || meta.student_b_name || 'Student B';
  const fileA = pair.file_a || meta.file_a;
  const fileB = pair.file_b || meta.file_b;
  const ioMatchScore   = pair.io_match_score ?? meta.io_match_score ?? null;
  const ioAvailable    = pair.io_available   ?? meta.io_available   ?? false;
  const interpretation = pair.interpretation ?? meta.interpretation ?? '';

  return (
    <div className={`rounded-3xl border overflow-hidden transition-all duration-200 ${open ? 'border-[#CF7249]/30 shadow-md' : 'border-[#E8E1D8] bg-white hover:border-[#CF7249]/20 hover:shadow-sm'}`}>
      <button onClick={() => setOpen(o => !o)} className="w-full text-left px-7 py-6 bg-white flex items-center gap-5">
        <span className="text-xs font-black text-[#D4CEC8] w-6 flex-shrink-0">#{rank}</span>

        {/* Score circle */}
        <div className={`w-14 h-14 rounded-2xl flex-shrink-0 flex items-center justify-center font-black text-sm border ${R.bg} ${R.text} ${R.ring}`}>
          {pctVal}%
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-2">
            <span className="font-black text-[#1A1714] text-sm">{nameA}</span>
            <span className="text-[#D4CEC8] text-xs">↔</span>
            <span className="font-black text-[#1A1714] text-sm">{nameB}</span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <RiskBadge score={score} />
            {pair.clone_type && (
              <span className="text-[10px] font-black px-2 py-0.5 rounded-lg bg-[#F0EBE3] text-[#6B6560] capitalize">{pair.clone_type}</span>
            )}
            {fileA && <span className="text-[10px] text-[#A8A29E] font-mono">{fileA.split('/').pop()}</span>}
          </div>
        </div>

        {/* Mini score bars */}
        <div className="hidden md:flex flex-col gap-2 min-w-[160px]">
          {[['Structural', t3, 'bg-violet-400'], ['Semantic', t4, 'bg-[#CF7249]']].map(([l, v, c]) => (
            <div key={l} className="flex items-center gap-2 text-[10px] text-[#A8A29E]">
              <span className="w-16 text-right">{l}</span>
              <div className="flex-1 h-1.5 bg-[#F0EBE3] rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${c}`} style={{ width: `${Math.round(v * 100)}%` }} />
              </div>
              <span className="text-[#6B6560] font-black w-8 text-right">{Math.round(v * 100)}%</span>
            </div>
          ))}
        </div>

        <div className={`text-[#A8A29E] flex-shrink-0 transition-transform duration-200 ${open ? 'rotate-180' : ''}`}>
          <Ico.ChevronDown />
        </div>
      </button>

      {open && (
        <div className="border-t border-[#F0EBE3] bg-[#F7F3EE]/60 px-7 pb-7 pt-5 space-y-5">
          {/* 4-type grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label:'Type-1', sub:'Exact copy',   val:t1, color:'bg-blue-500'   },
              { label:'Type-2', sub:'Renamed vars', val:t2, color:'bg-violet-500' },
              { label:'Type-3', sub:'Structural',   val:t3, color:'bg-amber-500'  },
              { label:'Type-4', sub:'Semantic',     val:t4, color:'bg-[#CF7249]'  },
            ].map(({ label, sub, val, color }) => (
              <div key={label} className="bg-white rounded-2xl border border-[#E8E1D8] px-4 py-4">
                <p className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E] mb-0.5">{label}</p>
                <p className="text-[10px] text-[#A8A29E] mb-3">{sub}</p>
                <div className="h-2 bg-[#F0EBE3] rounded-full overflow-hidden mb-2">
                  <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.round(val * 100)}%` }} />
                </div>
                <p className="text-2xl font-black text-[#1A1714]">{Math.round(val * 100)}%</p>
              </div>
            ))}
          </div>

          {/* Type-4 detail */}
          {t4 > 0 && (
            <div className="bg-white border border-[#E8E1D8] rounded-2xl px-5 py-4">
              <p className="text-[9px] font-black uppercase tracking-widest text-[#8B9BB4] mb-3">Type-4 — Educational Semantic Analysis</p>
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold text-[#A8A29E]">I/O Match:</span>
                  {ioAvailable && ioMatchScore !== null
                    ? <span className={`text-xs font-black ${ioMatchScore >= 0.9 ? 'text-[#CF7249]' : ioMatchScore >= 0.7 ? 'text-[#C4827A]' : 'text-[#8B9BB4]'}`}>{Math.round(ioMatchScore * 100)}%</span>
                    : <span className="text-[10px] text-[#A8A29E] italic">unavailable</span>}
                </div>
                {interpretation && <span className="text-[10px] text-[#6B6560] flex-1 min-w-0 truncate">{interpretation}</span>}
              </div>
            </div>
          )}

          {/* File details */}
          {(fileA || fileB) && (
            <div className="grid grid-cols-2 gap-3">
              {[[fileA, nameA, pair.submission_a_id, 'A'], [fileB, nameB, pair.submission_b_id, 'B']].map(([file, name, subId, label]) => (
                <div key={label} className="bg-white border border-[#E8E1D8] rounded-2xl px-4 py-4">
                  <p className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E] mb-2">Student {label}</p>
                  <p className="text-sm font-bold text-[#1A1714]">{name}</p>
                  {file && <p className="text-[10px] font-mono text-[#A8A29E] truncate mt-0.5">{file.split('/').pop()}</p>}
                  {subId && (
                    <Link to={`/submissions/${subId}`} className="inline-flex items-center gap-1 text-xs text-[#CF7249] hover:text-[#B85E38] font-black mt-2 transition-colors">
                      View submission <Ico.ExternalLink />
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 flex-wrap pt-1">
            {pair.submission_a_id && (
              <Link to={`/submissions/${pair.submission_a_id}`} className="px-4 py-2.5 rounded-xl text-xs font-black border border-[#E8E1D8] bg-white text-[#6B6560] hover:bg-[#F7F3EE] transition-colors">
                Open Submission A
              </Link>
            )}
            {pair.submission_b_id && (
              <Link to={`/submissions/${pair.submission_b_id}`} className="px-4 py-2.5 rounded-xl text-xs font-black border border-[#E8E1D8] bg-white text-[#6B6560] hover:bg-[#F7F3EE] transition-colors">
                Open Submission B
              </Link>
            )}
            <button
              onClick={() => navigate(`/analysis/pair/${pair.pair_id}`, { state:{ pair } })}
              className="ml-auto px-5 py-2.5 rounded-xl text-xs font-black bg-[#CF7249] text-white hover:bg-[#B85E38] transition-colors shadow-sm"
            >
              Full Comparison →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

/* ── Main page ── */
const AnalysisResults = () => {
  const { assignmentId } = useParams();
  const [results,    setResults]    = useState(null);
  const [threshold,  setThreshold]  = useState(0.5);
  const [loading,    setLoading]    = useState(true);
  const [filter,     setFilter]     = useState('all');
  const [sort,       setSort]       = useState('score');
  const [running,    setRunning]    = useState(false);
  const [csvLoading, setCsvLoading] = useState(false);
  const runningRef = useRef(false);

  useEffect(() => { fetchResults(); }, [assignmentId, threshold]);

  const fetchResults = async () => {
    setLoading(true);
    try { const data = await analysisService.getAssignmentResults(assignmentId, threshold * 100); setResults(data); }
    catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const triggerAnalysis = useCallback(async () => {
    if (runningRef.current) return;
    runningRef.current = true; setRunning(true);
    try {
      await analysisService.analyzeAssignment(assignmentId);
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        const data = await analysisService.getAssignmentResults(assignmentId, threshold * 100);
        if ((data?.highSimilarityPairs?.length > 0) || attempts > 30) {
          clearInterval(poll); setResults(data); setRunning(false); runningRef.current = false;
        }
      }, 4000);
    } catch (e) { console.error(e); setRunning(false); runningRef.current = false; }
  }, [assignmentId, threshold]);

  const downloadCsv = (mode = 'summary') => {
    if (csvLoading) return;
    setCsvLoading(true);
    try {
      const pairs = results?.highSimilarityPairs || [];
      if (!pairs.length) { alert('No results to export. Run analysis first.'); return; }
      const RECS = { CRITICAL:'Exact duplicate — flag immediately.', HIGH:'Strong similarity — schedule review.', MEDIUM:'Moderate similarity — add to queue.', LOW:'Monitor.', NONE:'No action.' };
      const header = mode === 'summary'
        ? ['Student File 1','Student File 2','Plagiarism Match (%)','Clone Type','Risk Level','Student A','Student B','Recommendation']
        : ['rank','student_a','student_b','clone_type','similarity_pct','type1_pct','type2_pct','type3_pct','confidence','risk_level','file_a','file_b','needs_review','recommendation'];
      const rows = [...pairs].sort((a,b) => norm(b.similarity??0) - norm(a.similarity??0)).map((p,i) => {
        const s = norm(p.similarity??0);
        const risk = s>=0.85?'CRITICAL':s>=0.70?'HIGH':s>=0.50?'MEDIUM':s>=0.30?'LOW':'NONE';
        const mb = (() => { try { return typeof p.matching_blocks==='string'?JSON.parse(p.matching_blocks):(p.matching_blocks||{}); } catch { return {}; } })();
        const row = mode === 'summary'
          ? [mb.file_a?mb.file_a.split('/').pop():'', mb.file_b?mb.file_b.split('/').pop():'', `${Math.round(s*100)}%`, p.clone_type||mb.primary_clone_type||'', risk, p.student_a_name||'', p.student_b_name||'', RECS[risk]||'']
          : [i+1,p.student_a_name||'',p.student_b_name||'',p.clone_type||mb.primary_clone_type||'',Math.round(s*100),Math.round(norm(p.type1_score??mb.type1_score??0)*100),Math.round(norm(p.type2_score??mb.type2_score??0)*100),Math.round(norm(p.type3_score??p.structural_score??mb.structural_score??0)*100),mb.confidence||'',risk,mb.file_a?mb.file_a.split('/').pop():'',mb.file_b?mb.file_b.split('/').pop():'',(p.needs_review||s>=0.70)?'YES':'NO',RECS[risk]||''];
        return row.map(v => `"${String(v).replace(/"/g,'""')}"`).join(',');
      });
      const csv = [header.join(','),...rows].join('\n');
      const blob = new Blob([csv], { type:'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a'); a.href=url; a.download=`codespectra_${mode}_${assignmentId}_${Date.now()}.csv`;
      document.body.appendChild(a); a.click(); a.remove(); URL.revokeObjectURL(url);
    } catch (err) { console.error('CSV export failed:', err); }
    finally { setCsvLoading(false); }
  };

  const rawPairs      = results?.highSimilarityPairs || [];
  const criticalCount = rawPairs.filter(p => getRisk(p.similarity) === 'CRITICAL').length;
  const highCount     = rawPairs.filter(p => getRisk(p.similarity) === 'HIGH').length;
  const avgScore      = rawPairs.length ? rawPairs.reduce((s,p) => s + norm(p.similarity??0), 0) / rawPairs.length : 0;
  const assignmentSettings = results?.assignment_settings || null;

  const filtered = rawPairs.filter(p => {
    const s = norm(p.similarity ?? p.combined_score ?? 0);
    if (filter === 'high')   return s >= 0.70;
    if (filter === 'medium') return s >= 0.50 && s < 0.70;
    if (filter === 'low')    return s < 0.50;
    return true;
  });
  const sorted = [...filtered].sort((a,b) => sort === 'name' ? (a.student_a_name||'').localeCompare(b.student_a_name||'') : norm(b.similarity??0) - norm(a.similarity??0));

  return (
    <div className="min-h-screen">

      {/* ── Sticky action bar ── */}
      <div className="bg-white/90 backdrop-blur-sm border-b border-[#E8E1D8] sticky top-16 z-40">
        <div className="max-w-6xl mx-auto px-6 py-3.5 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <Link to={`/assignments/${assignmentId}`} className="inline-flex items-center gap-2 text-xs font-semibold text-[#A8A29E] hover:text-[#CF7249] transition-colors">
              <Ico.ArrowLeft /> Assignment
            </Link>
            <span className="text-[#D4CEC8]">|</span>
            <span className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E]">Plagiarism Report</span>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {results?.highSimilarityPairs?.length > 0 && (
              <div className="flex items-stretch rounded-xl overflow-hidden border border-[#E8E1D8]">
                <button onClick={() => downloadCsv('summary')} disabled={csvLoading}
                  className="flex items-center gap-1.5 px-3 py-2 bg-white text-[#6B6560] text-xs font-black hover:bg-[#F7F3EE] disabled:opacity-50 transition-all border-r border-[#E8E1D8]">
                  <Ico.Download /> Summary
                </button>
                <button onClick={() => downloadCsv('technical')} disabled={csvLoading}
                  className="flex items-center gap-1.5 px-3 py-2 bg-white text-[#6B6560] text-xs font-black hover:bg-[#F7F3EE] disabled:opacity-50 transition-all">
                  Technical
                </button>
              </div>
            )}
            <button onClick={triggerAnalysis} disabled={running}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#CF7249] text-white text-xs font-black hover:bg-[#B85E38] disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-sm">
              {running
                ? <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Analyzing…</>
                : <><Ico.Play /> Re-run Analysis</>}
            </button>
          </div>
        </div>
      </div>


      <div className="max-w-6xl mx-auto px-6 py-12 space-y-8 pt-16">
        {/* ── Prominent heading ── */}
        <div className="mb-6">
          <h1 className="text-6xl font-extrabold text-[#CF7249] tracking-tight leading-tight mb-2">Similarity Report</h1>
          <p className="text-base text-[#A8A29E]">
            {rawPairs.length} pairs found · showing {sorted.length} above {Math.round(threshold * 100)}% threshold
          </p>
        </div>
        <div className="border-t-2 border-[#E8E1D8] mb-8" />
        {/* ── Stat cards ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-6">
          <Stat label="Total pairs"    value={rawPairs.length} />
          <Stat label="Critical ≥85%"  value={criticalCount} accent={criticalCount > 0 ? 'text-red-600' : 'text-[#D4CEC8]'} />
          <Stat label="High 70–85%"    value={highCount}     accent={highCount > 0 ? 'text-[#CF7249]' : 'text-[#D4CEC8]'} />
          <Stat label="Avg similarity" value={`${Math.round(avgScore * 100)}%`} />
        </div>
        <div className="border-t border-[#E8E1D8] mb-4" />

        {/* ── Active detectors ── */}
        {assignmentSettings && (
          <div className="flex flex-wrap items-center gap-2 px-5 py-4 rounded-2xl bg-white border border-[#E8E1D8] shadow-sm">
            <span className="text-xs font-black text-[#6B6560] mr-1">Active detectors:</span>
            {[
              { key:'type1', label:'Type-1 Exact',        color:'#CF7249', bg:'#FEF3EC' },
              { key:'type2', label:'Type-2 Renamed',       color:'#2D6A6A', bg:'#EBF4F4' },
              { key:'type3', label:'Type-3 Near-Miss',     color:'#C4827A', bg:'#FAEDEC' },
              { key:'type4', label:'Type-4 Semantic/I/O',  color:'#8B9BB4', bg:'#EFF2F7' },
            ].map(({ key, label, color, bg }) => (
              <span key={key} style={{
                fontSize:10, fontWeight:800, padding:'3px 10px', borderRadius:8,
                background: assignmentSettings[key] ? bg : '#F0EBE3',
                color: assignmentSettings[key] ? color : '#A8A29E',
                textDecoration: assignmentSettings[key] ? 'none' : 'line-through',
                opacity: assignmentSettings[key] ? 1 : 0.6,
              }}>{label}</span>
            ))}
          </div>
        )}

        {/* ── Critical alert ── */}
        {criticalCount > 0 && (
          <div className="flex items-start gap-4 px-6 py-5 rounded-2xl bg-red-50 border border-red-200">
            <span className="flex-shrink-0 mt-0.5"><Ico.AlertBell /></span>
            <p className="text-sm text-red-800 font-semibold">
              <strong>{criticalCount} pair{criticalCount !== 1 ? 's' : ''}</strong> with ≥85% similarity detected — immediate review recommended.
            </p>
          </div>
        )}

        {/* ── Controls ── */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-3 bg-white border border-[#E8E1D8] rounded-2xl px-5 py-3 shadow-sm">
            <Ico.Filter />
            <span className="text-xs font-black text-[#6B6560] flex-shrink-0">Min similarity</span>
            <input type="range" min="0" max="1" step="0.05" value={threshold}
              onChange={e => setThreshold(parseFloat(e.target.value))}
              className="w-28" style={{ accentColor:'#CF7249' }} />
            <span className="text-sm font-black text-[#CF7249] w-12">{Math.round(threshold * 100)}%</span>
          </div>

          <div className="flex gap-1.5">
            {['all','high','medium','low'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-3.5 py-2 rounded-xl text-xs font-black capitalize transition-all
                  ${filter === f ? 'bg-[#CF7249] text-white shadow-sm' : 'bg-white border border-[#E8E1D8] text-[#6B6560] hover:border-[#CF7249]/30'}`}>
                {f}
              </button>
            ))}
          </div>

          <div className="ml-auto flex items-center gap-1.5">
            <Ico.BarChart />
            {[['score','By score'],['name','By name']].map(([v,l]) => (
              <button key={v} onClick={() => setSort(v)}
                className={`px-3.5 py-2 rounded-xl text-xs font-black transition-all
                  ${sort === v ? 'bg-[#F0EBE3] text-[#CF7249]' : 'text-[#A8A29E] hover:text-[#6B6560]'}`}>
                {l}
              </button>
            ))}
          </div>
        </div>

        {/* ── Results ── */}
        {loading ? (
          <div className="flex items-center justify-center py-24 gap-3">
            <span className="w-6 h-6 border-2 border-[#CF7249] border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-[#6B6560] font-medium">Loading results…</span>
          </div>
        ) : rawPairs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-28 text-center bg-white rounded-3xl border border-[#E8E1D8]">
            <div className="w-16 h-16 rounded-2xl bg-[#FEF3EC] flex items-center justify-center mb-5">
              <Ico.Shield />
            </div>
            <p className="font-black text-[#1A1714] text-xl mb-2">No results yet</p>
            <p className="text-sm text-[#A8A29E] mb-7 max-w-xs leading-relaxed">Click Run Analysis to start plagiarism detection across all submissions.</p>
            <button onClick={triggerAnalysis} disabled={running}
              className="px-7 py-3.5 rounded-2xl bg-[#CF7249] text-white text-sm font-black hover:bg-[#B85E38] disabled:opacity-50 shadow-sm transition-colors">
              {running ? 'Analyzing…' : 'Run Analysis Now'}
            </button>
          </div>
        ) : sorted.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-24 text-center bg-white rounded-3xl border border-[#E8E1D8]">
            <p className="font-black text-[#1A1714] text-xl mb-2">No pairs above {Math.round(threshold * 100)}%</p>
            <p className="text-sm text-[#A8A29E]">Lower the threshold or change the filter.</p>
          </div>
        ) : (
          <div className="space-y-3">
            {sorted.map((pair, i) => <PairCard key={pair.pair_id || i} pair={pair} rank={i + 1} />)}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisResults;
