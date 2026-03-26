import React, { useState, useCallback } from 'react';
import analysisService from '../../services/analysisService';
import api from '../../utils/api';

// ─── Design tokens (matches global theme) ─────────────────────────────────────
// cream bg: #F7F3EE  | card: white         | border: #E8E1D8
// orange:   #CF7249  | orange-light: #FEF3EC
// teal:     #2D6A6A  | teal-light:   #EBF4F4
// pink:     #C4827A  | pink-light:   #FAEDEC
// slate:    #8B9BB4  | slate-light:  #EFF2F7
// text-dark:#1A1714  | text-mid:     #6B6560 | text-light: #A8A29E

const EXT_LANG = {
  '.cpp':'C++', '.c':'C', '.h':'C/C++', '.hpp':'C++', '.cc':'C++', '.cxx':'C++',
  '.java':'Java', '.py':'Python',
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
};

// Risk bands
const RISK = {
  CRITICAL: { label:'Critical', color:'#CF7249', bg:'#FEF3EC', border:'#CF7249' },
  HIGH:     { label:'High',     color:'#C4827A', bg:'#FAEDEC', border:'#C4827A' },
  MEDIUM:   { label:'Medium',   color:'#2D6A6A', bg:'#EBF4F4', border:'#2D6A6A' },
  LOW:      { label:'Low',      color:'#8B9BB4', bg:'#EFF2F7', border:'#8B9BB4' },
  NONE:     { label:'Clean',    color:'#A8A29E', bg:'#F7F3EE', border:'#E8E1D8' },
};

