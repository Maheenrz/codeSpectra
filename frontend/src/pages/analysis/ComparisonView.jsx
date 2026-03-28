// frontend/src/pages/analysis/ComparisonView.jsx
import React, { useState, useEffect } from 'react';
import { Link, useParams, useLocation } from 'react-router-dom';
import analysisService from '../../services/analysisService';

const RISK = {
  CRITICAL: { label:'Critical', bg:'bg-red-50',     text:'text-red-700',    bar:'bg-red-500',    border:'border-red-200'    },
  HIGH:     { label:'High',     bg:'bg-[#FEF3EC]',  text:'text-[#CF7249]',  bar:'bg-[#CF7249]',  border:'border-[#F4C9AA]'  },
  MEDIUM:   { label:'Medium',   bg:'bg-amber-50',   text:'text-amber-700',  bar:'bg-amber-400',  border:'border-amber-200'  },
  LOW:      { label:'Low',      bg:'bg-blue-50',    text:'text-blue-600',   bar:'bg-blue-400',   border:'border-blue-200'   },
  NONE:     { label:'Clean',    bg:'bg-[#F7F3EE]',  text:'text-[#6B6560]',  bar:'bg-[#D4CEC8]',  border:'border-[#E8E1D8]'  },
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

/* ── Icons ── */
const Ico = {
  ArrowLeft: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M19 12H5M12 5l-7 7 7 7"/>
    </svg>
  ),
  Shield: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
    </svg>
  ),
  ExternalLink: () => (
    <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
      <polyline points="15 3 21 3 21 9"/>
      <line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
  ),
  Printer: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="6 9 6 2 18 2 18 9"/>
      <path d="M6 18H4a2 2 0 01-2-2v-5a2 2 0 012-2h16a2 2 0 012 2v5a2 2 0 01-2 2h-2"/>
      <rect x="6" y="14" width="12" height="8"/>
    </svg>
  ),
  ChevronLeft: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="15 18 9 12 15 6"/>
    </svg>
  ),
  ChevronRight: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="9 18 15 12 9 6"/>
    </svg>
  ),
  Code: () => (
    <svg width="20" height="20" fill="none" stroke="#CF7249" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="16 18 22 12 16 6"/>
      <polyline points="8 6 2 12 8 18"/>
    </svg>
  ),
  FileText: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <line x1="16" y1="13" x2="8" y2="13"/>
      <line x1="16" y1="17" x2="8" y2="17"/>
    </svg>
  ),
};

/* ── Score bar (light theme) ── */
const ScoreBar = ({ label, val, color }) => (
  <div className="flex items-center gap-3">
    <span className="text-xs text-[#6B6560] w-20 flex-shrink-0">{label}</span>
    <div className="flex-1 h-2 bg-[#F0EBE3] rounded-full overflow-hidden">
      <div className={`h-full rounded-full ${color}`} style={{ width: pct(val) }} />
    </div>
    <span className="text-xs font-black text-[#1A1714] w-10 text-right">{pct(val)}</span>
  </div>
);

