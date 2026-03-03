import React, { useState, useEffect } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import analysisService from '../../services/analysisService';

// ─── Constants ────────────────────────────────────────────────────────────────
const RISK = {
  CRITICAL: { label:'Critical', bg:'bg-red-50',    text:'text-red-700',    bar:'bg-red-500',    border:'border-red-200'    },
  HIGH:     { label:'High',     bg:'bg-orange-50', text:'text-orange-700', bar:'bg-orange-400', border:'border-orange-200' },
  MEDIUM:   { label:'Medium',   bg:'bg-amber-50',  text:'text-amber-700',  bar:'bg-amber-400',  border:'border-amber-200'  },
  LOW:      { label:'Low',      bg:'bg-blue-50',   text:'text-blue-600',   bar:'bg-blue-400',   border:'border-blue-200'   },
  NONE:     { label:'Clean',    bg:'bg-gray-50',   text:'text-gray-500',   bar:'bg-gray-300',   border:'border-gray-200'   },
};

function getRisk(score) {
  const s = typeof score === 'number' ? score : 0;
  if (s >= 0.85) return 'CRITICAL';
  if (s >= 0.70) return 'HIGH';
  if (s >= 0.50) return 'MEDIUM';
  if (s >= 0.30) return 'LOW';
  return 'NONE';
}

const pct = n => `${Math.round((n || 0) * 100)}%`;

// ─── Full-width side-by-side code viewer ─────────────────────────────────────
const CodeViewer = ({ fragA, fragB, fragmentIndex }) => {
  const linesA  = (fragA?.source || '').split('\n');
  const linesB  = (fragB?.source || '').split('\n');
  const simSet  = new Set(fragA?.similar_lines || []);
  const maxLine = Math.max(linesA.length, linesB.length);

  const renderSide = (lines, meta, side) => (
    <div className="flex-1 min-w-0 border-r last:border-r-0 border-gray-200">
      {/* File header */}
      <div className="bg-gray-900 px-5 py-3 border-b border-gray-700">
        <div className="flex items-center gap-2 mb-0.5">
          <span className={`text-[9px] font-black uppercase tracking-widest px-1.5 py-px rounded
            ${side === 'A' ? 'bg-blue-900 text-blue-300' : 'bg-violet-900 text-violet-300'}`}>
            {side === 'A' ? 'Student A' : 'Student B'}
          </span>
        </div>
        <p className="text-xs font-bold text-gray-100 font-mono truncate">
          {meta?.file || '—'}
        </p>
        {meta?.name && (
          <p className="text-[10px] text-gray-500 mt-0.5 font-mono">
            {meta.name}(){meta.start ? ` · lines ${meta.start}–${meta.end}` : ''}
          </p>
        )}
      </div>

      {/* Code lines */}
      <div className="font-mono text-xs leading-[22px] bg-gray-950 overflow-x-auto">
        {Array.from({ length: Math.max(lines.length, 1) }, (_, i) => {
          const line = lines[i] ?? '';
          const highlighted = simSet.has(i);
          return (
            <div key={i}
              className={`flex min-w-0 ${highlighted
                ? 'bg-yellow-400/10 border-l-[3px] border-yellow-400'
                : 'hover:bg-gray-900/60'}`}>
              <span className="select-none text-gray-600 w-12 text-right pr-4 py-px flex-shrink-0 bg-gray-900/30 border-r border-gray-800/50 text-[11px]">
                {i + 1}
              </span>
              <pre className={`flex-1 px-4 py-px whitespace-pre text-[11px]
                ${highlighted ? 'text-yellow-100 font-semibold' : 'text-gray-400'}`}>
                {line || ' '}
              </pre>
            </div>
          );
        })}
        {/* Empty padding */}
        {lines.length === 0 && (
          <div className="px-4 py-8 text-center text-gray-600 text-xs">No source available</div>
        )}
      </div>
    </div>
  );

  return (
    <div className="rounded-2xl overflow-hidden border border-gray-200 shadow-sm">
      {/* Fragment badge */}
      <div className="bg-white border-b border-gray-100 px-5 py-2.5 flex items-center gap-3">
        <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">
          Fragment {fragmentIndex + 1}
        </span>
        {fragA?.similarity != null && (
          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700">
            {Math.round(fragA.similarity * 100)}% match
          </span>
        )}
        {simSet.size > 0 && (
          <span className="text-[10px] text-gray-400">
            {simSet.size} similar line{simSet.size !== 1 ? 's' : ''} highlighted
          </span>
        )}
      </div>

      {/* Split view */}
      <div className="grid grid-cols-2 divide-x divide-gray-200 max-h-[520px] overflow-auto">
        {renderSide(linesA, fragA, 'A')}
        {renderSide(linesB, fragB, 'B')}
      </div>
    </div>
  );
};

