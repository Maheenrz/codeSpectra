import React, { useState, useCallback, useEffect } from 'react';
import api from '../../utils/api';

const EXT_LANG = {
  '.cpp':'C++', '.c':'C', '.h':'C/C++', '.hpp':'C++', '.cc':'C++', '.cxx':'C++',
  '.java':'Java', '.kt':'Kotlin', '.kts':'Kotlin',
  '.py':'Python',
  '.js':'JavaScript', '.jsx':'JavaScript', '.ts':'TypeScript', '.tsx':'TypeScript',
};
const LANG_PILL = {
  'C++':        { bg:'#FEF3EC', color:'#CF7249' },
  'C':          { bg:'#FEF3EC', color:'#CF7249' },
  'C/C++':      { bg:'#FEF3EC', color:'#CF7249' },
  'Java':       { bg:'#FAEDEC', color:'#C4827A' },
  'Python':     { bg:'#EBF4F4', color:'#2D6A6A' },
  'JavaScript': { bg:'#EFF2F7', color:'#8B9BB4' },
  'TypeScript': { bg:'#EFF2F7', color:'#8B9BB4' },
  'Kotlin':     { bg:'#EEEDFE', color:'#534AB7' },
};
const RISK = {
  CRITICAL: { label:'Critical', color:'#CF7249', bg:'#FEF3EC', border:'#CF7249' },
  HIGH:     { label:'High',     color:'#C4827A', bg:'#FAEDEC', border:'#C4827A' },
  MEDIUM:   { label:'Medium',   color:'#2D6A6A', bg:'#EBF4F4', border:'#2D6A6A' },
  LOW:      { label:'Low',      color:'#8B9BB4', bg:'#EFF2F7', border:'#8B9BB4' },
  NONE:     { label:'Clean',    color:'#A8A29E', bg:'#F7F3EE', border:'#E8E1D8' },
};
const getExt  = n => '.' + n.split('.').pop().toLowerCase();
const isZip   = n => n.toLowerCase().endsWith('.zip');
const fmtSize = b => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(1)} KB`;
const pct     = n => `${Math.round((n || 0) * 100)}%`;
const CODE_EXTS = new Set(['.cpp','.c','.h','.hpp','.cc','.cxx','.java','.kt','.kts','.py','.js','.jsx','.ts','.tsx','.zip']);

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
  files.filter(f => !isZip(f.name)).forEach(f => {
    const lang = EXT_LANG[getExt(f.name)] || 'Other';
    g[lang] = (g[lang] || 0) + 1;
  });
  return g;
}

const IcoUpload   = () => <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>;
const IcoFolder   = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>;
const IcoFile     = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>;
const IcoZip      = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>;
const IcoX        = () => <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;
const IcoChevron  = ({ open }) => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24" style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}><polyline points="6 9 12 15 18 9"/></svg>;
const IcoScan     = () => <svg width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/><line x1="7" y1="12" x2="17" y2="12"/></svg>;
const IcoDownload = () => <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>;
const IcoAlert    = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;
const IcoCheck    = () => <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>;

const UploadIllustration = () => (
  <svg width="72" height="72" viewBox="0 0 72 72" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect x="8" y="20" width="36" height="44" rx="6" fill="#FEF3EC" stroke="#CF7249" strokeWidth="1.8"/>
    <rect x="28" y="8" width="36" height="44" rx="6" fill="white" stroke="#E8D5C8" strokeWidth="1.8"/>
    <line x1="35" y1="22" x2="57" y2="22" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <line x1="35" y1="30" x2="52" y2="30" stroke="#CF7249" strokeWidth="2" strokeLinecap="round" opacity="0.6"/>
    <line x1="35" y1="38" x2="55" y2="38" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <circle cx="54" cy="54" r="13" fill="#CF7249"/>
    <path d="M54 60V48M49 53l5-5 5 5" stroke="white" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const CodeDiff = ({ fragA, fragB }) => {
  const linesA = (fragA?.source || '').split('\n');
  const linesB = (fragB?.source || '').split('\n');
  const simSet = new Set(fragA?.similar_lines || []);

  const col = (lines, label, meta) => (
    <div style={{ flex:1, minWidth:0, overflowX:'auto' }}>
      <div style={{ background:'#1A1714', padding:'10px 16px', borderBottom:'1px solid #2D2825', position:'sticky', top:0 }}>
        <p style={{ fontSize:9, fontWeight:700, textTransform:'uppercase', letterSpacing:'0.15em', color:'#6B6560', marginBottom:2 }}>{label}</p>
        <p style={{ fontSize:11, fontWeight:600, color:'#F7F3EE', fontFamily:'monospace', overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{meta?.file || '—'}</p>
        {meta?.name && <p style={{ fontSize:10, color:'#6B6560', fontFamily:'monospace', marginTop:2 }}>{meta.name}(){meta.start ? ` · L${meta.start}–${meta.end}` : ''}</p>}
      </div>
      <div style={{ fontFamily:'monospace', fontSize:11, lineHeight:'22px', background:'#0F0D0B' }}>
        {lines.map((line, i) => (
          <div key={i} style={{ display:'flex', background:simSet.has(i)?'rgba(207,114,73,0.12)':'transparent', borderLeft:simSet.has(i)?'2px solid #CF7249':'2px solid transparent' }}>
            <span style={{ userSelect:'none', color:'#4A4540', width:36, textAlign:'right', paddingRight:12, paddingTop:1, flexShrink:0, background:'rgba(26,23,20,0.4)' }}>{i+1}</span>
            <pre style={{ flex:1, padding:'1px 12px', whiteSpace:'pre-wrap', wordBreak:'break-all', margin:0, color:simSet.has(i)?'#F7D5BF':'#8B7D72' }}>{line||' '}</pre>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div style={{ borderRadius:12, overflow:'hidden', border:'1px solid #E8E1D8' }}>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', maxHeight:280, overflow:'auto' }}>
        {col(linesA, 'File A', fragA)}
        <div style={{ borderLeft:'1px solid #2D2825' }}>{col(linesB, 'File B', fragB)}</div>
      </div>
    </div>
  );
};

const PairCard = ({ pair, index, getScore }) => {
  const [open, setOpen] = useState(false);
  const score = getScore(pair);
  const R = RISK[getRisk(score)];
  const t1 = pair.type1_score ?? 0;
  const t2 = pair.type2_score ?? 0;
  const t3 = pair.structural_score ?? pair.structural?.score ?? 0;
  const t4 = pair.semantic_score   ?? pair.semantic?.score   ?? 0;
  const cloneLabel = (() => {
    const raw = pair.primary_clone_type || pair.clone_type || '';
    if (raw === 'cross_layer') return 'Cross-Layer';
    return raw.replace('type', 'Type-');
  })();
  const fragments = (() => {
    if (Array.isArray(pair.fragments) && pair.fragments.length > 0) return pair.fragments;
    try {
      const mb = pair.matching_blocks;
      if (!mb) return [];
      const parsed = typeof mb === 'string' ? JSON.parse(mb) : mb;
      return Array.isArray(parsed) ? parsed : (parsed.fragments || []);
    } catch { return []; }
  })();

  return (
    <div className="bg-white rounded-2xl border-2 overflow-hidden transition-all duration-150"
      style={{ borderColor: open ? R.border : '#E8E1D8', boxShadow: open ? '0 4px 20px rgba(0,0,0,0.07)' : 'none' }}>
      <button onClick={() => setOpen(o => !o)}
        className="w-full text-left px-6 py-5 flex items-center gap-4 bg-white border-none cursor-pointer">
        <span className="text-xs font-bold text-[#C4B8AE] w-6 flex-shrink-0">#{index+1}</span>
        <div className="w-14 h-14 rounded-2xl flex items-center justify-center flex-shrink-0 font-black text-base border-2"
          style={{ background:R.bg, color:R.color, borderColor:R.border }}>
          {Math.round(score * 100)}%
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap mb-1.5">
            <span className="text-sm font-bold text-[#1A1714] truncate max-w-[160px]">{pair.file_a || 'File A'}</span>
            <span className="text-xs text-[#A8A29E] font-semibold">vs</span>
            <span className="text-sm font-bold text-[#1A1714] truncate max-w-[160px]">{pair.file_b || 'File B'}</span>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full inline-flex items-center gap-1.5"
              style={{ background:R.bg, color:R.color }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background:R.color }}/>
              {R.label}
            </span>
            {cloneLabel && cloneLabel !== 'Type-none' && (
              <span className="text-[10px] font-bold px-2 py-1 rounded-md bg-[#F7F3EE] text-[#6B6560] border border-[#E8E1D8]">{cloneLabel}</span>
            )}
            {fragments.length > 0 && (
              <span className="text-xs text-[#A8A29E]">{fragments.length} fragment{fragments.length !== 1 ? 's' : ''}</span>
            )}
          </div>
        </div>
        <div className="hidden md:flex flex-col gap-1 w-32 flex-shrink-0">
          <span className="text-[10px] text-[#A8A29E] font-semibold">Structural</span>
          <div className="h-2 bg-[#F0EBE3] rounded-full overflow-hidden">
            <div className="h-full rounded-full" style={{ width:pct(t3), background:R.color }}/>
          </div>
          <span className="text-xs font-bold" style={{ color:R.color }}>{pct(t3)}</span>
        </div>
        <IcoChevron open={open}/>
      </button>

      {open && (
        <div className="border-t-2 border-[#F0EBE3] bg-[#FDFCFB] p-6 space-y-5">
          <div className="grid grid-cols-4 gap-3">
            {[
              { label:'Type-1', sub:'Exact copy',   val:t1, color:'#CF7249', bg:'#FEF3EC' },
              { label:'Type-2', sub:'Renamed vars',  val:t2, color:'#2D6A6A', bg:'#EBF4F4' },
              { label:'Type-3', sub:'Structural',    val:t3, color:'#C4827A', bg:'#FAEDEC' },
              { label:'Type-4', sub:'Semantic/I/O',  val:t4, color:'#8B9BB4', bg:'#EFF2F7' },
            ].map(({ label, sub, val, color, bg }) => (
              <div key={label} className="rounded-xl p-4 border border-[#E8E1D8] bg-white">
                <p className="text-[9px] font-black uppercase tracking-widest mb-0.5" style={{ color }}>{label}</p>
                <p className="text-[10px] text-[#6B6560] mb-3">{sub}</p>
                <div className="h-1.5 rounded-full overflow-hidden mb-2" style={{ background:bg }}>
                  <div className="h-full rounded-full" style={{ width:pct(val), background:color }}/>
                </div>
                <p className="text-xl font-black" style={{ color }}>{pct(val)}</p>
              </div>
            ))}
          </div>
          {/* ── Cross-layer matches section (only shown when present) ── */}
          {pair.cross_layer?.matches?.length > 0 && (
            <div className="rounded-2xl border-2 overflow-hidden" style={{ borderColor:'#CECBF6' }}>
              <div className="px-5 py-3 flex items-center justify-between" style={{ background:'#EEEDFE' }}>
                <div className="flex items-center gap-2">
                  <span style={{ fontSize:14 }}>🌐</span>
                  <p className="text-xs font-black uppercase tracking-widest" style={{ color:'#534AB7' }}>Cross-Layer Feature Matches</p>
                </div>
                <span className="text-xs font-bold px-2.5 py-1 rounded-full" style={{ background:'#534AB7', color:'white' }}>
                  {pair.cross_layer.matches.length} shared
                </span>
              </div>
              <div className="px-5 py-3 bg-white">
                <p className="text-xs mb-3" style={{ color:'#6B6560' }}>
                  <span className="font-semibold" style={{ color:'#534AB7' }}>{pair.cross_layer.layer_a}</span>
                  {' ↔ '}
                  <span className="font-semibold" style={{ color:'#534AB7' }}>{pair.cross_layer.layer_b}</span>
                  {' — same function names found across both layers (score: '}
                  <span className="font-semibold">{Math.round((pair.cross_layer.cross_layer_score ?? 0) * 100)}%</span>
                  {')'}
                </p>
                <div className="flex flex-wrap gap-2">
                  {pair.cross_layer.matches.map((m, i) => (
                    <div key={i} className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border" style={{ borderColor:'#CECBF6', background:'#F8F7FF' }}>
                      <code className="text-xs font-bold" style={{ color:'#3C3489' }}>{m.canonical}</code>
                      <span className="text-[10px] px-1.5 py-0.5 rounded-md font-semibold" style={{
                        background: m.match_type === 'exact' ? '#1D9E75' : '#EF9F27',
                        color: 'white'
                      }}>{m.match_type}</span>
                      <span className="text-[10px]" style={{ color:'#888780' }}>
                        {m.original_a} → {m.original_b}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {fragments.length > 0 ? (
            <div>
              <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-3">Matching Fragments ({fragments.length})</p>
              <div className="space-y-4">
                {fragments.slice(0, 3).map((frag, i) => (
                  <div key={i}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-bold px-2.5 py-1 rounded-lg bg-[#FEF3EC] text-[#CF7249] border border-[#FCDDC5]">
                        Fragment {i+1}{frag.similarity ? ` · ${Math.round(frag.similarity*100)}% match` : ''}
                      </span>
                      {frag.func_a && <span className="text-xs text-[#A8A29E] font-mono">{frag.func_a}()</span>}
                    </div>
                    <CodeDiff
                      fragA={{ file:frag.file_a, name:frag.func_a, start:frag.start_a, end:frag.end_a, source:frag.source_a, similar_lines:frag.similar_lines }}
                      fragB={{ file:frag.file_b, name:frag.func_b, start:frag.start_b, end:frag.end_b, source:frag.source_b }}
                    />
                  </div>
                ))}
                {fragments.length > 3 && <p className="text-sm text-[#A8A29E] text-center">+{fragments.length-3} more fragments</p>}
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-xl border border-[#E8E1D8] p-4 text-sm text-[#A8A29E]">
              No fragment-level data — run in detailed mode for side-by-side code comparison.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

const typeConfig = {
  1: { label:'Exact Copies',   sub:'Whitespace & comment differences only',  color:'#CF7249', bg:'#FEF3EC', border:'#FCDDC5' },
  2: { label:'Renamed Vars',   sub:'Identifier & literal renaming',           color:'#2D6A6A', bg:'#EBF4F4', border:'#B8D9D9' },
  3: { label:'Near-Miss',      sub:'Modified statements & fragments',         color:'#C4827A', bg:'#FAEDEC', border:'#F0C4C0' },
  4: { label:'Semantic / I/O', sub:'I/O testing + PDG graph similarity',      color:'#8B9BB4', bg:'#EFF2F7', border:'#C8D2E0' },
};

const DetectorCard = ({ typeNum, enabled, onToggle }) => {
  const cfg = typeConfig[typeNum];
  return (
    <button onClick={onToggle}
      className="rounded-2xl border-2 p-5 text-left w-full cursor-pointer transition-all duration-150 select-none"
      style={{ background:enabled?cfg.bg:'white', borderColor:enabled?cfg.border:'#E8E1D8' }}>
      <div className="flex items-start justify-between mb-3">
        <span className="text-[10px] font-black uppercase tracking-widest" style={{ color:enabled?cfg.color:'#A8A29E' }}>Type-{typeNum}</span>
        <div className="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
          style={{ borderColor:enabled?cfg.color:'#E8E1D8', background:enabled?cfg.color:'white' }}>
          {enabled && <svg width="10" height="10" fill="none" stroke="white" strokeWidth="3" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>}
        </div>
      </div>
      <p className="text-sm font-bold mb-0.5" style={{ color:enabled?'#1A1714':'#6B6560' }}>{cfg.label}</p>
      <p className="text-xs leading-relaxed" style={{ color:enabled?'#6B6560':'#A8A29E' }}>{cfg.sub}</p>
    </button>
  );
};

const FileChip = ({ file, onRemove }) => {
  const lang = EXT_LANG[getExt(file.name)];
  const zip  = isZip(file.name);
  const lp   = lang ? (LANG_PILL[lang] || { bg:'#EFF2F7', color:'#8B9BB4' }) : null;
  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white border border-[#E8E1D8]">
      <span style={{ color:zip?'#CF7249':'#6B6560', flexShrink:0 }}>{zip?<IcoZip/>:<IcoFile/>}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-[#1A1714] truncate">{file.name}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-[#A8A29E]">{fmtSize(file.size)}</span>
          {lp && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded" style={{ background:lp.bg, color:lp.color }}>{lang}</span>}
          {zip && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-[#FEF3EC] text-[#CF7249]">ZIP</span>}
        </div>
      </div>
      <button onClick={onRemove}
        className="w-7 h-7 rounded-lg flex items-center justify-center text-[#A8A29E] hover:bg-[#FEF3EC] hover:text-[#CF7249] transition-colors flex-shrink-0">
        <IcoX/>
      </button>
    </div>
  );
};

export default function CodeAnalysis() {
  const [files,      setFiles]      = useState([]);
  const [detectors,  setDetectors]  = useState({ t1:true, t2:true, t3:true, t4:true });
  const [running,    setRunning]    = useState(false);
  const [results,    setResults]    = useState(null);
  const [error,      setError]      = useState('');
  const [filter,     setFilter]     = useState('all');
  const [threshold,  setThreshold]  = useState(0.40);
  const [dragging,   setDragging]   = useState(false);
  const [progress,   setProgress]   = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);

  const ALLOWED = '.cpp,.c,.h,.hpp,.cc,.cxx,.java,.kt,.kts,.py,.js,.jsx,.ts,.tsx,.zip';

  const filterCodeFiles = fl =>
    Array.from(fl).filter(f => CODE_EXTS.has('.' + f.name.split('.').pop().toLowerCase()));

  const addFiles = useCallback((incoming) => {
    setError('');
    const existing = new Set(files.map(f => f.name));
    const fresh = Array.from(incoming).filter(f => !existing.has(f.name));
    setFiles(prev => [...prev, ...fresh]);
  }, [files]);

  const onDrop = useCallback((e) => {
    e.preventDefault(); setDragging(false);
    if (e.dataTransfer?.files?.length) addFiles(filterCodeFiles(e.dataTransfer.files));
  }, [addFiles]);

  const handleDownloadCsv = (mode = 'summary') => {
    if (!results?.all_pairs?.length) { alert('No results to export.'); return; }
    const rows = [];
    results.all_pairs.forEach(pair => {
      if ((pair.file_a?.endsWith('.h') || pair.file_a?.endsWith('.hpp') ||
           pair.file_b?.endsWith('.h') || pair.file_b?.endsWith('.hpp'))) return;
      const score     = pair.combined_score ?? pair.structural_score ?? 0;
      const cloneType = pair.primary_clone_type?.replace('type', 'Type-') || 'none';
      rows.push({
        'Student File 1':         pair.student_a_name ? `${pair.student_a_name} (${pair.file_a})` : pair.file_a,
        'Student File 2':         pair.student_b_name ? `${pair.student_b_name} (${pair.file_b})` : pair.file_b,
        'Plagiarism Match (%)':   `${Math.round(score * 100)}%`,
        'Clone Type':             cloneType,
        'Risk Level':             score >= 0.85 ? 'HIGH' : score >= 0.7 ? 'MEDIUM' : score >= 0.5 ? 'LOW' : 'NONE',
        'Matched Functions':      (pair.fragments || []).map(f => `${f.func_a}() ↔ ${f.func_b}()`).join(', '),
        'Recommendation':         score >= 0.85 ? 'Flag for immediate review' : score >= 0.7 ? 'Review required' : 'Monitor',
      });
    });
    if (!rows.length) { alert('No valid results to export.'); return; }
    const csv = [Object.keys(rows[0]), ...rows.map(r => Object.values(r))]
      .map(row => row.map(v => `"${String(v).replace(/"/g, '""')}"`).join(',')).join('\n');
    const url = URL.createObjectURL(new Blob([csv], { type:'text/csv' }));
    const a   = document.createElement('a');
    a.href = url; a.download = `codespectra_${mode}_${Date.now()}.csv`; a.click();
    URL.revokeObjectURL(url);
  };

  const handleAnalyze = async () => {
    const isSingleZip = files.length === 1 && isZip(files[0].name);
    if (!isSingleZip && files.length < 2) {
      setError('Upload at least 2 code files, a folder, or a ZIP archive.');
      return;
    }
    setRunning(true); setError(''); setResults(null);

    try {
      // ── Class ZIP flow ──────────────────────────────────────────────────
      // Upload to backend → backend proxies to engine → engine extracts ZIP,
      // creates a background job, and returns job_id immediately.
      // We poll /analysis/zip/results/:jobId every second for progress.
      if (isSingleZip) {
        setProgress('Uploading ZIP…');
        const formData = new FormData();
        formData.append('file', files[0]);

        const response = await api.post('/analysis/zip', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 120000,  // 2 min — covers upload + ZIP extraction
        });

        const job = response.data;
        if (!job.job_id) {
          // Engine returned inline results (shouldn't happen, but handle gracefully)
          setProgress('');
          setResults({ all_pairs: job.clone_pairs || [], metadata: {} });
          setRunning(false);
          return;
        }

        const totalStudents = job.total_students || '?';
        setProgress(`Analyzing ${totalStudents} students… 0%`);

        // Poll until the background worker finishes or we hit the 10-minute limit.
        const MAX_POLLS = 600;
        let pollCount   = 0;
        let pollDone    = false;

        while (pollCount < MAX_POLLS && !pollDone) {
          await new Promise(r => setTimeout(r, 1000));
          pollCount++;

          let data;
          try {
            const statusRes = await api.get(`/analysis/zip/results/${job.job_id}`);
            data = statusRes.data;
          } catch (pollErr) {
            // Brief network hiccup — keep trying rather than giving up
            console.warn(`[Poll ${pollCount}] ${pollErr.message}`);
            continue;
          }

          const progressPct = Math.round(data.progress ?? data.progress_percent ?? 0);
          setProgress(`Analyzing ${totalStudents} students… ${progressPct}%`);

          if (data.status === 'completed' || data.status === 'partial') {
            pollDone = true;
            const rawPairs = data.clone_pairs || data.results || [];
            const pairs = rawPairs.map(cp => ({
              file_a:             cp.file_a,
              file_b:             cp.file_b,
              combined_score:     cp.effective_score ?? cp.combined_score ?? cp.structural_score ?? 0,
              structural_score:   cp.structural_score   ?? 0,
              semantic_score:     cp.semantic_score     ?? 0,
              type1_score:        cp.type1_score        ?? 0,
              type2_score:        cp.type2_score        ?? 0,
              primary_clone_type: cp.primary_clone_type ?? 'none',
              student_a_name:     data.student_names?.[cp.student_a_id] ?? cp.student_a_name ?? '',
              student_b_name:     data.student_names?.[cp.student_b_id] ?? cp.student_b_name ?? '',
              needs_review:       cp.needs_review  ?? false,
              summary:            cp.summary       ?? '',
            }));
            setResults({ all_pairs: pairs, metadata: { total_files: totalStudents } });
            setProgress('');
            setRunning(false);
          } else if (data.status === 'failed') {
            throw new Error(data.error || 'Analysis job failed on the engine');
          }
          // status === 'processing' → keep looping
        }

        if (!pollDone) {
          throw new Error('Analysis timed out after 10 minutes. Try splitting the ZIP into smaller batches.');
        }
        return;
      }

      // ── Individual files flow (up to 30 files) ──────────────────────────
      setProgress('Uploading files…');
      const form = new FormData();
      files.forEach(f => form.append('files', f));
      form.append('types', JSON.stringify(detectors));
      form.append('mode', 'detailed');
      setProgress('Analyzing — extracting fragments…');
      const data = await api.post('/analysis/files', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 600000,
      });
      setProgress('');
      setResults(data.data);
      setRunning(false);

    } catch (err) {
      const msg       = err.response?.data?.error || err.response?.data?.detail || err.message || 'Analysis failed.';
      const isTooBig  = msg.includes('Too many files') || msg.includes('synchronous analysis');
      setError(isTooBig
        ? `${files.length} files is too many for direct analysis. Put them all in a ZIP and upload the ZIP instead.`
        : msg
      );
      setProgress('');
      setRunning(false);
    }
  };

  useEffect(() => { if (results && !running) setDrawerOpen(true); }, [results, running]);

  const rawPairs  = results ? (results.all_pairs || results.highSimilarityPairs || results.pairs || []) : [];
  const getScore  = p => p.combined_score ?? Math.max(p.structural_score ?? p.structural?.score ?? 0, p.semantic_score ?? p.semantic?.score ?? 0) ?? p.similarity ?? 0;
  const filtered  = rawPairs.filter(p => {
    const s = getScore(p);
    if (filter === 'critical') return s >= 0.85;
    if (filter === 'high')     return s >= 0.70;
    if (filter === 'medium')   return s >= 0.50 && s < 0.70;
    return s >= threshold;
  }).sort((a, b) => getScore(b) - getScore(a));

  const critCount  = rawPairs.filter(p => getRisk(getScore(p)) === 'CRITICAL').length;
  const highCount  = rawPairs.filter(p => getRisk(getScore(p)) === 'HIGH').length;
  const avgScore   = rawPairs.length ? rawPairs.reduce((s, p) => s + getScore(p), 0) / rawPairs.length : 0;
  const langGroups = groupByLang(files);

  return (
    <div className="min-h-screen bg-[#F7F3EE]" style={{ fontFamily:"'DM Sans', system-ui, sans-serif" }}>
      <style>{`
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes slideIn { from { transform: translateX(100%); opacity:0; } to { transform: translateX(0); opacity:1; } }
        input[type=range]  { accent-color: #CF7249; }
      `}</style>

      <div className="pt-16"/>

      <div className="max-w-2xl mx-auto px-6 py-8 pb-16">

        {/* ── Header + upload zone (hidden once results arrive) ── */}
        {!results && (
          <>
            <div className="mb-6">
              <h1 className="text-2xl font-black text-[#1A1714] mb-1">Code Analysis</h1>
              <p className="text-sm text-[#6B6560] leading-relaxed max-w-lg">
                Upload any mix of source files or a ZIP archive. Same-language pairs are compared across four clone detection algorithms.
              </p>
            </div>

            <div
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              className="rounded-3xl border-2 border-dashed p-8 text-center transition-all duration-200 mb-8"
              style={{
                borderColor: dragging ? '#CF7249' : files.length ? '#2D6A6A' : '#D4C9BE',
                background:  dragging ? '#FEF3EC' : files.length ? '#F0F7F7' : 'white',
              }}
            >
              <div className="flex justify-center mb-4"><UploadIllustration/></div>
              <p className="text-base font-bold text-[#1A1714] mb-2">
                {files.length > 0 ? `${files.length} file${files.length !== 1 ? 's' : ''} ready` : 'Drop files, a folder, or a ZIP'}
              </p>
              <p className="text-xs text-[#A8A29E] mb-6">.cpp · .java · .py · .js · .ts · .zip · or an entire folder</p>
              <div className="flex justify-center gap-3 flex-wrap">
                <label className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-[#CF7249] text-white text-sm font-bold cursor-pointer hover:bg-[#B85E38] transition-colors shadow-md shadow-[#CF7249]/20">
                  <IcoFile/> Browse files
                  <input type="file" multiple className="hidden" accept={ALLOWED}
                    onChange={e => { if (e.target.files?.length) addFiles(filterCodeFiles(e.target.files)); e.target.value=''; }}/>
                </label>
                <label className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-white text-[#2D6A6A] border-2 border-[#B8D9D9] text-sm font-bold cursor-pointer hover:bg-[#EBF4F4] transition-colors">
                  <IcoFolder/> Browse folder
                  <input type="file" multiple className="hidden" {...{ webkitdirectory:'', mozdirectory:'' }}
                    onChange={e => { if (e.target.files?.length) addFiles(filterCodeFiles(e.target.files)); e.target.value=''; }}/>
                </label>
              </div>
            </div>
          </>
        )}

        {/* ── File list ── */}
        {files.length > 0 && (
          <div className="bg-white rounded-3xl border-2 border-[#E8E1D8] p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E]">Files ({files.length})</p>
              <button onClick={() => { setFiles([]); setResults(null); }}
                className="text-sm font-semibold text-[#C4827A] hover:underline">Clear all</button>
            </div>
            <div className="space-y-2 max-h-56 overflow-y-auto">
              {files.map((f, i) => <FileChip key={i} file={f} onRemove={() => setFiles(p => p.filter((_, x) => x !== i))}/>)}
            </div>
            {Object.keys(langGroups).length > 0 && (
              <div className="mt-4 pt-4 border-t border-[#F0EBE3]">
                <p className="text-[10px] font-bold uppercase tracking-widest text-[#A8A29E] mb-2">Language pools</p>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(langGroups).map(([lang, count]) => {
                    const lp = LANG_PILL[lang] || { bg:'#EFF2F7', color:'#8B9BB4' };
                    return <span key={lang} className="text-xs font-semibold px-2.5 py-1 rounded-full" style={{ background:lp.bg, color:lp.color }}>{lang} · {count}</span>;
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Detection types ── */}
        <div className="mb-6">
          <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-4">Detection Algorithms</p>
          <div className="grid grid-cols-2 gap-3">
            <DetectorCard typeNum={1} enabled={detectors.t1} onToggle={() => setDetectors(d => ({ ...d, t1:!d.t1 }))}/>
            <DetectorCard typeNum={2} enabled={detectors.t2} onToggle={() => setDetectors(d => ({ ...d, t2:!d.t2 }))}/>
            <DetectorCard typeNum={3} enabled={detectors.t3} onToggle={() => setDetectors(d => ({ ...d, t3:!d.t3 }))}/>
            <DetectorCard typeNum={4} enabled={detectors.t4} onToggle={() => setDetectors(d => ({ ...d, t4:!d.t4 }))}/>
          </div>
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-[#FAEDEC] border-2 border-[#F0C4C0] text-[#C4827A] mb-5">
            <IcoAlert/><p className="text-sm font-medium leading-relaxed">{error}</p>
          </div>
        )}

        {/* ── Hints ── */}
        {files.length === 1 && !isZip(files[0]?.name || '') && (
          <p className="text-sm text-center text-[#A8A29E] mb-4">Add one more file to compare, or upload a ZIP archive.</p>
        )}
        {files.length === 1 && isZip(files[0]?.name || '') && (
          <p className="text-sm text-center text-[#2D6A6A] font-semibold mb-4">
            Class ZIP detected — will extract and compare all student files inside.
          </p>
        )}

        {/* ── Analyse button ── */}
        <button
          onClick={handleAnalyze}
          disabled={running || files.length === 0}
          className="w-full py-5 rounded-2xl font-black text-base flex items-center justify-center gap-3 transition-all duration-150"
          style={{
            background: running || files.length === 0 ? '#E8E1D8' : '#CF7249',
            color:      running || files.length === 0 ? '#A8A29E' : 'white',
            cursor:     running || files.length === 0 ? 'not-allowed' : 'pointer',
            boxShadow:  running || files.length === 0 ? 'none' : '0 8px 24px rgba(207,114,73,0.25)',
          }}
        >
          {running ? (
            <>
              <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                style={{ animation:'spin 0.7s linear infinite' }}/>
              {progress || 'Analyzing…'}
            </>
          ) : (
            <><IcoScan/> Run Analysis</>
          )}
        </button>

        {/* ── View results button (after completion) ── */}
        {results && !running && (
          <button onClick={() => setDrawerOpen(true)}
            className="w-full mt-4 py-4 rounded-2xl font-black text-base flex items-center justify-center gap-3 bg-[#1A1714] text-white hover:bg-[#2D2825] transition-colors">
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
            View {rawPairs.length} Result{rawPairs.length !== 1 ? 's' : ''}
            {critCount > 0 && (
              <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#CF7249] text-white ml-1">
                {critCount} critical
              </span>
            )}
          </button>
        )}
      </div>

      {/* ── Results drawer ── */}
      {drawerOpen && (
        <>
          <div onClick={() => setDrawerOpen(false)}
            className="fixed inset-0 bg-[#1A1714]/40 backdrop-blur-sm z-40"/>

          <div className="fixed top-0 right-0 bottom-0 z-50 flex flex-col bg-[#F7F3EE]"
            style={{ width:'min(96vw,1020px)', boxShadow:'-8px 0 48px rgba(0,0,0,0.18)', animation:'slideIn 0.28s cubic-bezier(0.32,0,0.67,0) forwards' }}>

            <div className="flex items-center justify-between px-7 py-5 bg-white border-b-2 border-[#E8E1D8] flex-shrink-0">
              <div className="flex items-center gap-4">
                <button onClick={() => setDrawerOpen(false)}
                  className="w-9 h-9 rounded-xl border-2 border-[#E8E1D8] flex items-center justify-center text-[#6B6560] hover:bg-[#F7F3EE] transition-colors">
                  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
                </button>
                <div>
                  <p className="text-lg font-black text-[#1A1714]">Analysis Results</p>
                  <p className="text-xs text-[#A8A29E]">{rawPairs.length} pair{rawPairs.length!==1?'s':''} · {filtered.length} shown</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-[#F7F3EE] border border-[#E8E1D8]">
                  <span className="text-xs text-[#6B6560] font-semibold">Min</span>
                  <input type="range" min="0" max="1" step="0.05" value={threshold} onChange={e => setThreshold(parseFloat(e.target.value))} className="w-20"/>
                  <span className="text-sm font-black text-[#CF7249] w-8">{Math.round(threshold*100)}%</span>
                </div>
                <div className="flex gap-1.5">
                  {[{v:'all',l:'All'},{v:'critical',l:'Critical'},{v:'high',l:'High'},{v:'medium',l:'Medium'}].map(({v,l}) => (
                    <button key={v} onClick={() => setFilter(v)}
                      className="px-3 py-1.5 rounded-lg text-xs font-bold border-2 transition-colors"
                      style={{ borderColor:filter===v?'#CF7249':'#E8E1D8', background:filter===v?'#CF7249':'white', color:filter===v?'white':'#6B6560' }}>
                      {l}
                    </button>
                  ))}
                </div>
                <div className="flex rounded-xl overflow-hidden border-2 border-[#B8D9D9]">
                  {[{mode:'summary',label:'Summary'},{mode:'technical',label:'Technical'}].map(({mode,label}) => (
                    <button key={mode} onClick={() => handleDownloadCsv(mode)}
                      className="flex items-center gap-1.5 px-3 py-2 text-xs font-bold text-[#2D6A6A] bg-white hover:bg-[#EBF4F4] transition-colors"
                      style={{ borderRight:mode==='summary'?'1px solid #B8D9D9':'none' }}>
                      <IcoDownload/>{label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <div className="grid grid-cols-4 gap-4 px-7 py-5 flex-shrink-0">
              {[
                { label:'Total Pairs',  value:rawPairs.length, color:'#1A1714' },
                { label:'Critical ≥85%', value:critCount,  color:critCount>0?'#CF7249':'#A8A29E' },
                { label:'High 70–85%',  value:highCount,  color:highCount>0?'#C4827A':'#A8A29E' },
                { label:'Avg Score',    value:pct(avgScore), color:'#2D6A6A' },
              ].map(({ label, value, color }) => (
                <div key={label} className="bg-white rounded-2xl border-2 border-[#E8E1D8] px-5 py-4">
                  <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E] mb-2">{label}</p>
                  <p className="text-3xl font-black" style={{ color }}>{value}</p>
                </div>
              ))}
            </div>

            {critCount > 0 && (
              <div className="mx-7 mb-4 flex items-center gap-3 px-5 py-4 rounded-2xl bg-[#FEF3EC] border-2 border-[#FCDDC5] text-[#CF7249] flex-shrink-0">
                <IcoAlert/>
                <p className="text-sm font-bold">{critCount} pair{critCount!==1?'s':''} with ≥85% similarity — immediate review recommended.</p>
              </div>
            )}

            <div className="flex-1 overflow-y-auto px-7 pb-7">
              {filtered.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-20 bg-white border-2 border-dashed border-[#E8E1D8] rounded-3xl text-center">
                  <div className="w-14 h-14 rounded-2xl bg-[#EBF4F4] text-[#2D6A6A] flex items-center justify-center mb-4"><IcoCheck/></div>
                  <p className="text-lg font-bold text-[#1A1714] mb-2">No pairs above {Math.round(threshold*100)}%</p>
                  <p className="text-sm text-[#A8A29E]">Lower the threshold or change the filter.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filtered.map((pair, i) => <PairCard key={pair.pair_id||i} pair={pair} index={i} getScore={getScore}/>)}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