const getExt    = n => '.' + n.split('.').pop().toLowerCase();
const isZip     = n => n.toLowerCase().endsWith('.zip');
const fmtSize   = b => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(1)} KB`;
const pct       = n => `${Math.round((n || 0) * 100)}%`;

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

// ─── SVG Icons ────────────────────────────────────────────────────────────────
const IcoUpload  = () => <svg width="20" height="20" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>;
const IcoFolder  = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M22 19a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2h5l2 3h9a2 2 0 012 2z"/></svg>;
const IcoFile    = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>;
const IcoZip     = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/></svg>;
const IcoX       = () => <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" viewBox="0 0 24 24"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>;
const IcoChevron = ({ open }) => <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24" style={{ transform: open ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}><polyline points="6 9 12 15 18 9"/></svg>;
const IcoScan    = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/><line x1="7" y1="12" x2="17" y2="12"/></svg>;
const IcoDownload = () => <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>;
const IcoAlert   = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>;
const IcoCheck   = () => <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>;

// ─── Side-by-side code diff ────────────────────────────────────────────────────
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
          <div key={i} style={{ display:'flex', background: simSet.has(i) ? 'rgba(207,114,73,0.12)' : 'transparent', borderLeft: simSet.has(i) ? '2px solid #CF7249' : '2px solid transparent' }}>
            <span style={{ userSelect:'none', color:'#4A4540', width:36, textAlign:'right', paddingRight:12, paddingTop:1, flexShrink:0, background:'rgba(26,23,20,0.4)' }}>{i+1}</span>
            <pre style={{ flex:1, padding:'1px 12px', whiteSpace:'pre-wrap', wordBreak:'break-all', margin:0, color: simSet.has(i) ? '#F7D5BF' : '#8B7D72' }}>{line || ' '}</pre>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div style={{ borderRadius:10, overflow:'hidden', border:'1px solid #E8E1D8' }}>
      <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', borderLeft:'none', maxHeight:280, overflow:'auto' }}>
        {col(linesA, 'File A', fragA)}
        <div style={{ borderLeft:'1px solid #2D2825' }}>{col(linesB, 'File B', fragB)}</div>
      </div>
    </div>
  );
};

// ─── Pair Card ───────────────────────────────────────────────────────────────
const PairCard = ({ pair, index, getScore }) => {
  const [open, setOpen] = useState(false);
  const score = getScore(pair);
  const R = RISK[getRisk(score)];

  const t1 = pair.type1_score ?? 0;
  const t2 = pair.type2_score ?? 0;
  const t3 = pair.structural_score ?? pair.structural?.score ?? 0;
  const t4 = pair.semantic_score ?? pair.semantic?.score ?? 0;
  const cloneLabel = (pair.primary_clone_type || pair.clone_type || '').replace('type', 'Type-');

  // Type-4 enrichment fields (set by educational detector)
  const ioMatchScore    = pair.io_match_score    ?? null;   // 0.0–1.0 or null
  const ioAvailable     = pair.io_available      ?? false;
  const interpretation  = pair.interpretation    ?? '';

  // pair.fragments is set by the engine in detailed mode and contains
  // fragment source code for side-by-side diff display.
  // Fall back to parsing matching_blocks for legacy / assignment-view pairs.
  const fragments = (() => {
    if (Array.isArray(pair.fragments) && pair.fragments.length > 0)
      return pair.fragments;
    try {
      const mb = pair.matching_blocks;
      if (!mb) return [];
      const parsed = typeof mb === 'string' ? JSON.parse(mb) : mb;
      return Array.isArray(parsed) ? parsed : (parsed.fragments || []);
    } catch { return []; }
  })();

  return (
    <div style={{
      background: 'white',
      borderRadius: 14,
      border: `1px solid ${open ? R.border : '#E8E1D8'}`,
      overflow: 'hidden',
      transition: 'border-color 0.15s, box-shadow 0.15s',
      boxShadow: open ? '0 4px 16px rgba(0,0,0,0.06)' : 'none',
    }}>
      {/* Header */}
      <button onClick={() => setOpen(o => !o)} style={{
        width: '100%', textAlign: 'left', padding: '16px 20px',
        display: 'flex', alignItems: 'center', gap: 14,
        background: 'white', border: 'none', cursor: 'pointer',
      }}>
        {/* Index */}
        <span style={{ fontSize: 11, fontWeight: 700, color: '#A8A29E', width: 20, flexShrink: 0 }}>#{index + 1}</span>

        {/* Score circle */}
        <div style={{
          width: 48, height: 48, borderRadius: '50%', flexShrink: 0,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          background: R.bg, color: R.color, fontWeight: 800, fontSize: 13,
          border: `2px solid ${R.border}`,
        }}>
          {Math.round(score * 100)}%
        </div>

        {/* Names + badges */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#1A1714', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 180 }}>
              {pair.file_a || 'File A'}
            </span>
            <span style={{ fontSize: 11, color: '#A8A29E', fontWeight: 600 }}>vs</span>
            <span style={{ fontSize: 13, fontWeight: 700, color: '#1A1714', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: 180 }}>
              {pair.file_b || 'File B'}
            </span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 5, flexWrap: 'wrap' }}>
            {/* Risk badge */}
            <span style={{
              fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.1em',
              padding: '2px 8px', borderRadius: 20, background: R.bg, color: R.color,
              display: 'inline-flex', alignItems: 'center', gap: 4,
            }}>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: R.color, flexShrink: 0 }} />
              {R.label}
            </span>
            {/* Clone type badge */}
            {cloneLabel && cloneLabel !== 'Type-none' && (
              <span style={{
                fontSize: 9, fontWeight: 700, padding: '2px 7px', borderRadius: 6,
                background: '#F7F3EE', color: '#6B6560', border: '1px solid #E8E1D8',
              }}>{cloneLabel}</span>
            )}
            {fragments.length > 0 && (
              <span style={{ fontSize: 10, color: '#A8A29E' }}>
                {fragments.length} fragment{fragments.length !== 1 ? 's' : ''}
              </span>
            )}
          </div>
        </div>

        {/* Structural bar */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, minWidth: 120 }} className="hidden-mobile">
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 10, color: '#6B6560' }}>
            <span style={{ width: 60, textAlign: 'right' }}>Structural</span>
            <div style={{ flex: 1, height: 4, background: '#F0EBE3', borderRadius: 2, overflow: 'hidden' }}>
              <div style={{ height: '100%', background: '#CF7249', borderRadius: 2, width: pct(t3) }} />
            </div>
            <span style={{ color: '#1A1714', fontWeight: 600, width: 30 }}>{pct(t3)}</span>
          </div>
        </div>

        <IcoChevron open={open} />
      </button>

      {/* Expanded */}
      {open && (
        <div style={{ borderTop: '1px solid #F0EBE3', background: '#FDFCFB', padding: 20 }}>

          {/* Score breakdown — 4 type cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 8, marginBottom: 16 }}>
            {[
              { label: 'Type-1', sub: 'Exact copy',       val: t1, color: '#CF7249', bg: '#FEF3EC' },
              { label: 'Type-2', sub: 'Renamed vars',     val: t2, color: '#2D6A6A', bg: '#EBF4F4' },
              { label: 'Type-3', sub: 'Structural',       val: t3, color: '#C4827A', bg: '#FAEDEC' },
              { label: 'Type-4', sub: 'Semantic/I⁠O',    val: t4, color: '#8B9BB4', bg: '#EFF2F7' },
            ].map(({ label, sub, val, color, bg }) => (
              <div key={label} style={{ background: 'white', border: '1px solid #E8E1D8', borderRadius: 10, padding: '10px 12px' }}>
                <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#A8A29E', marginBottom: 2 }}>{label}</p>
                <p style={{ fontSize: 9, color: '#6B6560', marginBottom: 6 }}>{sub}</p>
                <div style={{ height: 4, background: '#F0EBE3', borderRadius: 2, overflow: 'hidden', marginBottom: 5 }}>
                  <div style={{ height: '100%', background: color, borderRadius: 2, width: pct(val), transition: 'width 0.4s' }} />
                </div>
                <p style={{ fontSize: 18, fontWeight: 800, color: '#1A1714' }}>{pct(val)}</p>
              </div>
            ))}
          </div>

          {/* Type-4 I/O behavioral detail — only shown when semantic score is non-zero */}
          {t4 > 0 && (
            <div style={{
              background: 'white', border: '1px solid #E8E1D8', borderRadius: 10,
              padding: '12px 14px', marginBottom: 16,
            }}>
              <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#8B9BB4', marginBottom: 8 }}>
                Type-4 — Educational Semantic Analysis
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 12, alignItems: 'center' }}>
                {/* I/O behavioral score */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 10, color: '#6B6560', fontWeight: 600 }}>I/O Match:</span>
                  {ioAvailable && ioMatchScore !== null ? (
                    <span style={{
                      fontSize: 11, fontWeight: 800,
                      color: ioMatchScore >= 0.9 ? '#CF7249' : ioMatchScore >= 0.7 ? '#C4827A' : '#8B9BB4',
                    }}>{Math.round(ioMatchScore * 100)}%</span>
                  ) : (
                    <span style={{ fontSize: 10, color: '#A8A29E', fontStyle: 'italic' }}>not available</span>
                  )}
                </div>
                {/* Algorithm interpretation */}
                {interpretation && (
                  <span style={{
                    fontSize: 10, color: '#6B6560', lineHeight: 1.5,
                    flex: 1, minWidth: 0,
                    overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                  }} title={interpretation}>
                    {interpretation}
                  </span>
                )}
              </div>
            </div>
          )}

          {/* Fragment diffs */}
          {fragments.length > 0 ? (
            <div>
              <p style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#A8A29E', marginBottom: 10 }}>
                Matching Fragments ({fragments.length})
              </p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {fragments.slice(0, 3).map((frag, i) => (
                  <div key={i}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                      <span style={{
                        fontSize: 10, fontWeight: 700, padding: '2px 8px', borderRadius: 6,
                        background: '#FEF3EC', color: '#CF7249', border: '1px solid #FCDDC5',
                      }}>
                        Fragment {i+1}{frag.similarity ? ` · ${Math.round(frag.similarity*100)}% match` : ''}
                      </span>
                      {frag.func_a && <span style={{ fontSize: 10, color: '#A8A29E', fontFamily: 'monospace' }}>{frag.func_a}()</span>}
                    </div>
                    <CodeDiff
                      fragA={{ file: frag.file_a, name: frag.func_a, start: frag.start_a, end: frag.end_a, source: frag.source_a, similar_lines: frag.similar_lines }}
                      fragB={{ file: frag.file_b, name: frag.func_b, start: frag.start_b, end: frag.end_b, source: frag.source_b }}
                    />
                  </div>
                ))}
                {fragments.length > 3 && (
                  <p style={{ fontSize: 11, color: '#A8A29E', textAlign: 'center', paddingTop: 4 }}>
                    +{fragments.length - 3} more fragments
                  </p>
                )}
              </div>
            </div>
          ) : (
            <div style={{ background: 'white', border: '1px solid #E8E1D8', borderRadius: 10, padding: '14px 16px', fontSize: 12, color: '#A8A29E' }}>
              No fragment-level data — run in detailed mode for side-by-side code comparison.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// ─── File Chip ────────────────────────────────────────────────────────────────
const FileChip = ({ file, onRemove }) => {
  const lang = EXT_LANG[getExt(file.name)];
  const zip  = isZip(file.name);
  const lp   = lang ? (LANG_PILL[lang] || { bg:'#EFF2F7', color:'#8B9BB4' }) : null;
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10,
      padding: '8px 12px', borderRadius: 10,
      background: 'white', border: '1px solid #E8E1D8',
    }}
      className="file-chip-row"
    >
      <span style={{ color: zip ? '#CF7249' : '#6B6560', flexShrink: 0 }}>
        {zip ? <IcoZip /> : <IcoFile />}
      </span>
      <div style={{ flex: 1, minWidth: 0 }}>
        <p style={{ fontSize: 12, fontWeight: 600, color: '#1A1714', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{file.name}</p>
        <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginTop: 2 }}>
          <span style={{ fontSize: 10, color: '#A8A29E' }}>{fmtSize(file.size)}</span>
          {lp && <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 4, background: lp.bg, color: lp.color }}>{lang}</span>}
          {zip && <span style={{ fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 4, background: '#FEF3EC', color: '#CF7249' }}>ZIP</span>}
        </div>
      </div>
      <button onClick={onRemove} style={{
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        width: 22, height: 22, borderRadius: 6, border: 'none', background: 'transparent',
        color: '#A8A29E', cursor: 'pointer', flexShrink: 0,
        transition: 'background 0.15s, color 0.15s',
      }}
        onMouseEnter={e => { e.currentTarget.style.background = '#FEF3EC'; e.currentTarget.style.color = '#CF7249'; }}
        onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#A8A29E'; }}
      >
        <IcoX />
      </button>
    </div>
  );
};

// ─── Detector Toggle ──────────────────────────────────────────────────────────
const typeConfig = {
  1: { label: 'Exact Copies',    sub: 'Whitespace & comment differences only',  color: '#CF7249', bg: '#FEF3EC', border: '#FCDDC5' },
  2: { label: 'Renamed Vars',    sub: 'Identifier & literal renaming',           color: '#2D6A6A', bg: '#EBF4F4', border: '#B8D9D9' },
  3: { label: 'Near-Miss',       sub: 'Modified statements & fragments',         color: '#C4827A', bg: '#FAEDEC', border: '#F0C4C0' },
  4: { label: 'Semantic / I⁠O',  sub: 'I/O testing + PDG graph similarity',      color: '#8B9BB4', bg: '#EFF2F7', border: '#C8D2E0' },
};

const DetectorToggle = ({ typeNum, enabled, onToggle }) => {
  const cfg = typeConfig[typeNum];
  return (
    <button
      onClick={onToggle}
      style={{
        padding: '12px 14px', borderRadius: 12, textAlign: 'left',
        border: `2px solid ${enabled ? cfg.border : '#E8E1D8'}`,
        background: enabled ? cfg.bg : 'white',
        cursor: 'pointer',
        transition: 'all 0.15s', width: '100%',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
        <span style={{ fontSize: 9, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.12em', color: enabled ? cfg.color : '#A8A29E' }}>
          Type-{typeNum}
        </span>
        <div style={{
          width: 14, height: 14, borderRadius: '50%',
          border: `2px solid ${enabled ? cfg.color : '#E8E1D8'}`,
          background: enabled ? cfg.color : 'transparent',
          transition: 'all 0.15s',
        }} />
      </div>
      <p style={{ fontSize: 12, fontWeight: 700, color: enabled ? '#1A1714' : '#6B6560', marginBottom: 2 }}>{cfg.label}</p>
      <p style={{ fontSize: 10, color: enabled ? '#6B6560' : '#A8A29E', lineHeight: 1.4 }}>{cfg.sub}</p>
    </button>
  );
};

// ─── Stat Card ────────────────────────────────────────────────────────────────
const StatCard = ({ label, value, color, bg }) => (
  <div style={{ background: 'white', border: '1px solid #E8E1D8', borderRadius: 14, padding: '16px 18px' }}>
    <p style={{ fontSize: 10, fontWeight: 600, color: '#A8A29E', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 6 }}>{label}</p>
    <p style={{ fontSize: 28, fontWeight: 800, color: color || '#1A1714' }}>{value}</p>
  </div>
);

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function CodeAnalysis() {
  const [files,     setFiles]     = useState([]);
  const [detectors, setDetectors] = useState({ t1: true, t2: true, t3: true, t4: true });
  const [running,   setRunning]   = useState(false);
  const [results,   setResults]   = useState(null);
  const [error,     setError]     = useState('');
  const [filter,    setFilter]    = useState('all');
  const [threshold, setThreshold] = useState(0.40);
  const [dragging,  setDragging]  = useState(false);
  const [progress,    setProgress]    = useState('');
  const [csvLoading,  setCsvLoading]  = useState(false);

  const ALLOWED   = '.cpp,.c,.h,.hpp,.cc,.cxx,.java,.py,.js,.jsx,.ts,.tsx,.zip';
  const CODE_EXTS = new Set(['.cpp','.c','.h','.hpp','.cc','.cxx','.java','.py','.js','.jsx','.ts','.tsx','.zip']);

  const filterCodeFiles = (fileList) =>
    Array.from(fileList).filter(f => CODE_EXTS.has('.' + f.name.split('.').pop().toLowerCase()));

  const addFiles = useCallback((incoming) => {
    setError('');
    const existing = new Set(files.map(f => f.name));
    const fresh = Array.from(incoming).filter(f => !existing.has(f.name));
    setFiles(prev => [...prev, ...fresh]);
  }, [files]);

  const onDrop = useCallback((e) => {
    e.preventDefault();
    setDragging(false);
    if (e.dataTransfer?.files?.length) addFiles(filterCodeFiles(e.dataTransfer.files));
  }, [addFiles]);

  const toggleDetector = k => setDetectors(d => ({ ...d, [k]: !d[k] }));

  // csvMode tracks which button is in-flight: null | 'summary' | 'technical'
  const [csvMode, setCsvMode] = useState(null);

  const handleDownloadCsv = async (mode = 'summary') => {
    if (files.length < 2 || csvMode) return;
    setCsvMode(mode);
    setCsvLoading(true);
    try {
      const form = new FormData();
      files.forEach(f => form.append('files', f));
      const response = await api.post(
        `/analysis/report/csv?language=cpp&mode=${mode}&detailed=true`,
        form,
        { headers: { 'Content-Type': 'multipart/form-data' }, responseType: 'blob', timeout: 300000 }
      );
      const fname = mode === 'summary'
        ? `codespectra_summary_${Date.now()}.csv`
        : `codespectra_technical_${Date.now()}.csv`;
      const url  = window.URL.createObjectURL(new Blob([response.data], { type: 'text/csv' }));
      const link = document.createElement('a');
      link.href  = url;
      link.setAttribute('download', fname);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('CSV download failed:', err);
      alert('CSV export failed. Make sure the analysis engine is running.');
    } finally {
      setCsvMode(null);
      setCsvLoading(false);
    }
  };

  const handleAnalyze = async () => {
    // Allow: 1 ZIP, OR 2+ code files
    const isSingleZip = files.length === 1 && isZip(files[0].name);
    if (!isSingleZip && files.length < 2) {
      setError('Upload at least 2 code files, a folder, or a ZIP archive (with student sub-zips inside).');
      return;
    }

    setRunning(true); setError(''); setResults(null);

    try {
      // ── Path A: single class ZIP → async job with polling ────────────────
      if (isSingleZip) {
        setProgress('Uploading ZIP…');
        const job = await analysisService.analyzeClassZip(files[0]);

        if (!job.job_id) {
          // engine returned synchronous project-mode result
          setProgress('');
          setResults({ all_pairs: [], metadata: {}, ...(job.clone_classes ? { clone_classes: job.clone_classes } : {}) });
          return;
        }

        // Poll until complete
        const jobId = job.job_id;
        const totalStudents = job.total_students || '?';
        setProgress(`Analyzing ${totalStudents} students… 0%`);

        await new Promise((resolve, reject) => {
          let attempts = 0;
          const MAX_ATTEMPTS = 180;  // 180 × 5 s = 15 min max
          const timer = setInterval(async () => {
            attempts++;
            try {
              const status = await analysisService.pollZipResults(jobId);
              const pct = Math.round(status.progress || 0);
              setProgress(`Analyzing ${totalStudents} students… ${pct}%`);

              if (status.status === 'completed' || status.status === 'partial') {
                clearInterval(timer);
                // Convert job results into the all_pairs shape the frontend expects
                const pairs = (status.clone_pairs || []).map(cp => ({
                  file_a:             cp.file_a,
                  file_b:             cp.file_b,
                  combined_score:     cp.effective_score ?? cp.structural_score ?? 0,
                  structural_score:   cp.structural_score  ?? 0,
                  semantic_score:     cp.semantic_score    ?? 0,
                  type1_score:        cp.type1_score        ?? 0,
                  type2_score:        cp.type2_score        ?? 0,
                  primary_clone_type: cp.primary_clone_type ?? 'none',
                  similarity_level:   cp.similarity_level   ?? 'NONE',
                  needs_review:       cp.needs_review       ?? false,
                  summary:            cp.summary            ?? '',
                  // student names attached by engine when mode=class_zip
                  student_a_name:     status.student_names?.[cp.student_a_id] ?? '',
                  student_b_name:     status.student_names?.[cp.student_b_id] ?? '',
                }));
                setResults({ all_pairs: pairs, metadata: { total_files: totalStudents } });
                resolve();
              } else if (status.status === 'failed') {
                clearInterval(timer);
                reject(new Error(status.error || 'Analysis job failed'));
              } else if (attempts >= MAX_ATTEMPTS) {
                clearInterval(timer);
                reject(new Error('Analysis timed out after 15 minutes.'));
              }
            } catch (pollErr) {
              clearInterval(timer);
              reject(pollErr);
            }
          }, 5000);
        });

        setProgress('');
        return;
      }

      // ── Path B: individual files → synchronous analysis ───────────────
      setProgress('Uploading files…');
      const form = new FormData();
      files.forEach(f => form.append('files', f));
      form.append('types', JSON.stringify(detectors));
      form.append('mode', 'detailed');
      setProgress('Analyzing — extracting fragments…');
      const data = await analysisService.analyzeFiles(form);
      setProgress('');
      setResults(data);

    } catch (err) {
      const msg = err.response?.data?.error || err.response?.data?.detail || err.message || 'Analysis failed.';
      // If the engine rejected because there are too many files, suggest ZIP
      const isTooBig = msg.includes('Too many files') || msg.includes('synchronous analysis');
      setError(isTooBig
        ? `${files.length} files is too many for direct analysis. Put them all in a ZIP and upload the ZIP instead — it runs asynchronously and handles any number of files.`
        : msg
      );
      setProgress('');
    } finally {
      setRunning(false);
    }
  };

  // ── Derived ──────────────────────────────────────────────────────────────────
  const rawPairs = results
    ? (results.all_pairs || results.highSimilarityPairs || results.pairs || [])
    : [];

  // combined_score = max(structural_score, semantic_score) set by engine v3.0
  // Fallback chain ensures Type-4-only pairs still surface with non-zero score
  const getScore = p =>
    p.combined_score
    ?? Math.max(
         p.structural_score ?? p.structural?.score ?? 0,
         p.semantic_score   ?? p.semantic?.score   ?? 0,
       )
    ?? p.similarity
    ?? 0;

  const filtered = rawPairs
    .filter(p => {
      const s = getScore(p);
      if (filter === 'critical') return s >= 0.85;
      if (filter === 'high')     return s >= 0.70;
      if (filter === 'medium')   return s >= 0.50 && s < 0.70;
      return s >= threshold;
    })
    .sort((a, b) => getScore(b) - getScore(a));

  const critCount  = rawPairs.filter(p => getRisk(getScore(p)) === 'CRITICAL').length;
  const highCount  = rawPairs.filter(p => getRisk(getScore(p)) === 'HIGH').length;
  const avgScore   = rawPairs.length ? rawPairs.reduce((s, p) => s + getScore(p), 0) / rawPairs.length : 0;
  const langGroups = groupByLang(files);

  // ── Results drawer (full-screen slide-over) ────────────────────────────────
  const [drawerOpen, setDrawerOpen] = useState(false);
  // Open drawer automatically when results arrive
  React.useEffect(() => { if (results && !running) setDrawerOpen(true); }, [results, running]);

  return (
    <div style={{ minHeight: '100vh', background: '#F7F3EE', fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <style>{`
        @keyframes spin    { to { transform: rotate(360deg); } }
        @keyframes slideIn { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        input[type=range] { accent-color: #CF7249; }
      `}</style>

      {/* Spacer below fixed navbar */}
      <div style={{ height: 60 }} />

      <div style={{ maxWidth: 680, margin: '0 auto', padding: '36px 24px 80px' }}>

        {/* ── Page header ── */}
        <div style={{ marginBottom: 28 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            padding: '4px 12px', borderRadius: 20,
            background: '#FEF3EC', border: '1px solid #FCDDC5',
            fontSize: 11, fontWeight: 600, color: '#CF7249', marginBottom: 12,
          }}>
            <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#CF7249', animation: 'pulse 2s infinite' }} />
            No assignment required — analyze any code files directly
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#1A1714', marginBottom: 6 }}>Code Analysis</h1>
          <p style={{ fontSize: 14, color: '#6B6560', maxWidth: 500, lineHeight: 1.6 }}>
            Upload any mix of source files, a folder, or a ZIP archive. Same-language files are paired and checked with all four detectors.
          </p>
        </div>

        {/* ── SINGLE COLUMN PANEL (upload + controls) ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          {/* fake left-panel wrapper for the grid that used to be here */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>

            {/* Drop zone */}
            <div
              onDragOver={e => { e.preventDefault(); setDragging(true); }}
              onDragLeave={() => setDragging(false)}
              onDrop={onDrop}
              style={{
                border: `2px dashed ${dragging ? '#CF7249' : files.length ? '#2D6A6A' : '#D4C9BE'}`,
                borderRadius: 16, padding: '28px 20px', textAlign: 'center',
                background: dragging ? '#FEF3EC' : files.length ? '#F0F7F7' : 'white',
                transition: 'all 0.2s', cursor: 'default',
              }}
            >
              <div style={{
                width: 44, height: 44, borderRadius: 12, background: '#FEF3EC',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                margin: '0 auto 12px', color: '#CF7249',
                transform: dragging ? 'scale(1.1)' : 'scale(1)', transition: 'transform 0.2s',
              }}>
                <IcoUpload />
              </div>
              <p style={{ fontSize: 13, fontWeight: 700, color: '#1A1714', marginBottom: 4 }}>
                {files.length > 0
                  ? `${files.length} file${files.length !== 1 ? 's' : ''} selected`
                  : 'Drop files, folder, or ZIP here'}
              </p>
              <p style={{ fontSize: 11, color: '#A8A29E', marginBottom: 16, lineHeight: 1.5 }}>
                .cpp .java .py .js .ts · .zip · or a whole folder
              </p>
              <div style={{ display: 'flex', justifyContent: 'center', gap: 8, flexWrap: 'wrap' }}>
                <label style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  padding: '8px 16px', borderRadius: 10,
                  background: '#CF7249', color: 'white',
                  fontSize: 12, fontWeight: 700, cursor: 'pointer',
                  transition: 'background 0.15s',
                }}
                  onMouseEnter={e => e.currentTarget.style.background = '#B85E38'}
                  onMouseLeave={e => e.currentTarget.style.background = '#CF7249'}
                >
                  <IcoFile /> Browse files
                  <input type="file" multiple style={{ display: 'none' }} accept={ALLOWED}
                    onChange={e => { if (e.target.files?.length) addFiles(filterCodeFiles(e.target.files)); e.target.value = ''; }} />
                </label>
                <label style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  padding: '8px 16px', borderRadius: 10,
                  background: 'white', color: '#2D6A6A',
                  border: '1.5px solid #B8D9D9',
                  fontSize: 12, fontWeight: 700, cursor: 'pointer',
                  transition: 'background 0.15s',
                }}
                  onMouseEnter={e => e.currentTarget.style.background = '#EBF4F4'}
                  onMouseLeave={e => e.currentTarget.style.background = 'white'}
                >
                  <IcoFolder /> Browse folder
                  <input type="file" multiple style={{ display: 'none' }}
                    webkitdirectory="" mozdirectory=""
                    onChange={e => { if (e.target.files?.length) addFiles(filterCodeFiles(e.target.files)); e.target.value = ''; }} />
                </label>
              </div>
            </div>

            {/* File list */}
            {files.length > 0 && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#A8A29E' }}>
                    Files ({files.length})
                  </p>
                  <button onClick={() => { setFiles([]); setResults(null); }}
                    style={{ fontSize: 11, fontWeight: 600, color: '#C4827A', background: 'none', border: 'none', cursor: 'pointer' }}>
                    Clear all
                  </button>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 5, maxHeight: 200, overflowY: 'auto' }}>
                  {files.map((f, i) => (
                    <FileChip key={i} file={f} onRemove={() => setFiles(p => p.filter((_, x) => x !== i))} />
                  ))}
                </div>

                {/* Language summary */}
                {Object.keys(langGroups).length > 0 && (
                  <div style={{ marginTop: 10, padding: '10px 12px', background: 'white', borderRadius: 10, border: '1px solid #E8E1D8' }}>
                    <p style={{ fontSize: 9, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#A8A29E', marginBottom: 8 }}>
                      Language pools
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {Object.entries(langGroups).map(([lang, count]) => {
                        const lp = LANG_PILL[lang] || { bg: '#EFF2F7', color: '#8B9BB4' };
                        return (
                          <span key={lang} style={{ fontSize: 10, fontWeight: 600, padding: '3px 8px', borderRadius: 6, background: lp.bg, color: lp.color }}>
                            {lang} · {count}
                          </span>
                        );
                      })}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Detection toggles */}
            <div>
              <p style={{ fontSize: 10, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.12em', color: '#A8A29E', marginBottom: 10 }}>
                Detection Types
              </p>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <DetectorToggle typeNum={1} enabled={detectors.t1} onToggle={() => toggleDetector('t1')} />
                <DetectorToggle typeNum={2} enabled={detectors.t2} onToggle={() => toggleDetector('t2')} />
                <DetectorToggle typeNum={3} enabled={detectors.t3} onToggle={() => toggleDetector('t3')} />
                <DetectorToggle typeNum={4} enabled={detectors.t4} onToggle={() => toggleDetector('t4')} />
              </div>
            </div>

            {/* Error */}
            {error && (
              <div style={{
                display: 'flex', alignItems: 'flex-start', gap: 10,
                padding: '12px 14px', borderRadius: 10,
                background: '#FAEDEC', border: '1px solid #F0C4C0', color: '#C4827A',
              }}>
                <IcoAlert />
                <p style={{ fontSize: 12, fontWeight: 500, lineHeight: 1.5 }}>{error}</p>
              </div>
            )}

            {/* Run button */}
            <button
              onClick={handleAnalyze}
              disabled={running || files.length === 0}
              style={{
                width: '100%', padding: '14px 20px', borderRadius: 12, border: 'none',
                background: running || files.length === 0 ? '#E8E1D8' : '#CF7249',
                color: running || files.length === 0 ? '#A8A29E' : 'white',
                fontSize: 14, fontWeight: 800, cursor: running || files.length === 0 ? 'not-allowed' : 'pointer',
                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                transition: 'background 0.15s',
              }}
              onMouseEnter={e => { if (!running && files.length > 0) e.currentTarget.style.background = '#B85E38'; }}
              onMouseLeave={e => { if (!running && files.length > 0) e.currentTarget.style.background = '#CF7249'; }}
            >
              {running ? (
                <>
                  <span style={{
                    width: 14, height: 14, border: '2px solid rgba(255,255,255,0.4)',
                    borderTopColor: 'white', borderRadius: '50%',
                    animation: 'spin 0.7s linear infinite',
                    display: 'inline-block',
                  }} />
                  {progress || 'Analyzing…'}
                </>
              ) : (
                <><IcoScan /> Run Analysis</>
              )}
            </button>
            <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

            {files.length === 1 && !isZip(files[0]?.name || '') && (
              <p style={{ fontSize: 11, textAlign: 'center', color: '#A8A29E' }}>
                Add one more file to compare, or upload a ZIP archive.
              </p>
            )}
            {files.length === 1 && isZip(files[0]?.name || '') && (
              <p style={{ fontSize: 11, textAlign: 'center', color: '#2D6A6A', fontWeight: 600 }}>
                Class ZIP detected — will extract and compare all student files inside.
              </p>
            )}

            {/* ── View Results button (shown after analysis) ── */}
            {results && !running && (
              <button
                onClick={() => setDrawerOpen(true)}
                style={{
                  width: '100%', padding: '13px 20px', borderRadius: 14, border: 'none',
                  background: '#1A1714', color: 'white',
                  fontSize: 14, fontWeight: 800, cursor: 'pointer',
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10,
                  transition: 'background 0.15s',
                }}
                onMouseEnter={e => e.currentTarget.style.background = '#2D2825'}
                onMouseLeave={e => e.currentTarget.style.background = '#1A1714'}
              >
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><polyline points="9 18 15 12 9 6"/></svg>
                View {rawPairs.length} Result{rawPairs.length !== 1 ? 's' : ''}
                {critCount > 0 && (
                  <span style={{ fontSize: 11, fontWeight: 700, padding: '2px 8px', borderRadius: 10, background: '#CF7249', color: 'white', marginLeft: 4 }}>
                    {critCount} critical
                  </span>
                )}
              </button>
            )}
          </div></div>{/* close double wrappers */}
        </div>{/* close single-col */}
      </div>{/* close max-w container */}

      {/* ─────────────────────────────────────────────── */}
      {/* RESULTS DRAWER — slides in from the right over the full viewport */}
      {/* ─────────────────────────────────────────────── */}
      {drawerOpen && (
        <>
          {/* Backdrop */}
          <div
            onClick={() => setDrawerOpen(false)}
            style={{
              position: 'fixed', inset: 0, background: 'rgba(26,23,20,0.45)',
              backdropFilter: 'blur(4px)', zIndex: 40,
            }}
          />

          {/* Drawer panel */}
          <div style={{
            position: 'fixed', top: 0, right: 0, bottom: 0,
            width: 'min(96vw, 1000px)',
            background: '#F7F3EE',
            zIndex: 50,
            display: 'flex', flexDirection: 'column',
            boxShadow: '-8px 0 40px rgba(0,0,0,0.18)',
            animation: 'slideIn 0.3s cubic-bezier(0.32,0,0.67,0) forwards',
          }}>
            {/* Drawer header */}
            <div style={{
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              padding: '18px 24px', background: 'white', borderBottom: '1px solid #E8E1D8',
              flexShrink: 0,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                <button
                  onClick={() => setDrawerOpen(false)}
                  style={{ display:'flex', alignItems:'center', justifyContent:'center', width:32, height:32, borderRadius:10, border:'1px solid #E8E1D8', background:'white', cursor:'pointer', color:'#6B6560' }}
                >
                  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M18 6L6 18M6 6l12 12"/></svg>
                </button>
                <div>
                  <p style={{ fontSize: 16, fontWeight: 800, color: '#1A1714' }}>Analysis Results</p>
                  <p style={{ fontSize: 11, color: '#A8A29E' }}>{rawPairs.length} pair{rawPairs.length !== 1 ? 's' : ''} · {filtered.length} shown</p>
                </div>
              </div>

              {/* Drawer controls */}
              <div style={{ display:'flex', alignItems:'center', gap:8 }}>
                {/* Threshold */}
                <div style={{ display:'flex', alignItems:'center', gap:8, padding:'6px 12px', borderRadius:10, background:'#F7F3EE', border:'1px solid #E8E1D8' }}>
                  <span style={{ fontSize:11, color:'#6B6560', fontWeight:600 }}>Min</span>
                  <input type="range" min="0" max="1" step="0.05" value={threshold} onChange={e => setThreshold(parseFloat(e.target.value))} style={{ width:80 }} />
                  <span style={{ fontSize:12, fontWeight:800, color:'#CF7249', width:32 }}>{Math.round(threshold*100)}%</span>
                </div>
                {/* Filter pills */}
                <div style={{ display:'flex', gap:3 }}>
                  {[{v:'all',l:'All'},{v:'critical',l:'Critical'},{v:'high',l:'High'},{v:'medium',l:'Medium'}].map(({v,l}) => (
                    <button key={v} onClick={() => setFilter(v)} style={{
                      padding:'5px 11px', borderRadius:8,
                      border: filter===v ? '1.5px solid #CF7249' : '1.5px solid #E8E1D8',
                      background: filter===v ? '#CF7249' : 'white',
                      color: filter===v ? 'white' : '#6B6560',
                      fontSize:11, fontWeight:700, cursor:'pointer',
                    }}>{l}</button>
                  ))}
                </div>
                {/* CSV */}
                <div style={{ display:'flex', alignItems:'stretch', borderRadius:8, overflow:'hidden', border:'1.5px solid #B8D9D9' }}>
                  {[{mode:'summary',label:'Summary'},{mode:'technical',label:'Technical'}].map(({mode,label}) => (
                    <button key={mode} onClick={() => handleDownloadCsv(mode)} disabled={!!csvMode || files.length < 2}
                      style={{
                        display:'inline-flex', alignItems:'center', gap:4,
                        padding:'5px 10px', background: csvMode===mode ? '#EBF4F4' : 'white',
                        color:'#2D6A6A', fontSize:11, fontWeight:700,
                        border:'none', borderRight: mode==='summary' ? '1px solid #B8D9D9' : 'none',
                        cursor: files.length < 2 ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {csvMode===mode ? <span style={{width:9,height:9,border:'2px solid #B8D9D9',borderTopColor:'#2D6A6A',borderRadius:'50%',display:'inline-block',animation:'spin 0.7s linear infinite'}}/> : <IcoDownload />}
                      {csvMode===mode ? 'Exporting…' : label}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Stats row */}
            <div style={{ display:'grid', gridTemplateColumns:'repeat(4,1fr)', gap:10, padding:'16px 24px', flexShrink:0 }}>
              <StatCard label="Total Pairs"   value={rawPairs.length} />
              <StatCard label="Critical ≥85%" value={critCount}  color={critCount  > 0 ? '#CF7249' : '#A8A29E'} />
              <StatCard label="High 70–85%"   value={highCount}  color={highCount  > 0 ? '#C4827A' : '#A8A29E'} />
              <StatCard label="Avg Score"     value={pct(avgScore)} />
            </div>

            {/* Alerts */}
            {critCount > 0 && (
              <div style={{ margin:'0 24px 12px', display:'flex', alignItems:'center', gap:10, padding:'11px 14px', borderRadius:12, background:'#FEF3EC', border:'1px solid #FCDDC5', color:'#CF7249', flexShrink:0 }}>
                <IcoAlert />
                <p style={{ fontSize:13, fontWeight:600 }}>{critCount} pair{critCount!==1?'s':''} with ≥85% similarity — immediate review recommended.</p>
              </div>
            )}

            {/* Pair list — scrollable */}
            <div style={{ flex:1, overflowY:'auto', padding:'0 24px 24px' }}>
              {filtered.length === 0 ? (
                <div style={{ display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', padding:'60px 24px', background:'white', border:'2px dashed #E8E1D8', borderRadius:16, textAlign:'center', marginTop:8 }}>
                  <IcoCheck />
                  <p style={{ fontSize:14, fontWeight:700, color:'#1A1714', marginTop:10 }}>No pairs above {Math.round(threshold*100)}%</p>
                  <p style={{ fontSize:11, color:'#A8A29E', marginTop:4 }}>Lower the threshold or change the filter.</p>
                </div>
              ) : (
                <div style={{ display:'flex', flexDirection:'column', gap:10, paddingTop:8 }}>
                  {filtered.map((pair, i) => (
                    <PairCard key={pair.pair_id || i} pair={pair} index={i} getScore={getScore} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}