/* ── Code viewer (dark) ── */
const CodeViewer = ({ fragA, fragB, fragmentIndex, total }) => {
  const linesA = (fragA?.source_a || fragA?.source || '').split('\n');
  const linesB = (fragB?.source_b || fragB?.source || '').split('\n');
  const simSet = new Set(fragA?.similar_lines || []);

  const renderSide = (lines, meta, label, accentClass) => (
    <div className="flex-1 min-w-0 flex flex-col">
      <div className="bg-gray-900 px-5 py-3.5 border-b border-gray-800 flex-shrink-0">
        <div className="flex items-center gap-2 mb-1">
          <span className={`text-[9px] font-black uppercase tracking-widest px-2 py-0.5 rounded-lg ${accentClass}`}>
            {label}
          </span>
          {total > 1 && <span className="text-[9px] text-gray-500">Fragment {fragmentIndex + 1}/{total}</span>}
        </div>
        <p className="text-xs font-bold text-gray-200 font-mono truncate">{meta?.file_a || meta?.file_b || meta?.file || '—'}</p>
        {(meta?.func_a || meta?.func_b || meta?.name) && (
          <p className="text-[10px] text-gray-500 mt-0.5 font-mono">
            {(meta.func_a || meta.func_b || meta.name)}()
            {(meta.start_a || meta.start_b || meta.start) && ` · lines ${meta.start_a||meta.start_b||meta.start}–${meta.end_a||meta.end_b||meta.end}`}
          </p>
        )}
      </div>
      <div className="font-mono text-xs leading-[22px] bg-gray-950 overflow-auto flex-1 max-h-[560px]">
        {lines.length === 0 || (lines.length === 1 && lines[0] === '') ? (
          <div className="px-5 py-16 text-center text-gray-600 text-xs">No source available</div>
        ) : lines.map((line, i) => {
          const highlighted = simSet.has(i);
          return (
            <div key={i} className={`flex min-w-0 ${highlighted ? 'bg-yellow-400/10 border-l-[3px] border-[#CF7249]' : 'hover:bg-gray-900/50'}`}>
              <span className="select-none text-gray-600 w-12 text-right pr-4 py-px flex-shrink-0 bg-gray-900/30 border-r border-gray-800 text-[11px]">{i+1}</span>
              <pre className={`flex-1 px-4 py-px whitespace-pre text-[11px] overflow-x-auto ${highlighted ? 'text-yellow-100 font-semibold' : 'text-gray-300'}`}>{line||' '}</pre>
            </div>
          );
        })}
      </div>
    </div>
  );

  return (
    <div className="rounded-3xl overflow-hidden border border-gray-800 shadow-xl">
      <div className="bg-gray-800 border-b border-gray-700 px-6 py-3 flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-gray-700 flex items-center justify-center flex-shrink-0">
          <Ico.Code />
        </div>
        <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">Code Comparison</span>
        {fragA?.similarity != null && (
          <span className="text-[10px] font-black px-2.5 py-1 rounded-full bg-[#CF7249]/20 text-[#CF7249]">
            {Math.round(norm(fragA.similarity) * 100)}% match
          </span>
        )}
        {simSet.size > 0 && <span className="text-[10px] text-gray-500">{simSet.size} highlighted lines</span>}
      </div>
      <div className="grid grid-cols-2 divide-x divide-gray-800">
        {renderSide(linesA, fragA, 'Student A', 'bg-blue-900 text-blue-300')}
        {renderSide(linesB, fragB, 'Student B', 'bg-purple-900 text-purple-300')}
      </div>
    </div>
  );
};

