// frontend/src/pages/analysis/ComparisonView.jsx
import React, { useState, useEffect } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import analysisService from '../../services/analysisService';

const RISK = {
  CRITICAL: { label:'Critical', bg:'bg-red-50',    text:'text-red-700',    bar:'bg-red-500',    border:'border-red-200'    },
  HIGH:     { label:'High',     bg:'bg-orange-50', text:'text-orange-700', bar:'bg-orange-400', border:'border-orange-200' },
  MEDIUM:   { label:'Medium',   bg:'bg-amber-50',  text:'text-amber-700',  bar:'bg-amber-400',  border:'border-amber-200'  },
  LOW:      { label:'Low',      bg:'bg-blue-50',   text:'text-blue-600',   bar:'bg-blue-400',   border:'border-blue-200'   },
  NONE:     { label:'Clean',    bg:'bg-gray-50',   text:'text-gray-500',   bar:'bg-gray-300',   border:'border-gray-200'   },
};

const norm = v => v == null ? 0 : v > 1 ? v / 100 : v;
const pct  = v => `${Math.round(norm(v) * 100)}%`;

function getRisk(score) {
  const s = norm(score);
  if (s >= 0.85) return 'CRITICAL';
  if (s >= 0.70) return 'HIGH';
  if (s >= 0.50) return 'MEDIUM';
  if (s >= 0.30) return 'LOW';
  return 'NONE';
}

// ─── Side-by-side code viewer ─────────────────────────────────────────────────
const CodeViewer = ({ fragA, fragB, fragmentIndex, total }) => {
  const linesA = (fragA?.source_a || fragA?.source || '').split('\n');
  const linesB = (fragB?.source_b || fragB?.source || '').split('\n');
  const simSet = new Set(fragA?.similar_lines || []);

  const renderSide = (lines, meta, label, colorClass) => (
    <div className="flex-1 min-w-0 flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 px-4 py-3 border-b border-gray-700 flex-shrink-0">
        <div className="flex items-center gap-2 mb-1">
          <span className={`text-[9px] font-black uppercase tracking-widest px-1.5 py-px rounded ${colorClass}`}>
            {label}
          </span>
          {total > 1 && (
            <span className="text-[9px] text-gray-500">Fragment {fragmentIndex + 1}/{total}</span>
          )}
        </div>
        <p className="text-xs font-bold text-gray-100 font-mono truncate">
          {meta?.file_a || meta?.file_b || meta?.file || '—'}
        </p>
        {(meta?.func_a || meta?.func_b || meta?.name) && (
          <p className="text-[10px] text-gray-500 mt-0.5 font-mono">
            {(meta.func_a || meta.func_b || meta.name)}()
            {(meta.start_a || meta.start_b || meta.start) &&
              ` · lines ${meta.start_a || meta.start_b || meta.start}–${meta.end_a || meta.end_b || meta.end}`}
          </p>
        )}
      </div>

      {/* Code */}
      <div className="font-mono text-xs leading-[22px] bg-gray-950 overflow-auto flex-1 max-h-[560px]">
        {lines.length === 0 || (lines.length === 1 && lines[0] === '') ? (
          <div className="px-4 py-12 text-center text-gray-600 text-xs">No source available</div>
        ) : (
          lines.map((line, i) => {
            const highlighted = simSet.has(i);
            return (
              <div key={i} className={`flex min-w-0 ${highlighted
                ? 'bg-yellow-400/10 border-l-[3px] border-yellow-400'
                : 'hover:bg-gray-900/50'}`}>
                <span className="select-none text-gray-600 w-12 text-right pr-4 py-px flex-shrink-0 bg-gray-900/30 border-r border-gray-800 text-[11px]">
                  {i + 1}
                </span>
                <pre className={`flex-1 px-4 py-px whitespace-pre text-[11px] overflow-x-auto
                  ${highlighted ? 'text-yellow-100 font-semibold' : 'text-gray-300'}`}>
                  {line || ' '}
                </pre>
              </div>
            );
          })
        )}
      </div>
    </div>
  );

  return (
    <div className="rounded-2xl overflow-hidden border border-gray-800 shadow-xl">
      {/* Fragment info bar */}
      <div className="bg-gray-800 border-b border-gray-700 px-5 py-2.5 flex items-center gap-3">
        <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">
          Code Comparison
        </span>
        {fragA?.similarity != null && (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-900/60 text-yellow-300">
            {Math.round(norm(fragA.similarity) * 100)}% match
          </span>
        )}
        {simSet.size > 0 && (
          <span className="text-[10px] text-gray-500">
            {simSet.size} highlighted lines
          </span>
        )}
      </div>

      {/* Split pane */}
      <div className="grid grid-cols-2 divide-x divide-gray-800">
        {renderSide(linesA, fragA, 'Student A', 'bg-blue-900 text-blue-300')}
        {renderSide(linesB, fragB, 'Student B', 'bg-violet-900 text-violet-300')}
      </div>
    </div>
  );
};

