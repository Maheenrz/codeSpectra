// frontend/src/pages/analysis/AnalysisResults.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import analysisService from '../../services/analysisService';
import api from '../../utils/api';

// DB stores similarity as 0-100. Normalise everywhere to 0-1.
const norm   = (v) => v == null ? 0 : v > 1 ? v / 100 : v;
const pctFmt = (v) => `${Math.round(norm(v) * 100)}%`;

const RISK = {
  CRITICAL: { label:'Critical', bg:'bg-red-100',    text:'text-red-700',    bar:'bg-red-500',    dot:'bg-red-500'    },
  HIGH:     { label:'High',     bg:'bg-orange-100', text:'text-orange-700', bar:'bg-orange-400', dot:'bg-orange-400' },
  MEDIUM:   { label:'Medium',   bg:'bg-amber-100',  text:'text-amber-700',  bar:'bg-amber-400',  dot:'bg-amber-400'  },
  LOW:      { label:'Low',      bg:'bg-blue-100',   text:'text-blue-700',   bar:'bg-blue-400',   dot:'bg-blue-400'   },
  NONE:     { label:'Clean',    bg:'bg-gray-100',   text:'text-gray-500',   bar:'bg-gray-300',   dot:'bg-gray-300'   },
};

function getRisk(rawScore) {
  const s = norm(rawScore);
  if (s >= 0.85) return 'CRITICAL';
  if (s >= 0.70) return 'HIGH';
  if (s >= 0.50) return 'MEDIUM';
  if (s >= 0.30) return 'LOW';
  return 'NONE';
}

function parseBlocks(raw) {
  try {
    const p = typeof raw === 'string' ? JSON.parse(raw) : raw;
    if (!p) return { meta: {}, fragments: [] };
    if (Array.isArray(p)) return { meta: {}, fragments: p };
    if (p.fragments) return { meta: p, fragments: p.fragments };
    return { meta: p, fragments: [] };
  } catch { return { meta: {}, fragments: [] }; }
}

const RiskBadge = ({ score }) => {
  const R = RISK[getRisk(score)];
  return (
    <span className={`inline-flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest px-2.5 py-1 rounded-full ${R.bg} ${R.text}`}>
      <span className={`w-1.5 h-1.5 rounded-full ${R.dot}`} />
      {R.label}
    </span>
  );
};

const Stat = ({ label, value, sub, accent }) => (
  <div className="bg-white rounded-2xl border border-gray-100 px-6 py-5">
    <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">{label}</p>
    <p className={`text-3xl font-black tracking-tight ${accent || 'text-gray-900'}`}>{value}</p>
    {sub && <p className="text-xs text-gray-500 mt-1">{sub}</p>}
  </div>
);

