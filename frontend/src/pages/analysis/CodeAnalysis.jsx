import React, { useState, useCallback } from 'react';
import { Link } from 'react-router-dom';
import analysisService from '../../services/analysisService';

// ─── Constants ─────────────────────────────────────────────────────────────────
const EXT_LANG = {
  '.cpp':'C++','.c':'C','.h':'C/C++','.hpp':'C++','.cc':'C++','.cxx':'C++',
  '.java':'Java','.py':'Python',
  '.js':'JavaScript','.jsx':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript',
};
const LANG_COLORS = {
  'C++':'bg-blue-100 text-blue-700','C':'bg-sky-100 text-sky-700',
  'C/C++':'bg-sky-100 text-sky-700','Java':'bg-orange-100 text-orange-700',
  'Python':'bg-yellow-100 text-yellow-700','JavaScript':'bg-amber-100 text-amber-700',
  'TypeScript':'bg-indigo-100 text-indigo-700',
};
const RISK = {
  CRITICAL:{ label:'Critical', bg:'bg-red-100',    text:'text-red-700',    bar:'bg-red-500',    ring:'ring-red-300'    },
  HIGH:    { label:'High',     bg:'bg-orange-100', text:'text-orange-700', bar:'bg-orange-400', ring:'ring-orange-300' },
  MEDIUM:  { label:'Medium',   bg:'bg-amber-100',  text:'text-amber-700',  bar:'bg-amber-400',  ring:'ring-amber-300'  },
  LOW:     { label:'Low',      bg:'bg-blue-100',   text:'text-blue-600',   bar:'bg-blue-400',   ring:'ring-blue-300'   },
  NONE:    { label:'Clean',    bg:'bg-gray-100',   text:'text-gray-500',   bar:'bg-gray-300',   ring:'ring-gray-300'   },
};

