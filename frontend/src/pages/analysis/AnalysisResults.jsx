// frontend/src/pages/analysis/AnalysisResults.jsx
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import analysisService from '../../services/analysisService';

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
  const [running,   setRunning]   = useState(false);
  // Ref to prevent rapid re-clicks
  const runningRef = useRef(false);

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
  const lysis = useCallback(async () => {
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
          <button onClick={triggerAnalysis} disabled={running}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-bold hover:bg-slate-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0">
            {running
              ? <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" /> Analyzing…</>
              : '▶ Re-run Analysis'}
          </button>
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