// ─── Pair card ────────────────────────────────────────────────────────────────
const PairCard = ({ pair, rank }) => {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const score  = norm(pair.similarity ?? pair.combined_score ?? 0);
  const R      = RISK[getRisk(score)];
  const pctVal = Math.round(score * 100);
  const { meta, fragments } = parseBlocks(pair.matching_blocks);

  const t1 = norm(pair.type1_score      ?? meta.type1_score      ?? 0);
  const t2 = norm(pair.type2_score      ?? meta.type2_score      ?? 0);
  const t3 = norm(pair.type3_score      ?? pair.structural_score ?? meta.structural_score ?? 0);
  const t4 = norm(pair.type4_score      ?? pair.semantic_score   ?? meta.semantic_score   ?? 0);

  // Type-4 enrichment (from educational detector)
  const ioMatchScore   = pair.io_match_score   ?? meta.io_match_score   ?? null;
  const ioAvailable    = pair.io_available     ?? meta.io_available     ?? false;
  const interpretation = pair.interpretation   ?? meta.interpretation   ?? '';

  const nameA = pair.student_a_name || meta.student_a_name || 'Student A';
  const nameB = pair.student_b_name || meta.student_b_name || 'Student B';
  const fileA = pair.file_a || meta.file_a;
  const fileB = pair.file_b || meta.file_b;

  return (
    <div className={`rounded-2xl border overflow-hidden transition-all
      ${open ? 'border-slate-300 shadow-md' : 'border-gray-100 hover:border-gray-300 hover:shadow-sm'}`}>

      <button onClick={() => setOpen(o => !o)}
        className="w-full text-left px-6 py-5 bg-white flex items-center gap-4">
        <span className="text-xs font-black text-gray-300 w-6 flex-shrink-0">#{rank}</span>

        <div className={`w-14 h-14 rounded-full flex-shrink-0 flex items-center justify-center font-black text-sm ${R.bg} ${R.text}`}>
          {pctVal}%
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-bold text-gray-900 text-sm">{nameA}</span>
            <span className="text-gray-300 text-xs">↔</span>
            <span className="font-bold text-gray-900 text-sm">{nameB}</span>
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <RiskBadge score={score} />
            {pair.clone_type && (
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-md bg-slate-100 text-slate-600">
                {pair.clone_type}
              </span>
            )}
            {fileA && <span className="text-[10px] text-gray-400 font-mono">{fileA.split('/').pop()}</span>}
          </div>
        </div>

        <div className="hidden md:flex flex-col gap-1 min-w-[150px]">
          {[['Structural', t3, 'bg-violet-400'], ['Semantic', t4, 'bg-rose-400']].map(([l, v, c]) => (
            <div key={l} className="flex items-center gap-2 text-[10px] text-gray-400">
              <span className="w-16 text-right">{l}</span>
              <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                <div className={`h-full rounded-full ${c}`} style={{ width: `${Math.round(v * 100)}%` }} />
              </div>
              <span className="text-gray-600 font-semibold w-8 text-right">{Math.round(v * 100)}%</span>
            </div>
          ))}
        </div>

        <svg className={`w-5 h-5 text-gray-400 flex-shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {open && (
        <div className="border-t border-gray-100 bg-gray-50/50 px-6 pb-6 pt-4 space-y-5">
          {/* 4-type breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label:'Type-1', sub:'Exact copy',   val:t1, color:'bg-blue-500'   },
              { label:'Type-2', sub:'Renamed vars', val:t2, color:'bg-violet-500' },
              { label:'Type-3', sub:'Structural',   val:t3, color:'bg-amber-500'  },
              { label:'Type-4', sub:'Semantic',     val:t4, color:'bg-rose-500'   },
            ].map(({ label, sub, val, color }) => (
              <div key={label} className="bg-white rounded-xl border border-gray-100 px-4 py-3">
                <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-0.5">{label}</p>
                <p className="text-[10px] text-gray-400 mb-2">{sub}</p>
                <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-1.5">
                  <div className={`h-full rounded-full ${color}`} style={{ width: `${Math.round(val * 100)}%` }} />
                </div>
                <p className="text-lg font-black text-gray-900">{Math.round(val * 100)}%</p>
              </div>
            ))}
          </div>

          {/* Type-4 I/O behavioral detail */}
          {t4 > 0 && (
            <div className="bg-white border border-gray-100 rounded-xl px-4 py-3 mb-3">
              <p className="text-[9px] font-black uppercase tracking-widest text-[#8B9BB4] mb-2">Type-4 — Educational Semantic Analysis</p>
              <div className="flex flex-wrap items-center gap-4">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-semibold text-gray-500">I/O Match:</span>
                  {ioAvailable && ioMatchScore !== null ? (
                    <span className={`text-xs font-black ${
                      ioMatchScore >= 0.9 ? 'text-[#CF7249]'
                      : ioMatchScore >= 0.7 ? 'text-[#C4827A]'
                      : 'text-[#8B9BB4]'
                    }`}>{Math.round(ioMatchScore * 100)}%</span>
                  ) : (
                    <span className="text-[10px] text-gray-400 italic">unavailable</span>
                  )}
                </div>
                {interpretation && (
                  <span className="text-[10px] text-gray-500 flex-1 min-w-0 truncate" title={interpretation}>
                    {interpretation}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Files */}
          {(fileA || fileB) && (
            <div className="grid grid-cols-2 gap-3">
              {[[fileA, nameA, pair.submission_a_id], [fileB, nameB, pair.submission_b_id]].map(([file, name, subId], i) => (
                <div key={i} className="bg-white border border-gray-100 rounded-xl px-4 py-3">
                  <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">
                    {i === 0 ? 'Student A' : 'Student B'}
                  </p>
                  <p className="text-sm font-semibold text-gray-800">{name}</p>
                  {file && <p className="text-[10px] font-mono text-gray-500 truncate mt-0.5">{file.split('/').pop()}</p>}
                  {subId && (
                    <Link to={`/submissions/${subId}`}
                      className="text-xs text-slate-600 hover:text-slate-900 font-semibold underline underline-offset-2 mt-1 inline-block">
                      View submission →
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-2 pt-1 flex-wrap">
            {pair.submission_a_id && (
              <Link to={`/submissions/${pair.submission_a_id}`}
                className="px-4 py-2 rounded-lg text-xs font-bold border border-gray-200 bg-white text-gray-700 hover:bg-gray-50">
                Open Submission A
              </Link>
            )}
            {pair.submission_b_id && (
              <Link to={`/submissions/${pair.submission_b_id}`}
                className="px-4 py-2 rounded-lg text-xs font-bold border border-gray-200 bg-white text-gray-700 hover:bg-gray-50">
                Open Submission B
              </Link>
            )}
            <button
              onClick={() => navigate(`/analysis/pair/${pair.pair_id}`, { state: { pair } })}
              className="ml-auto px-4 py-2 rounded-lg text-xs font-bold bg-slate-900 text-white hover:bg-slate-700">
              Full Comparison →
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

// ─── Main page ────────────────────────────────────────────────────────────────
const AnalysisResults = () => {
  const { assignmentId } = useParams();
  const [results,   setResults]   = useState(null);
  const [threshold, setThreshold] = useState(0.5);
  const [loading,   setLoading]   = useState(true);
  const [filter,    setFilter]    = useState('all');
  const [sort,      setSort]      = useState('score');
  const [running,    setRunning]    = useState(false);
  const [csvLoading,  setCsvLoading]  = useState(false);
  // Ref to prevent rapid re-clicks
  const runningRef = useRef(false);

  const downloadCsv = (mode = 'summary') => {
    if (csvLoading) return;
    setCsvLoading(true);
    try {
      const pairs = results?.highSimilarityPairs || [];
      if (!pairs.length) { alert('No results to export yet. Run analysis first.'); return; }

      // ── Summary mode: 8 human-readable columns ──────────────────────────
      if (mode === 'summary') {
        const RECS = {
          CRITICAL:'Exact duplicate or renamed — flag immediately.',
          HIGH:    'Strong structural similarity — schedule review.',
          MEDIUM:  'Moderate similarity — add to review queue.',
          LOW:     'Low similarity — monitor.',
          NONE:    'No action required.',
        };
        const CLONE_LABEL = {
          type1: 'Type 1 — Exact Copy', type2: 'Type 2 — Renamed Variables',
          type3: 'Type 3 — Structural Clone', none: 'No Clone',
        };
        const header = ['Student File 1','Student File 2','Plagiarism Match (%)','Clone Type','Risk Level','Student A','Student B','Recommendation'];
        const rows   = [...pairs]
          .sort((a, b) => norm(b.similarity ?? 0) - norm(a.similarity ?? 0))
          .map(p => {
            const s    = norm(p.similarity ?? 0);
            const risk = s >= 0.85 ? 'CRITICAL' : s >= 0.70 ? 'HIGH' : s >= 0.50 ? 'MEDIUM' : s >= 0.30 ? 'LOW' : 'NONE';
            const mb   = (() => { try { return typeof p.matching_blocks === 'string' ? JSON.parse(p.matching_blocks) : (p.matching_blocks || {}); } catch { return {}; } })();
            return [
              mb.file_a ? mb.file_a.split('/').pop() : '',
              mb.file_b ? mb.file_b.split('/').pop() : '',
              `${Math.round(s * 100)}%`,
              CLONE_LABEL[p.clone_type || mb.primary_clone_type] || (p.clone_type || ''),
              risk,
              p.student_a_name || '',
              p.student_b_name || '',
              RECS[risk] || '',
            ].map(v => `"${String(v).replace(/"/g, '""')}"`).join(',');
          });
        const csv  = [header.join(','), ...rows].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url  = URL.createObjectURL(blob);
        const a    = document.createElement('a');
        a.href     = url;
        a.download = `codespectra_summary_${assignmentId}_${Date.now()}.csv`;
        document.body.appendChild(a); a.click(); a.remove();
        URL.revokeObjectURL(url);
        return;
      }

      // ── Technical mode: all available scores ─────────────────────────────
      const header = [
        'rank','student_a','student_b','clone_type','similarity_pct',
        'type1_pct','type2_pct','type3_pct','confidence','risk_level',
        'file_a','file_b','needs_review','recommendation',
      ];
      const RECS = { CRITICAL:'Flag immediately.', HIGH:'Schedule review.', MEDIUM:'Add to queue.', LOW:'Monitor.', NONE:'No action.' };
      const rows = [...pairs]
        .sort((a, b) => norm(b.similarity ?? 0) - norm(a.similarity ?? 0))
        .map((p, i) => {
          const s    = norm(p.similarity ?? 0);
          const risk = s >= 0.85 ? 'CRITICAL' : s >= 0.70 ? 'HIGH' : s >= 0.50 ? 'MEDIUM' : s >= 0.30 ? 'LOW' : 'NONE';
          const mb   = (() => { try { return typeof p.matching_blocks === 'string' ? JSON.parse(p.matching_blocks) : (p.matching_blocks || {}); } catch { return {}; } })();
          return [
            i + 1,
            p.student_a_name || '',
            p.student_b_name || '',
            p.clone_type || mb.primary_clone_type || '',
            Math.round(s * 100),
            Math.round(norm(p.type1_score ?? mb.type1_score ?? 0) * 100),
            Math.round(norm(p.type2_score ?? mb.type2_score ?? 0) * 100),
            Math.round(norm(p.type3_score ?? p.structural_score ?? mb.structural_score ?? 0) * 100),
            mb.confidence || '',
            risk,
            mb.file_a ? mb.file_a.split('/').pop() : '',
            mb.file_b ? mb.file_b.split('/').pop() : '',
            (p.needs_review || s >= 0.70) ? 'YES' : 'NO',
            RECS[risk] || '',
          ].map(v => `"${String(v).replace(/"/g, '""')}"`).join(',');
        });
      const csv  = [header.join(','), ...rows].join('\n');
      const blob = new Blob([csv], { type: 'text/csv' });
      const url  = URL.createObjectURL(blob);
      const a    = document.createElement('a');
      a.href     = url;
      a.download = `codespectra_technical_${assignmentId}_${Date.now()}.csv`;
      document.body.appendChild(a); a.click(); a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('CSV export failed:', err);
    } finally {
      setCsvLoading(false);
    }
  };

  useEffect(() => { fetchResults(); }, [assignmentId, threshold]);

  const fetchResults = async () => {
    setLoading(true);
    try {
      const data = await analysisService.getAssignmentResults(assignmentId, threshold * 100);
      setResults(data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  // ── DEBOUNCED trigger — ignores clicks while already running ─────────────
  const triggerAnalysis = useCallback(async () => {
    if (runningRef.current) {
      console.log('[UI] Analysis already running — ignoring click');
      return;
    }
    runningRef.current = true;
    setRunning(true);
    try {
      await analysisService.analyzeAssignment(assignmentId);
      // Poll DB every 4s until results appear
      let attempts = 0;
      const poll = setInterval(async () => {
        attempts++;
        const data = await analysisService.getAssignmentResults(assignmentId, threshold * 100);
        if ((data?.highSimilarityPairs?.length > 0) || attempts > 30) {
          clearInterval(poll);
          setResults(data);
          setRunning(false);
          runningRef.current = false;
        }
      }, 4000);
    } catch (e) {
      console.error(e);
      setRunning(false);
      runningRef.current = false;
    }
  }, [assignmentId, threshold]);

  // Read assignment detection settings from results if available
  const assignmentSettings = results?.assignment_settings || null;
  const rawPairs = results?.highSimilarityPairs || [];

  const filtered = rawPairs.filter(p => {
    const s = norm(p.similarity ?? p.combined_score ?? 0);
    if (filter === 'high')   return s >= 0.70;
    if (filter === 'medium') return s >= 0.50 && s < 0.70;
    if (filter === 'low')    return s < 0.50;
    return true;
  });

  const sorted = [...filtered].sort((a, b) => {
    if (sort === 'name') return (a.student_a_name || '').localeCompare(b.student_a_name || '');
    return norm(b.similarity ?? 0) - norm(a.similarity ?? 0);
  });

  const criticalCount = rawPairs.filter(p => getRisk(p.similarity) === 'CRITICAL').length;
  const highCount     = rawPairs.filter(p => getRisk(p.similarity) === 'HIGH').length;
  const avgScore      = rawPairs.length
    ? rawPairs.reduce((s, p) => s + norm(p.similarity ?? 0), 0) / rawPairs.length : 0;

  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&display=swap');`}</style>

      {/* Nav */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3 min-w-0">
            <Link to={`/assignments/${assignmentId}`}
              className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-800 flex-shrink-0">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Assignment
            </Link>
            <span className="text-gray-200">|</span>
            <p className="text-xs font-black uppercase tracking-widest text-gray-400">Plagiarism Report</p>
          </div>
          <div className="flex items-center gap-2 flex-shrink-0">
            {/* Export CSV — Summary / Technical split button */}
            {results?.highSimilarityPairs?.length > 0 && (
              <div className="flex items-stretch rounded-xl overflow-hidden border border-[#B8D9D9]">
                <button
                  onClick={() => downloadCsv('summary')}
                  disabled={csvLoading}
                  title="8-column human-readable report"
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-[#2D6A6A] text-xs font-bold hover:bg-[#EBF4F4] disabled:opacity-50 transition-all border-r border-[#B8D9D9]"
                >
                  {csvLoading
                    ? <span className="w-3 h-3 border-2 border-[#B8D9D9] border-t-[#2D6A6A] rounded-full animate-spin" />
                    : <svg width="11" height="11" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>}
                  Summary
                </button>
                <button
                  onClick={() => downloadCsv('technical')}
                  disabled={csvLoading}
                  title="Full technical report with all scores"
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white text-[#2D6A6A] text-xs font-bold hover:bg-[#EBF4F4] disabled:opacity-50 transition-all"
                >
                  Technical
                </button>
              </div>
            )}
            <button onClick={triggerAnalysis} disabled={running}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[#1A1714] text-white text-xs font-bold hover:bg-[#2D2825] disabled:opacity-50 disabled:cursor-not-allowed transition-all">
              {running
                ? <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Analyzing…</>
                : '▶ Re-run Analysis'}
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-8 space-y-6">
        <div>
          <h1 className="text-2xl font-black text-gray-900 tracking-tight">Similarity Report</h1>
          <p className="text-sm text-gray-500 mt-1">
            {rawPairs.length} pairs found · showing {sorted.length} above {Math.round(threshold * 100)}% threshold
          </p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Stat label="Total pairs"    value={rawPairs.length} />
          <Stat label="Critical ≥85%"  value={criticalCount}
            accent={criticalCount > 0 ? 'text-red-600' : 'text-gray-400'} />
          <Stat label="High 70–85%"    value={highCount}
            accent={highCount > 0 ? 'text-amber-600' : 'text-gray-400'} />
          <Stat label="Avg similarity" value={`${Math.round(avgScore * 100)}%`} />
        </div>

        {/* Detection type settings banner */}
        {assignmentSettings && (
          <div className="flex flex-wrap items-center gap-2 px-4 py-3 rounded-xl bg-[#F7F3EE] border border-[#E8E1D8]">
            <span className="text-xs font-bold text-[#6B6560]">Active detectors:</span>
            {[
              { key: 'type1', label: 'Type-1 Exact',    color: '#CF7249', bg: '#FEF3EC' },
              { key: 'type2', label: 'Type-2 Renamed',  color: '#2D6A6A', bg: '#EBF4F4' },
              { key: 'type3', label: 'Type-3 Near-Miss', color: '#C4827A', bg: '#FAEDEC' },
              { key: 'type4', label: 'Type-4 Semantic/I⁠O', color: '#8B9BB4', bg: '#EFF2F7' },
            ].map(({ key, label, color, bg }) => (
              <span key={key} style={{
                fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                background: assignmentSettings[key] ? bg : '#F0EBE3',
                color: assignmentSettings[key] ? color : '#A8A29E',
                textDecoration: assignmentSettings[key] ? 'none' : 'line-through',
                opacity: assignmentSettings[key] ? 1 : 0.6,
              }}>{label}</span>
            ))}
          </div>
        )}

        {criticalCount > 0 && (
          <div className="flex items-center gap-3 px-5 py-4 rounded-xl bg-red-50 border border-red-200">
            <span className="text-xl">🚨</span>
            <p className="text-sm text-red-800 font-semibold">
              {criticalCount} pair{criticalCount !== 1 ? 's' : ''} with ≥85% similarity — immediate review recommended.
            </p>
          </div>
        )}

        {/* Controls */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-3 bg-white border border-gray-200 rounded-xl px-4 py-2.5">
            <span className="text-xs font-bold text-gray-500 flex-shrink-0">Min similarity</span>
            <input type="range" min="0" max="1" step="0.05" value={threshold}
              onChange={e => setThreshold(parseFloat(e.target.value))}
              className="w-32 accent-slate-900" />
            <span className="text-sm font-black text-slate-900 w-12">{Math.round(threshold * 100)}%</span>
          </div>

          <div className="flex gap-1.5">
            {['all','high','medium','low'].map(f => (
              <button key={f} onClick={() => setFilter(f)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold capitalize transition-all
                  ${filter === f ? 'bg-slate-900 text-white' : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-400'}`}>
                {f}
              </button>
            ))}
          </div>

          <div className="ml-auto flex gap-1.5">
            {[['score','By score'],['name','By name']].map(([v, l]) => (
              <button key={v} onClick={() => setSort(v)}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all
                  ${sort === v ? 'bg-slate-100 text-slate-900' : 'text-gray-500 hover:text-gray-800'}`}>
                {l}
              </button>
            ))}
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20 gap-3">
            <span className="w-6 h-6 border-2 border-slate-900 border-t-transparent rounded-full animate-spin" />
            <span className="text-sm text-gray-500">Loading results…</span>
          </div>
        ) : rawPairs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <span className="text-5xl mb-4">📋</span>
            <p className="font-bold text-gray-700 text-lg">No results yet</p>
            <p className="text-sm text-gray-500 mt-1 mb-4">Click Run Analysis to start detection.</p>
            <button onClick={triggerAnalysis} disabled={running}
              className="px-6 py-3 rounded-xl bg-slate-900 text-white text-sm font-bold hover:bg-slate-700 disabled:opacity-50">
              {running ? 'Analyzing…' : '▶ Run Analysis Now'}
            </button>
          </div>
        ) : sorted.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-center">
            <span className="text-5xl mb-4">✅</span>
            <p className="font-bold text-gray-700 text-lg">No pairs above {Math.round(threshold * 100)}%</p>
            <p className="text-sm text-gray-500 mt-1">Lower the threshold or change the filter.</p>
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