const getExt  = n => '.' + n.split('.').pop().toLowerCase();
const isZipF  = n => n.toLowerCase().endsWith('.zip');
const fmtSize = b => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(1)} KB`;
const pct     = n => `${Math.round((n||0)*100)}%`;

function getRisk(score) {
  const s = typeof score === 'number' ? score : 0;
  if (s >= 0.85) return 'CRITICAL';
  if (s >= 0.70) return 'HIGH';
  if (s >= 0.50) return 'MEDIUM';
  if (s >= 0.30) return 'LOW';
  return 'NONE';
}

function groupByLang(files) {
  const g = {};
  files.filter(f => !isZipF(f.name)).forEach(f => {
    const lang = EXT_LANG[getExt(f.name)] || 'Other';
    g[lang] = (g[lang] || 0) + 1;
  });
  return g;
}

// ─── Side-by-side code diff (dark theme) ─────────────────────────────────────
const CodeDiff = ({ fragA, fragB }) => {
  const linesA = (fragA?.source || '').split('\n');
  const linesB = (fragB?.source || '').split('\n');
  const simSet = new Set(fragA?.similar_lines || []);

  const col = (lines, label, meta) => (
    <div className="flex-1 min-w-0 overflow-x-auto">
      <div className="bg-gray-900 px-4 py-2.5 border-b border-gray-700 sticky top-0">
        <p className="text-[9px] font-black uppercase tracking-widest text-gray-500 mb-0.5">{label}</p>
        <p className="text-xs font-bold text-gray-200 truncate font-mono">{meta?.file || '—'}</p>
        {meta?.name && (
          <p className="text-[10px] text-gray-500 mt-0.5 font-mono">
            {meta.name}(){meta.start ? ` · L${meta.start}–${meta.end}` : ''}
          </p>
        )}
      </div>
      <div className="font-mono text-xs leading-[22px] bg-gray-950">
        {lines.map((line, i) => (
          <div key={i} className={`flex ${simSet.has(i) ? 'bg-yellow-500/10 border-l-2 border-yellow-400' : ''}`}>
            <span className="select-none text-gray-600 w-10 text-right pr-3 py-px flex-shrink-0 bg-gray-900/40">
              {i + 1}
            </span>
            <pre className={`flex-1 px-3 py-px whitespace-pre-wrap break-all
              ${simSet.has(i) ? 'text-yellow-100' : 'text-gray-400'}`}>{line || ' '}</pre>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="rounded-xl overflow-hidden border border-gray-800">
      <div className="grid grid-cols-2 divide-x divide-gray-800 max-h-80 overflow-auto">
        {col(linesA, 'File A', fragA)}
        {col(linesB, 'File B', fragB)}
      </div>
    </div>
  );
};

// ─── Expandable pair card ─────────────────────────────────────────────────────
const PairCard = ({ pair, index }) => {
  const [open, setOpen] = useState(false);
  const score = pair.combined_score ?? pair.similarity ?? 0;
  const R = RISK[getRisk(score)];

  const fragments = (() => {
    try {
      const mb = pair.matching_blocks;
      if (!mb) return [];
      const p = typeof mb === 'string' ? JSON.parse(mb) : mb;
      return Array.isArray(p) ? p : (p.fragments || []);
    } catch { return []; }
  })();

  return (
    <div className={`rounded-2xl border overflow-hidden transition-all
      ${open ? 'border-gray-700 shadow-xl shadow-black/20' : 'border-gray-800 hover:border-gray-600'}`}>

      {/* Header row */}
      <button onClick={() => setOpen(o => !o)}
        className="w-full text-left px-5 py-4 bg-gray-900 flex items-center gap-4">
        <span className="text-xs font-black text-gray-600 w-6 flex-shrink-0">#{index + 1}</span>

        {/* Score ring */}
        <div className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0
          font-black text-sm ring-2 ${R.ring} ${R.bg} ${R.text}`}>
          {Math.round(score * 100)}%
        </div>

        {/* File names */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm font-bold text-gray-100 truncate max-w-[200px]">
              {pair.file_a || pair.student_a_name || 'File A'}
            </span>
            <span className="text-gray-600 text-xs font-bold">vs</span>
            <span className="text-sm font-bold text-gray-100 truncate max-w-[200px]">
              {pair.file_b || pair.student_b_name || 'File B'}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-1.5 flex-wrap">
            <span className={`inline-flex items-center gap-1 text-[10px] font-black uppercase tracking-widest px-2 py-0.5 rounded-full ${R.bg} ${R.text}`}>
              <span className={`w-1.5 h-1.5 rounded-full ${R.bar}`} /> {R.label}
            </span>
            {fragments.length > 0 && (
              <span className="text-[10px] text-gray-500">
                {fragments.length} matching fragment{fragments.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>

        {/* Mini score bars — hidden on small screens */}
        <div className="hidden lg:flex flex-col gap-1.5 min-w-[140px]">
          {[
            { l:'Structural', v: pair.structural_score ?? pair.type3_score },
            { l:'Semantic',   v: pair.semantic_score   ?? pair.type4_score },
          ].map(({ l, v }) => (
            <div key={l} className="flex items-center gap-2 text-[10px] text-gray-500">
              <span className="w-16 text-right">{l}</span>
              <div className="flex-1 h-1 bg-gray-800 rounded-full overflow-hidden">
                <div className="h-full bg-slate-400 rounded-full" style={{ width: pct(v) }} />
              </div>
              <span className="text-gray-400 w-8 text-right">{pct(v)}</span>
            </div>
          ))}
        </div>

        {/* Chevron */}
        <svg className={`w-4 h-4 text-gray-500 flex-shrink-0 transition-transform ${open ? 'rotate-180' : ''}`}
          fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Expanded detail */}
      {open && (
        <div className="bg-gray-950 border-t border-gray-800 p-5 space-y-5">

          {/* 4-type breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[
              { label:'Type-1', sub:'Exact copy',   val: pair.type1_score,                          color:'bg-blue-500'   },
              { label:'Type-2', sub:'Renamed vars', val: pair.type2_score,                          color:'bg-violet-500' },
              { label:'Type-3', sub:'Structural',   val: pair.structural_score ?? pair.type3_score, color:'bg-amber-500'  },
              { label:'Type-4', sub:'Semantic',     val: pair.semantic_score   ?? pair.type4_score,  color:'bg-rose-500'   },
            ].map(({ label, sub, val, color }) => (
              <div key={label} className="bg-gray-900 rounded-xl border border-gray-800 px-4 py-3">
                <p className="text-[10px] font-black uppercase tracking-widest text-gray-500">{label}</p>
                <p className="text-[10px] text-gray-600 mb-2">{sub}</p>
                <div className="h-1 bg-gray-800 rounded-full overflow-hidden mb-1.5">
                  <div className={`h-full rounded-full ${color}`} style={{ width: val ? pct(val) : '0%' }} />
                </div>
                <p className="text-xl font-black text-gray-100">{val != null ? pct(val) : '—'}</p>
              </div>
            ))}
          </div>

          {/* Fragment diffs */}
          {fragments.length > 0 ? (
            <div className="space-y-4">
              <p className="text-[10px] font-black uppercase tracking-widest text-gray-500">
                Matching Fragments ({fragments.length})
              </p>
              {fragments.slice(0, 4).map((frag, i) => (
                <div key={i}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-yellow-400/20 text-yellow-300 border border-yellow-400/30">
                      Fragment {i + 1}
                      {frag.similarity ? ` · ${Math.round(frag.similarity * 100)}% match` : ''}
                    </span>
                    {frag.func_a && (
                      <span className="text-[10px] text-gray-600 font-mono">{frag.func_a}()</span>
                    )}
                  </div>
                  <CodeDiff
                    fragA={{
                      file: frag.file_a, name: frag.func_a,
                      start: frag.start_a, end: frag.end_a,
                      source: frag.source_a, similar_lines: frag.similar_lines,
                    }}
                    fragB={{
                      file: frag.file_b, name: frag.func_b,
                      start: frag.start_b, end: frag.end_b,
                      source: frag.source_b,
                    }}
                  />
                </div>
              ))}
              {fragments.length > 4 && (
                <p className="text-xs text-gray-600 text-center py-2">
                  +{fragments.length - 4} more fragments not shown
                </p>
              )}
            </div>
          ) : (
            <div className="rounded-xl border border-gray-800 bg-gray-900 px-5 py-4 text-sm text-gray-500">
              No fragment-level data for this pair. The engine may need to run in detailed mode.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ─── Stat card ────────────────────────────────────────────────────────────────
const StatCard = ({ label, value, sub, warn }) => (
  <div className="bg-gray-900 rounded-2xl border border-gray-800 px-5 py-4">
    <p className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-1">{label}</p>
    <p className={`text-3xl font-black tracking-tight ${warn ? 'text-red-400' : 'text-gray-100'}`}>{value}</p>
    {sub && <p className="text-xs text-gray-600 mt-1">{sub}</p>}
  </div>
);

// ─── File chip ────────────────────────────────────────────────────────────────
const FileChip = ({ file, onRemove }) => {
  const lang = EXT_LANG[getExt(file.name)];
  const zip  = isZipF(file.name);
  return (
    <div className="flex items-center gap-2.5 px-3 py-2 rounded-xl bg-gray-800 border border-gray-700 group">
      <span className="text-base flex-shrink-0">{zip ? '📦' : '📄'}</span>
      <div className="flex-1 min-w-0">
        <p className="text-xs font-semibold text-gray-200 truncate">{file.name}</p>
        <div className="flex items-center gap-1.5 mt-0.5">
          <span className="text-[10px] text-gray-500">{fmtSize(file.size)}</span>
          {lang && (
            <span className={`text-[9px] font-bold px-1.5 py-px rounded-md ${LANG_COLORS[lang] || 'bg-gray-700 text-gray-300'}`}>
              {lang}
            </span>
          )}
          {zip && (
            <span className="text-[9px] font-bold px-1.5 py-px rounded-md bg-violet-900 text-violet-300">ZIP</span>
          )}
        </div>
      </div>
      <button type="button" onClick={onRemove}
        className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 transition-all text-xs font-bold px-1">
        ✕
      </button>
    </div>
  );
};

// ─── Detector type toggle ─────────────────────────────────────────────────────
const DetectorToggle = ({ typeNum, label, desc, enabled, onToggle }) => {
  const colors = { 1:'blue', 2:'violet', 3:'amber', 4:'rose' };
  const c = colors[typeNum];
  return (
    <button type="button" onClick={onToggle}
      className={`p-4 rounded-xl border-2 text-left transition-all
        ${enabled
          ? `border-${c}-600 bg-${c}-950/30`
          : 'border-gray-800 bg-gray-900/60 hover:border-gray-700'}`}>
      <div className="flex justify-between items-start mb-1.5">
        <span className={`text-[10px] font-black uppercase tracking-widest
          ${enabled ? `text-${c}-400` : 'text-gray-600'}`}>
          Type-{typeNum}
        </span>
        <div className={`w-4 h-4 rounded-full border-2 transition-all
          ${enabled ? `border-${c}-400 bg-${c}-400` : 'border-gray-700'}`} />
      </div>
      <p className={`text-xs font-bold ${enabled ? 'text-gray-100' : 'text-gray-500'}`}>{label}</p>
      <p className={`text-[10px] mt-0.5 leading-relaxed ${enabled ? 'text-gray-500' : 'text-gray-700'}`}>{desc}</p>
    </button>
  );
};

// ─── Main page ────────────────────────────────────────────────────────────────
export default function CodeAnalysis() {
  const [files,     setFiles]     = useState([]);
  const [detectors, setDetectors] = useState({ t1:true, t2:true, t3:true, t4:false });
  const [running,   setRunning]   = useState(false);
  const [results,   setResults]   = useState(null);
  const [error,     setError]     = useState('');
  const [filter,    setFilter]    = useState('all');
  const [threshold, setThreshold] = useState(0.40);
  const [dragging,  setDragging]  = useState(false);
  const [progress,  setProgress]  = useState('');

  const ALLOWED = '.cpp,.c,.h,.hpp,.cc,.cxx,.java,.py,.js,.jsx,.ts,.tsx,.zip';

  const addFiles = useCallback((incoming) => {
    setError('');
    const existingNames = new Set(files.map(f => f.name));
    const unique = Array.from(incoming).filter(f => !existingNames.has(f.name));
    setFiles(prev => [...prev, ...unique]);
  }, [files]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer?.files?.length) addFiles(e.dataTransfer.files);
  }, [addFiles]);

  const toggleDetector = (key) => setDetectors(d => ({ ...d, [key]: !d[key] }));

  const handleAnalyze = async () => {
    if (files.length < 2) { setError('Upload at least 2 files to compare.'); return; }
    setRunning(true); setError(''); setResults(null); setProgress('Uploading files…');
    try {
      const form = new FormData();
      files.forEach(f => form.append('files', f));
      form.append('types', JSON.stringify(detectors));
      form.append('mode', 'detailed');
      setProgress('Analyzing — extracting fragments…');
      const data = await analysisService.analyzeFiles(form);
      setProgress('');
      setResults(data);
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Analysis failed. Check engine connection.');
      setProgress('');
    } finally {
      setRunning(false);
    }
  };

  // ── Derived state ────────────────────────────────────────────────────────────
  const rawPairs = results
    ? (results.highSimilarityPairs || results.all_pairs || results.pairs || [])
    : [];

  const filtered = rawPairs
    .filter(p => {
      const s = p.combined_score ?? p.similarity ?? 0;
      if (filter === 'critical') return s >= 0.85;
      if (filter === 'high')     return s >= 0.70;
      if (filter === 'medium')   return s >= 0.50 && s < 0.70;
      return s >= threshold;
    })
    .sort((a, b) =>
      (b.combined_score ?? b.similarity ?? 0) - (a.combined_score ?? a.similarity ?? 0)
    );

  const criticalCount = rawPairs.filter(p => getRisk(p.combined_score ?? p.similarity ?? 0) === 'CRITICAL').length;
  const highCount     = rawPairs.filter(p => getRisk(p.combined_score ?? p.similarity ?? 0) === 'HIGH').length;
  const avgScore = rawPairs.length
    ? rawPairs.reduce((s, p) => s + (p.combined_score ?? p.similarity ?? 0), 0) / rawPairs.length
    : 0;

  const langGroups = groupByLang(files);

  // ── Render ───────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-950 text-gray-100"
      style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&display=swap');
        input[type=range]::-webkit-slider-thumb {
          -webkit-appearance: none; width: 16px; height: 16px;
          border-radius: 50%; background: #f1f5f9; cursor: pointer;
        }
        input[type=range]::-webkit-slider-runnable-track {
          height: 4px; border-radius: 2px; background: #1e293b;
        }
      `}</style>

      {/* Nav bar */}
      <div className="border-b border-gray-800 bg-gray-900/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/dashboard"
              className="flex items-center gap-1.5 text-xs font-semibold text-gray-500 hover:text-gray-300 transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Dashboard
            </Link>
            <span className="text-gray-700">·</span>
            <span className="text-xs font-black uppercase tracking-widest text-gray-400">Code Analysis</span>
          </div>
          <span className="text-xs font-black text-gray-700">CodeSpectra // Detector</span>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-6 py-10">

        {/* Hero */}
        <div className="mb-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800 border border-slate-700 text-xs font-bold text-slate-400 mb-4">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            No assignment required — analyze any files directly
          </div>
          <h1 className="text-4xl font-black tracking-tight text-gray-100 mb-2">Code Analysis</h1>
          <p className="text-gray-500 text-base max-w-xl">
            Drop any mix of code files or ZIPs. Files are grouped by language —
            every same-language pair is checked across all 4 detector types.
            Fragments, functions, and lines are compared side-by-side.
          </p>
        </div>

        <div className="grid lg:grid-cols-5 gap-8">

          {/* ── Left panel: upload + config ── */}
          <div className="lg:col-span-2 space-y-5">

            {/* Drop zone */}
            <div
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer
                ${dragging
                  ? 'border-slate-400 bg-slate-800/40'
                  : files.length
                    ? 'border-emerald-700 bg-emerald-950/20'
                    : 'border-gray-700 hover:border-gray-500 bg-gray-900/50'}`}>
              <div className={`text-4xl mb-3 transition-transform ${dragging ? 'scale-110' : ''}`}>
                {files.length > 0 ? '📂' : '⬆️'}
              </div>
              <p className="text-sm font-bold text-gray-300 mb-1">
                {files.length > 0
                  ? `${files.length} file${files.length !== 1 ? 's' : ''} ready`
                  : 'Drop code files or ZIPs here'}
              </p>
              <p className="text-xs text-gray-600 mb-4">
                .cpp .java .py .js .ts · or a .zip archive
              </p>
              <label className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-700 text-white text-xs font-bold hover:bg-slate-600 cursor-pointer transition-colors">
                Browse files
                <input type="file" multiple className="hidden" accept={ALLOWED}
                  onChange={e => {
                    if (e.target.files?.length) addFiles(e.target.files);
                    e.target.value = '';
                  }} />
              </label>
            </div>

            {/* File list */}
            {files.length > 0 && (
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <p className="text-[10px] font-black uppercase tracking-widest text-gray-500">
                    Files ({files.length})
                  </p>
                  <button onClick={() => { setFiles([]); setResults(null); }}
                    className="text-xs text-red-500 hover:text-red-400 font-semibold">
                    Clear all
                  </button>
                </div>

                <div className="space-y-1.5 max-h-52 overflow-y-auto pr-1">
                  {files.map((f, i) => (
                    <FileChip key={i} file={f}
                      onRemove={() => setFiles(p => p.filter((_, x) => x !== i))} />
                  ))}
                </div>

                {/* Language pool preview */}
                {Object.keys(langGroups).length > 0 && (
                  <div className="pt-2 space-y-1.5">
                    <p className="text-[10px] font-black uppercase tracking-widest text-gray-600">
                      Language pools (compared independently)
                    </p>
                    {Object.entries(langGroups).map(([lang, count]) => (
                      <div key={lang} className="flex items-center justify-between">
                        <span className={`text-[10px] font-bold px-1.5 py-px rounded-md
                          ${LANG_COLORS[lang] || 'bg-gray-800 text-gray-400'}`}>
                          {lang}
                        </span>
                        <span className="text-[10px] text-gray-600">
                          {count} file{count !== 1 ? 's' : ''}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Detection type toggles */}
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest text-gray-500 mb-3">
                Detection Types
              </p>
              <div className="grid grid-cols-2 gap-2">
                <DetectorToggle typeNum={1} label="Exact Copies"  desc="Whitespace & comment changes"  enabled={detectors.t1} onToggle={() => toggleDetector('t1')} />
                <DetectorToggle typeNum={2} label="Renamed Vars"  desc="Identifier renaming"            enabled={detectors.t2} onToggle={() => toggleDetector('t2')} />
                <DetectorToggle typeNum={3} label="Near-Miss"     desc="Modified statements & fragments" enabled={detectors.t3} onToggle={() => toggleDetector('t3')} />
                <DetectorToggle typeNum={4} label="Semantic / AI" desc="Same algorithm, different code"  enabled={detectors.t4} onToggle={() => toggleDetector('t4')} />
              </div>
            </div>

            {/* Error message */}
            {error && (
              <div className="px-4 py-3 rounded-xl bg-red-950/50 border border-red-800 text-xs text-red-400 font-medium">
                ⚠ {error}
              </div>
            )}

            {/* Run button */}
            <button onClick={handleAnalyze} disabled={running || files.length < 2}
              className="w-full py-4 rounded-xl font-black text-sm bg-white text-gray-950
                         hover:bg-gray-100 disabled:opacity-30 disabled:cursor-not-allowed
                         shadow-lg shadow-white/5 transition-all">
              {running ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-gray-950 border-t-transparent rounded-full animate-spin" />
                  {progress || 'Analyzing…'}
                </span>
              ) : '⚡ Run Analysis'}
            </button>

            {files.length === 1 && (
              <p className="text-[10px] text-center text-gray-600">
                Need at least 2 files to compare.
              </p>
            )}
          </div>

          {/* ── Right panel: results ── */}
          <div className="lg:col-span-3 space-y-5">

            {/* Idle */}
            {!results && !running && (
              <div className="flex flex-col items-center justify-center h-80 rounded-2xl border border-dashed border-gray-800 text-center">
                <span className="text-5xl mb-4">🔬</span>
                <p className="font-bold text-gray-500 text-base">Results appear here</p>
                <p className="text-xs text-gray-700 mt-1 max-w-xs">
                  Upload at least 2 files, choose detector types, then click Run Analysis.
                  Same-language files are paired automatically.
                </p>
              </div>
            )}

            {/* Running */}
            {running && (
              <div className="flex flex-col items-center justify-center h-80 rounded-2xl border border-gray-800 bg-gray-900/50">
                <div className="w-10 h-10 border-2 border-white border-t-transparent rounded-full animate-spin mb-4" />
                <p className="font-bold text-gray-300 text-sm">{progress || 'Analyzing…'}</p>
                <p className="text-xs text-gray-600 mt-1">Extracting fragments, comparing pairs across all detectors…</p>
              </div>
            )}

            {/* Results */}
            {results && !running && (
              <>
                {/* Stats row */}
                <div className="grid grid-cols-4 gap-3">
                  <StatCard label="Total Pairs"   value={rawPairs.length} />
                  <StatCard label="Critical ≥85%" value={criticalCount} warn={criticalCount > 0} sub="needs review" />
                  <StatCard label="High 70–85%"   value={highCount}     warn={highCount > 0} />
                  <StatCard label="Avg Score"     value={pct(avgScore)} />
                </div>

                {/* Critical alert */}
                {criticalCount > 0 && (
                  <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-red-950/60 border border-red-800">
                    <span className="text-xl flex-shrink-0">🚨</span>
                    <p className="text-sm text-red-300 font-semibold">
                      {criticalCount} pair{criticalCount !== 1 ? 's' : ''} with ≥85% similarity — immediate review recommended.
                    </p>
                  </div>
                )}

                {/* Filter controls */}
                <div className="flex flex-wrap items-center gap-3">
                  <div className="flex items-center gap-2 bg-gray-900 border border-gray-700 rounded-xl px-3 py-2">
                    <span className="text-xs text-gray-500 font-bold flex-shrink-0">Min</span>
                    <input type="range" min="0" max="1" step="0.05" value={threshold}
                      onChange={e => setThreshold(parseFloat(e.target.value))}
                      className="w-24 accent-white" />
                    <span className="text-xs font-black text-white w-8">{Math.round(threshold * 100)}%</span>
                  </div>
                  <div className="flex gap-1">
                    {[
                      { v:'all',      l:'All'      },
                      { v:'critical', l:'Critical' },
                      { v:'high',     l:'High'     },
                      { v:'medium',   l:'Medium'   },
                    ].map(({ v, l }) => (
                      <button key={v} onClick={() => setFilter(v)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all
                          ${filter === v
                            ? 'bg-white text-gray-950'
                            : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}>
                        {l}
                      </button>
                    ))}
                  </div>
                  <span className="text-xs text-gray-600 ml-auto">{filtered.length} pair{filtered.length !== 1 ? 's' : ''} shown</span>
                </div>

                {/* Pair list */}
                {filtered.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-16 rounded-2xl border border-dashed border-gray-800 text-center">
                    <span className="text-4xl mb-3">✅</span>
                    <p className="font-bold text-gray-500">No pairs above {Math.round(threshold * 100)}%</p>
                    <p className="text-xs text-gray-700 mt-1">Lower the threshold or change the filter.</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filtered.map((pair, i) => (
                      <PairCard key={pair.pair_id || i} pair={pair} index={i} />
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}