/* ── Main ── */
export default function ComparisonView() {
  const { pairId }      = useParams();
  const { state }       = useLocation();
  const [pair, setPair] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error,   setError]   = useState(null);
  const [activeFragment, setActiveFragment] = useState(0);

  useEffect(() => {
    const load = async () => {
      setLoading(true); setError(null);
      try {
        const data = await analysisService.getPairDetail(pairId);
        setPair(data);
      } catch (err) {
        console.error('Failed to load pair:', err);
        if (state?.pair) setPair(state.pair);
        else setError('Could not load pair details.');
      } finally { setLoading(false); }
    };
    load();
  }, [pairId]);

  if (loading) return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center">
      <div className="text-center">
        <div className="w-10 h-10 border-2 border-[#CF7249] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-[#6B6560] font-medium">Loading comparison…</p>
      </div>
    </div>
  );

  if (error || !pair) return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center">
      <div className="text-center">
        <p className="text-[#6B6560] font-medium">{error || 'Pair data not found.'}</p>
        <button onClick={() => window.history.back()} className="text-xs text-[#CF7249] underline mt-2 inline-block">← Go back</button>
      </div>
    </div>
  );

  const score     = norm(pair.similarity ?? pair.combined_score ?? 0);
  const riskLevel = getRisk(score);
  const R         = RISK[riskLevel];
  const fragments = pair.fragments || [];
  const t1 = norm(pair.type1_score      ?? 0);
  const t2 = norm(pair.type2_score      ?? 0);
  const t3 = norm(pair.structural_score ?? pair.type3_score ?? 0);
  const t4 = norm(pair.semantic_score   ?? pair.type4_score ?? 0);
  const activeF = fragments[activeFragment];

  return (
    <div className="min-h-screen bg-[#F7F3EE]">

      {/* ── Sticky breadcrumb ── */}
      <div className="bg-white/90 backdrop-blur-sm border-b border-[#E8E1D8] sticky top-16 z-40">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex items-center justify-between gap-4 flex-wrap">
          <div className="flex items-center gap-3">
            <button onClick={() => window.history.back()} className="inline-flex items-center gap-2 text-xs font-semibold text-[#A8A29E] hover:text-[#CF7249] transition-colors">
              <Ico.ArrowLeft /> Report
            </button>
            <span className="text-[#D4CEC8]">·</span>
            <span className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E]">Pair Comparison</span>
          </div>
          <div className={`flex items-center gap-2.5 px-4 py-2 rounded-xl border ${R.bg} ${R.border}`}>
            <span className={`w-2 h-2 rounded-full ${R.bar}`} />
            <span className={`text-xs font-black uppercase tracking-widest ${R.text}`}>
              {R.label} · {Math.round(score * 100)}% similarity
            </span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">

        {/* ── Big heading ── */}
        <div>
          <h1 className="text-5xl font-black text-[#CF7249] tracking-tight leading-none">Code Similarity</h1>
          <p className="text-sm text-[#A8A29E] mt-3">Side-by-side comparison of matching code fragments between two students.</p>
        </div>

        {/* ── Student cards + score ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Student A */}
          <div className="bg-white rounded-3xl border border-[#E8E1D8] px-6 py-6 shadow-sm">
            <p className="text-[10px] font-black uppercase tracking-widest text-blue-500 mb-3">Student A</p>
            <p className="font-black text-[#1A1714] text-xl">{pair.student_a_name || '—'}</p>
            {pair.file_a && <p className="text-[11px] font-mono text-[#A8A29E] truncate mt-2">{pair.file_a}</p>}
            {pair.submission_a_id && (
              <Link to={`/submissions/${pair.submission_a_id}`} className="inline-flex items-center gap-1 text-xs font-black text-[#CF7249] hover:text-[#B85E38] mt-3 transition-colors">
                View submission <Ico.ExternalLink />
              </Link>
            )}
          </div>

          {/* Student B */}
          <div className="bg-white rounded-3xl border border-[#E8E1D8] px-6 py-6 shadow-sm">
            <p className="text-[10px] font-black uppercase tracking-widest text-purple-500 mb-3">Student B</p>
            <p className="font-black text-[#1A1714] text-xl">{pair.student_b_name || '—'}</p>
            {pair.file_b && <p className="text-[11px] font-mono text-[#A8A29E] truncate mt-2">{pair.file_b}</p>}
            {pair.submission_b_id && (
              <Link to={`/submissions/${pair.submission_b_id}`} className="inline-flex items-center gap-1 text-xs font-black text-[#CF7249] hover:text-[#B85E38] mt-3 transition-colors">
                View submission <Ico.ExternalLink />
              </Link>
            )}
          </div>

          {/* Score summary */}
          <div className="bg-white rounded-3xl border border-[#E8E1D8] px-6 py-6 shadow-sm space-y-3.5">
            <p className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E]">Detection Scores</p>
            <ScoreBar label="Overall"    val={score} color={R.bar} />
            <ScoreBar label="Type-1"     val={t1}    color="bg-blue-500"   />
            <ScoreBar label="Type-2"     val={t2}    color="bg-violet-500" />
            <ScoreBar label="Structural" val={t3}    color="bg-amber-500"  />
            <ScoreBar label="Semantic"   val={t4}    color="bg-[#CF7249]"  />
            {pair.confidence && (
              <p className="text-[10px] text-[#A8A29E] pt-2 border-t border-[#F0EBE3]">
                Confidence: <span className="font-black text-[#6B6560]">{pair.confidence}</span>
                {fragments.length > 0 && ` · ${fragments.length} fragment${fragments.length !== 1 ? 's' : ''}`}
              </p>
            )}
          </div>
        </div>

        {/* ── 4-type score cards ── */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label:'Type-1', sub:'Exact copy',            val:t1, color:'bg-blue-500'   },
            { label:'Type-2', sub:'Renamed variables',     val:t2, color:'bg-violet-500' },
            { label:'Type-3', sub:'Structural similarity', val:t3, color:'bg-amber-500'  },
            { label:'Type-4', sub:'Semantic similarity',   val:t4, color:'bg-[#CF7249]'  },
          ].map(({ label, sub, val, color }) => (
            <div key={label} className="bg-white rounded-3xl border border-[#E8E1D8] px-6 py-6 shadow-sm">
              <p className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E] mb-1">{label}</p>
              <p className="text-[10px] text-[#A8A29E] mb-4">{sub}</p>
              <div className="h-2 bg-[#F0EBE3] rounded-full overflow-hidden mb-3">
                <div className={`h-full rounded-full ${color}`} style={{ width: pct(val) }} />
              </div>
              <p className="text-3xl font-black text-[#1A1714]">{pct(val)}</p>
            </div>
          ))}
        </div>

        {/* ── Code comparison section ── */}
        {fragments.length > 0 ? (
          <div className="space-y-6">
            <div className="flex items-end justify-between gap-4 flex-wrap">
              <div>
                <h2 className="text-3xl font-black text-[#CF7249]">Code Comparison</h2>
                <p className="text-sm text-[#A8A29E] mt-1.5">
                  Comparing the most similar files between both students.
                  {fragments[0]?.similar_lines?.length > 0 && ' Orange lines show matching code.'}
                </p>
              </div>

              {fragments.length > 1 && (
                <div className="flex items-center gap-2">
                  <button disabled={activeFragment === 0}
                    onClick={() => setActiveFragment(i => i - 1)}
                    className="w-9 h-9 rounded-xl border border-[#E8E1D8] bg-white flex items-center justify-center text-[#6B6560] hover:bg-[#F7F3EE] disabled:opacity-30 transition-colors">
                    <Ico.ChevronLeft />
                  </button>
                  <span className="text-sm font-black text-[#1A1714] px-2">{activeFragment+1} / {fragments.length}</span>
                  <button disabled={activeFragment === fragments.length - 1}
                    onClick={() => setActiveFragment(i => i + 1)}
                    className="w-9 h-9 rounded-xl border border-[#E8E1D8] bg-white flex items-center justify-center text-[#6B6560] hover:bg-[#F7F3EE] disabled:opacity-30 transition-colors">
                    <Ico.ChevronRight />
                  </button>
                </div>
              )}
            </div>

            {/* Fragment pills */}
            {fragments.length > 1 && (
              <div className="flex flex-wrap gap-2">
                {fragments.map((f, i) => (
                  <button key={i} onClick={() => setActiveFragment(i)}
                    className={`px-4 py-2 rounded-xl text-xs font-black transition-all
                      ${activeFragment === i
                        ? 'bg-[#CF7249] text-white shadow-sm'
                        : 'bg-white border border-[#E8E1D8] text-[#6B6560] hover:border-[#CF7249]/30'}`}>
                    Fragment {i+1}
                    {f.similarity != null && <span className="ml-1.5 opacity-60">{Math.round(norm(f.similarity)*100)}%</span>}
                  </button>
                ))}
              </div>
            )}

            {activeF && (
              <CodeViewer key={activeFragment} fragmentIndex={activeFragment} total={fragments.length} fragA={activeF} fragB={activeF} />
            )}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-24 rounded-3xl border border-dashed border-[#E8E1D8] text-center bg-white">
            <div className="w-16 h-16 rounded-2xl bg-[#F7F3EE] flex items-center justify-center mb-5">
              <Ico.FileText />
            </div>
            <p className="font-black text-[#1A1714] text-lg mb-2">File content unavailable</p>
            <p className="text-sm text-[#A8A29E] max-w-sm leading-relaxed">
              Source files could not be read from disk. Make sure the analysis-engine container is running and files are mounted correctly.
            </p>
          </div>
        )}

        {/* ── Bottom actions ── */}
        <div className="flex gap-3 pt-4 border-t border-[#E8E1D8] flex-wrap">
          {pair.submission_a_id && (
            <Link to={`/submissions/${pair.submission_a_id}`}
              className="px-5 py-3 rounded-2xl border border-[#E8E1D8] bg-white text-sm font-black text-[#6B6560] hover:bg-[#F7F3EE] transition-colors">
              Open Submission A
            </Link>
          )}
          {pair.submission_b_id && (
            <Link to={`/submissions/${pair.submission_b_id}`}
              className="px-5 py-3 rounded-2xl border border-[#E8E1D8] bg-white text-sm font-black text-[#6B6560] hover:bg-[#F7F3EE] transition-colors">
              Open Submission B
            </Link>
          )}
          <button onClick={() => window.print()}
            className="ml-auto flex items-center gap-2 px-5 py-3 rounded-2xl bg-[#CF7249] text-white text-sm font-black hover:bg-[#B85E38] transition-colors shadow-sm">
            <Ico.Printer /> Export / Print
          </button>
        </div>
      </div>
    </div>
  );
}