// ─── Score card ───────────────────────────────────────────────────────────────
const ScoreCard = ({ label, sub, score, color }) => (
  <div className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm">
    <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-0.5">{label}</p>
    <p className="text-[10px] text-gray-400 mb-3">{sub}</p>
    <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden mb-2">
      <div className={`h-full rounded-full ${color} transition-all`}
        style={{ width: score != null ? pct(score) : '0%' }} />
    </div>
    <p className="text-2xl font-black text-gray-900">
      {score != null ? pct(score) : '—'}
    </p>
  </div>
);

// ─── Student card ─────────────────────────────────────────────────────────────
const StudentCard = ({ label, name, submissionId, files = [] }) => (
  <div className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm">
    <p className="text-[10px] font-black uppercase tracking-widest text-gray-400 mb-2">{label}</p>
    <p className="font-black text-gray-900 text-base mb-1">{name || '—'}</p>
    {files.length > 0 && (
      <div className="space-y-1 mb-3">
        {files.map((f, i) => (
          <p key={i} className="text-[10px] font-mono text-gray-500 truncate">{f}</p>
        ))}
      </div>
    )}
    {submissionId && (
      <Link to={`/submissions/${submissionId}`}
        className="inline-flex items-center gap-1 text-xs font-bold text-slate-700 hover:text-slate-900 underline underline-offset-2">
        View full submission →
      </Link>
    )}
  </div>
);