const ScoreBar = ({ label, val, color }) => (
  <div className="flex items-center gap-3">
    <span className="text-xs text-gray-500 w-20 flex-shrink-0">{label}</span>
    <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${color}`} style={{ width: pct(val) }} />
    </div>
    <span className="text-xs font-black text-gray-900 w-10 text-right">{pct(val)}</span>
  </div>
);

// ─── Main ─────────────────────────────────────────────────────────────────────
export default function ComparisonView() {
  const { pairId }      = useParams();
  const { state }       = useLocation();
  const [pair, setPair] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [activeFragment, setActiveFragment] = useState(0);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        // Always fetch from backend — it reads actual file content from disk
        const data = await analysisService.getPairDetail(pairId);
        setPair(data);
      } catch (err) {
        console.error('Failed to load pair:', err);
        // Fall back to state if API fails
        if (state?.pair) setPair(state.pair);
        else setError('Could not load pair details.');
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [pairId]);

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <div className="text-center">
        <div className="w-10 h-10 border-2 border-white border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-gray-400">Loading comparison…</p>
      </div>
    </div>
  );

  if (error || !pair) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <div className="text-center">
        <p className="text-gray-500 font-medium">{error || 'Pair data not found.'}</p>
        <button onClick={() => window.history.back()}
          className="text-xs text-slate-600 underline mt-2 inline-block">← Go back</button>
      </div>
    </div>
  );

  const score      = norm(pair.similarity ?? pair.combined_score ?? 0);
  const riskLevel  = getRisk(score);
  const R          = RISK[riskLevel];
  const fragments  = pair.fragments || [];

  const t1 = norm(pair.type1_score      ?? 0);
  const t2 = norm(pair.type2_score      ?? 0);
  const t3 = norm(pair.structural_score ?? pair.type3_score ?? 0);
  const t4 = norm(pair.semantic_score   ?? pair.type4_score ?? 0);

  const activeF = fragments[activeFragment];

  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&display=swap');`}</style>

      {/* Nav */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-20">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <button onClick={() => window.history.back()}
              className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-800">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Report
            </button>
            <span className="text-gray-200">·</span>
            <span className="text-xs font-black uppercase tracking-widest text-gray-400">Pair Comparison</span>
          </div>
          <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${R.bg} ${R.border}`}>
            <span className={`w-2 h-2 rounded-full ${R.bar}`} />
            <span className={`text-xs font-black uppercase tracking-widest ${R.text}`}>
              {R.label} · {Math.round(score * 100)}% similarity
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

        {/* Student cards + score summary */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Student A */}
          <div className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm">
            <p className="text-[10px] font-black uppercase tracking-widest text-blue-400 mb-2">Student A</p>
            <p className="font-black text-gray-900 text-lg">{pair.student_a_name || '—'}</p>
            {pair.file_a && <p className="text-[11px] font-mono text-gray-500 truncate mt-1">{pair.file_a}</p>}
            {pair.submission_a_id && (
              <Link to={`/submissions/${pair.submission_a_id}`}
                className="text-xs font-bold text-slate-600 hover:text-slate-900 underline underline-offset-2 mt-2 inline-block">
                View submission →
              </Link>
            )}
          </div>

          {/* Student B */}
          <div className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm">
            <p className="text-[10px] font-black uppercase tracking-widest text-violet-400 mb-2">Student B</p>
            <p className="font-black text-gray-900 text-lg">{pair.student_b_name || '—'}</p>
            {pair.file_b && <p className="text-[11px] font-mono text-gray-500 truncate mt-1">{pair.file_b}</p>}
            {pair.submission_b_id && (
              <Link to={`/submissions/${pair.submission_b_id}`}
                className="text-xs font-bold text-slate-600 hover:text-slate-900 underline underline-offset-2 mt-2 inline-block">
                View submission →
              </Link>
            )}
          </div>

          {/* Score summary */}
          <div className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm space-y-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-gray-400">Detection Scores</p>
            <ScoreBar label="Overall"    val={score} color={R.bar} />
            <ScoreBar label="Type-1"     val={t1}    color="bg-blue-500"   />
            <ScoreBar label="Type-2"     val={t2}    color="bg-violet-500" />
            <ScoreBar label="Structural" val={t3}    color="bg-amber-500"  />
            <ScoreBar label="Semantic"   val={t4}    color="bg-rose-500"   />
            {pair.confidence && (
              <p className="text-[10px] text-gray-400 pt-1 border-t border-gray-100">
                Confidence: <span className="font-bold text-gray-700">{pair.confidence}</span>
                {fragments.length > 0 && ` · ${fragments.length} fragment${fragments.length !== 1 ? 's' : ''}`}
              </p>
            )}
          </div>
        </div>

        {/* 4-type score cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label:'Type-1', sub:'Exact copy',            val:t1, color:'bg-blue-500'   },
            { label:'Type-2', sub:'Renamed variables',     val:t2, color:'bg-violet-500' },
            { label:'Type-3', sub:'Structural similarity', val:t3, color:'bg-amber-500'  },
            { label:'Type-4', sub:'Semantic similarity',   val:t4, color:'bg-rose-500'   },
          ].map(({ label, sub, val, color }) => (
            <div key={label} className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm">
              <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-0.5">{label}</p>
              <p className="text-[10px] text-gray-400 mb-3">{sub}</p>
              <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-2">
                <div className={`h-full rounded-full ${color}`} style={{ width: pct(val) }} />
              </div>
              <p className="text-2xl font-black text-gray-900">{pct(val)}</p>
            </div>
          ))}
        </div>

        {/* ── Code comparison section ── */}
        {fragments.length > 0 ? (
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-gray-900">Code Comparison</h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  Comparing the most similar files between both students.
                  {fragments[0]?.similar_lines?.length > 0 && ' Yellow lines show matching code.'}
                </p>
              </div>

              {/* Fragment nav (only if multiple) */}
              {fragments.length > 1 && (
                <div className="flex items-center gap-2">
                  <button disabled={activeFragment === 0}
                    onClick={() => setActiveFragment(i => i - 1)}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 disabled:opacity-30">
                    ‹
                  </button>
                  <span className="text-sm font-bold text-gray-700">
                    {activeFragment + 1} / {fragments.length}
                  </span>
                  <button disabled={activeFragment === fragments.length - 1}
                    onClick={() => setActiveFragment(i => i + 1)}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 disabled:opacity-30">
                    ›
                  </button>
                </div>
              )}
            </div>

            {/* Fragment pills */}
            {fragments.length > 1 && (
              <div className="flex flex-wrap gap-2">
                {fragments.map((f, i) => (
                  <button key={i} onClick={() => setActiveFragment(i)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all
                      ${activeFragment === i
                        ? 'bg-slate-900 text-white'
                        : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-400'}`}>
                    Fragment {i + 1}
                    {f.similarity != null && <span className="ml-1 opacity-60">{Math.round(norm(f.similarity) * 100)}%</span>}
                  </button>
                ))}
              </div>
            )}

            {/* The actual code viewer */}
            {activeF && (
              <CodeViewer
                key={activeFragment}
                fragmentIndex={activeFragment}
                total={fragments.length}
                fragA={activeF}
                fragB={activeF}
              />
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 rounded-2xl border border-dashed border-gray-200 text-center bg-white">
            <span className="text-5xl mb-4">📄</span>
            <p className="font-bold text-gray-600 text-base">File content unavailable</p>
            <p className="text-sm text-gray-400 mt-1 max-w-sm">
              The source files could not be read from disk.
              Make sure the analysis-engine container is running and files are mounted correctly.
            </p>
          </div>
        )}

        {/* Bottom actions */}
        <div className="flex gap-3 pt-2 border-t border-gray-200">
          {pair.submission_a_id && (
            <Link to={`/submissions/${pair.submission_a_id}`}
              className="px-5 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-bold text-gray-700 hover:bg-gray-50">
              Open Submission A
            </Link>
          )}
          {pair.submission_b_id && (
            <Link to={`/submissions/${pair.submission_b_id}`}
              className="px-5 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-bold text-gray-700 hover:bg-gray-50">
              Open Submission B
            </Link>
          )}
          <button onClick={() => window.print()}
            className="ml-auto px-5 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-bold hover:bg-slate-700">
            Export / Print
          </button>
        </div>
      </div>
    </div>
  );
}