// ─── Main page ────────────────────────────────────────────────────────────────
export default function ComparisonView() {
  const { pairId }      = useParams();
  const { state }       = useLocation(); // pair data passed via navigate(path, { state: pair })
  const [pair, setPair] = useState(state?.pair || null);
  const [loading, setLoading] = useState(!state?.pair);
  const [activeFragment, setActiveFragment] = useState(0);

  // If no state was passed, try fetching by pairId
  useEffect(() => {
    if (!pair && pairId) {
      setLoading(true);
      analysisService.getPairDetail(pairId)
        .then(data => setPair(data))
        .catch(err => console.error('Failed to load pair:', err))
        .finally(() => setLoading(false));
    }
  }, [pairId]);

  // Parse fragments
  const fragments = (() => {
    if (!pair) return [];
    try {
      const mb = pair.matching_blocks;
      if (!mb) return [];
      const p = typeof mb === 'string' ? JSON.parse(mb) : mb;
      return Array.isArray(p) ? p : (p.fragments || []);
    } catch { return []; }
  })();

  const score = pair ? (pair.similarity ?? pair.combined_score ?? 0) : 0;
  const riskLevel = getRisk(score);
  const R = RISK[riskLevel];

  // Files mentioned across fragments
  const filesA = [...new Set(fragments.map(f => f.file_a).filter(Boolean))];
  const filesB = [...new Set(fragments.map(f => f.file_b).filter(Boolean))];

  if (loading) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <div className="text-center">
        <div className="w-10 h-10 border-2 border-slate-900 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-gray-500 font-medium">Loading comparison…</p>
      </div>
    </div>
  );

  if (!pair) return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <div className="text-center">
        <p className="text-gray-500 font-medium">Pair data not found.</p>
        <Link to="/dashboard" className="text-xs text-slate-600 underline mt-2 inline-block">
          Back to dashboard
        </Link>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
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
            <span className="text-xs font-black uppercase tracking-widest text-gray-400">
              Pair Comparison
            </span>
          </div>

          {/* Overall risk badge */}
          <div className={`flex items-center gap-2 px-4 py-2 rounded-xl border ${R.bg} ${R.border}`}>
            <span className={`w-2 h-2 rounded-full ${R.bar}`} />
            <span className={`text-xs font-black uppercase tracking-widest ${R.text}`}>
              {R.label} · {Math.round(score * 100)}% overall similarity
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">

        {/* Student info + scores */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <StudentCard
            label="Student A"
            name={pair.student_a_name}
            submissionId={pair.submission_a_id}
            files={filesA}
          />
          <StudentCard
            label="Student B"
            name={pair.student_b_name}
            submissionId={pair.submission_b_id}
            files={filesB}
          />

          {/* Summary stats */}
          <div className="bg-white rounded-2xl border border-gray-100 px-5 py-4 shadow-sm space-y-3">
            <p className="text-[10px] font-black uppercase tracking-widest text-gray-400">Detection Summary</p>
            {[
              { label: 'Overall',    val: score,                                            bar: R.bar           },
              { label: 'Type-1',     val: pair.type1_score,                                 bar: 'bg-blue-500'   },
              { label: 'Type-2',     val: pair.type2_score,                                 bar: 'bg-violet-500' },
              { label: 'Structural', val: pair.structural_score ?? pair.type3_score,        bar: 'bg-amber-500'  },
              { label: 'Semantic',   val: pair.semantic_score   ?? pair.type4_score,        bar: 'bg-rose-500'   },
            ].map(({ label, val, bar }) => (
              <div key={label} className="flex items-center gap-3">
                <span className="text-xs text-gray-500 w-20 flex-shrink-0">{label}</span>
                <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                  <div className={`h-full rounded-full ${bar}`}
                    style={{ width: val != null ? pct(val) : '0%' }} />
                </div>
                <span className="text-xs font-black text-gray-900 w-10 text-right">
                  {val != null ? pct(val) : '—'}
                </span>
              </div>
            ))}
            <div className="pt-2 border-t border-gray-100">
              <p className="text-[10px] text-gray-400">
                {fragments.length} matching fragment{fragments.length !== 1 ? 's' : ''} detected
              </p>
            </div>
          </div>
        </div>

        {/* 4-type score cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <ScoreCard label="Type-1" sub="Exact copy"            score={pair.type1_score}                          color="bg-blue-500"   />
          <ScoreCard label="Type-2" sub="Renamed variables"     score={pair.type2_score}                          color="bg-violet-500" />
          <ScoreCard label="Type-3" sub="Structural similarity" score={pair.structural_score ?? pair.type3_score} color="bg-amber-500"  />
          <ScoreCard label="Type-4" sub="Semantic similarity"   score={pair.semantic_score   ?? pair.type4_score} color="bg-rose-500"   />
        </div>

        {/* Fragment section */}
        {fragments.length > 0 ? (
          <div className="space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-black text-gray-900">Matching Code Fragments</h2>
                <p className="text-sm text-gray-500 mt-0.5">
                  {fragments.length} fragment{fragments.length !== 1 ? 's' : ''} found.
                  Yellow lines indicate highest similarity.
                </p>
              </div>

              {/* Fragment selector — shown when >1 fragment */}
              {fragments.length > 1 && (
                <div className="flex items-center gap-2">
                  <button
                    disabled={activeFragment === 0}
                    onClick={() => setActiveFragment(i => i - 1)}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 disabled:opacity-30">
                    ‹
                  </button>
                  <span className="text-sm font-bold text-gray-700 min-w-[80px] text-center">
                    {activeFragment + 1} / {fragments.length}
                  </span>
                  <button
                    disabled={activeFragment === fragments.length - 1}
                    onClick={() => setActiveFragment(i => i + 1)}
                    className="w-8 h-8 rounded-lg border border-gray-200 flex items-center justify-center text-gray-500 hover:bg-gray-100 disabled:opacity-30">
                    ›
                  </button>
                </div>
              )}
            </div>

            {/* Fragment tab pills — for quick jumping */}
            {fragments.length > 1 && (
              <div className="flex flex-wrap gap-2">
                {fragments.map((frag, i) => (
                  <button key={i} onClick={() => setActiveFragment(i)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all
                      ${activeFragment === i
                        ? 'bg-slate-900 text-white'
                        : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-400'}`}>
                    Fragment {i + 1}
                    {frag.similarity != null && (
                      <span className="ml-1 opacity-60">{Math.round(frag.similarity * 100)}%</span>
                    )}
                  </button>
                ))}
              </div>
            )}

            {/* Active fragment diff */}
            {(() => {
              const frag = fragments[activeFragment];
              if (!frag) return null;
              return (
                <CodeViewer
                  key={activeFragment}
                  fragmentIndex={activeFragment}
                  fragA={{
                    file:         frag.file_a,
                    name:         frag.func_a,
                    start:        frag.start_a,
                    end:          frag.end_a,
                    source:       frag.source_a,
                    similar_lines: frag.similar_lines,
                    similarity:   frag.similarity,
                  }}
                  fragB={{
                    file:   frag.file_b,
                    name:   frag.func_b,
                    start:  frag.start_b,
                    end:    frag.end_b,
                    source: frag.source_b,
                  }}
                />
              );
            })()}

            {/* All fragments summary list */}
            {fragments.length > 1 && (
              <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
                <div className="px-5 py-3 border-b border-gray-100">
                  <p className="text-xs font-black uppercase tracking-widest text-gray-400">
                    All Fragments
                  </p>
                </div>
                <div className="divide-y divide-gray-50">
                  {fragments.map((frag, i) => (
                    <button key={i} onClick={() => setActiveFragment(i)}
                      className={`w-full text-left px-5 py-3 flex items-center gap-4 hover:bg-gray-50 transition-colors
                        ${activeFragment === i ? 'bg-slate-50' : ''}`}>
                      <span className="text-xs font-black text-gray-300 w-6">#{i + 1}</span>
                      <div className="flex-1 min-w-0">
                        <div className="flex gap-2 text-xs text-gray-600 font-mono truncate">
                          <span className="text-blue-600 truncate max-w-[180px]">{frag.file_a || '—'}</span>
                          <span className="text-gray-300">↔</span>
                          <span className="text-violet-600 truncate max-w-[180px]">{frag.file_b || '—'}</span>
                        </div>
                        {(frag.func_a || frag.func_b) && (
                          <p className="text-[10px] text-gray-400 mt-0.5 font-mono">
                            {frag.func_a && `${frag.func_a}()`}
                            {frag.func_a && frag.func_b && ' ↔ '}
                            {frag.func_b && `${frag.func_b}()`}
                          </p>
                        )}
                      </div>
                      {frag.similarity != null && (
                        <span className={`text-xs font-black flex-shrink-0 ${RISK[getRisk(frag.similarity)].text}`}>
                          {Math.round(frag.similarity * 100)}%
                        </span>
                      )}
                      {activeFragment === i && (
                        <span className="text-[10px] font-bold text-slate-500 flex-shrink-0">Viewing</span>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 rounded-2xl border border-dashed border-gray-200 text-center">
            <span className="text-5xl mb-4">📋</span>
            <p className="font-bold text-gray-600 text-base">No fragment-level data</p>
            <p className="text-sm text-gray-400 mt-1 max-w-sm">
              The analysis engine returned file-level scores only.
              Re-run with detailed mode enabled to see line-by-line fragment comparison.
            </p>
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3 pt-2 border-t border-gray-200">
          {pair.submission_a_id && (
            <Link to={`/submissions/${pair.submission_a_id}`}
              className="px-5 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-bold text-gray-700 hover:bg-gray-50 transition-colors">
              Open Submission A
            </Link>
          )}
          {pair.submission_b_id && (
            <Link to={`/submissions/${pair.submission_b_id}`}
              className="px-5 py-2.5 rounded-xl border border-gray-200 bg-white text-sm font-bold text-gray-700 hover:bg-gray-50 transition-colors">
              Open Submission B
            </Link>
          )}
          <button onClick={() => window.print()}
            className="ml-auto px-5 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-bold hover:bg-slate-700 transition-colors">
            Export / Print
          </button>
        </div>
      </div>
    </div>
  );
}