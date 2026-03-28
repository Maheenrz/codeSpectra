import React from 'react';
import { useNavigate } from 'react-router-dom';

// ── Minimalist SVG illustration — two files being scanned for clones ──────────
const PlagiarismScanIllustration = () => (
  <svg
    viewBox="0 0 520 420"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    className="w-full h-full"
    style={{ maxHeight: 420 }}
  >
    {/* ── Background subtle grid ── */}
    <defs>
      <pattern id="grid" x="0" y="0" width="28" height="28" patternUnits="userSpaceOnUse">
        <circle cx="1" cy="1" r="1" fill="#CF7249" opacity="0.12"/>
      </pattern>
      <linearGradient id="fadeLeft"  x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#F7F3EE" stopOpacity="1"/><stop offset="100%" stopColor="#F7F3EE" stopOpacity="0"/></linearGradient>
      <linearGradient id="fadeRight" x1="0" y1="0" x2="1" y2="0"><stop offset="0%" stopColor="#F7F3EE" stopOpacity="0"/><stop offset="100%" stopColor="#F7F3EE" stopOpacity="1"/></linearGradient>
    </defs>
    <rect width="520" height="420" fill="url(#grid)"/>
    <rect width="80"  height="420" fill="url(#fadeLeft)"/>
    <rect x="440" width="80" height="420" fill="url(#fadeRight)"/>

    {/* ════════════════════════════════════════════════
        FILE A — left card
    ════════════════════════════════════════════════ */}
    <rect x="24" y="60" width="176" height="230" rx="14" fill="white" stroke="#E8E1D8" strokeWidth="1.5"/>
    {/* card header */}
    <rect x="24" y="60" width="176" height="38" rx="14" fill="#FEF3EC"/>
    <rect x="24" y="84" width="176" height="14" fill="#FEF3EC"/>
    <circle cx="44" cy="79" r="5" fill="#CF7249" opacity="0.7"/>
    <circle cx="58" cy="79" r="5" fill="#CF7249" opacity="0.35"/>
    <rect x="70" y="74" width="76" height="10" rx="5" fill="#CF7249" opacity="0.25"/>
    {/* code lines */}
    {[
      { y: 116, w: 120, color: '#CF7249', op: 1 },
      { y: 132, w: 90,  color: '#E8D5C8', op: 1 },
      { y: 148, w: 140, color: '#CF7249', op: 0.5 },
      { y: 164, w: 70,  color: '#E8D5C8', op: 1 },
      { y: 180, w: 130, color: '#CF7249', op: 1 },   // matched line A
      { y: 196, w: 100, color: '#E8D5C8', op: 1 },
      { y: 212, w: 115, color: '#CF7249', op: 0.4 },
      { y: 228, w: 80,  color: '#E8D5C8', op: 1 },
      { y: 244, w: 125, color: '#CF7249', op: 1 },   // matched line B
      { y: 260, w: 95,  color: '#E8D5C8', op: 1 },
    ].map(({ y, w, color, op }, i) => (
      <rect key={i} x="40" y={y} width={w} height="9" rx="4.5" fill={color} opacity={op * 0.6}/>
    ))}
    {/* highlight rows — matched lines */}
    <rect x="24" y="174" width="176" height="18" rx="4" fill="#CF7249" opacity="0.08"/>
    <rect x="24" y="238" width="176" height="18" rx="4" fill="#CF7249" opacity="0.08"/>

    {/* Student A label */}
    <rect x="36" y="302" width="96" height="20" rx="10" fill="#FEF3EC"/>
    <rect x="42" y="308" width="84" height="8" rx="4" fill="#CF7249" opacity="0.5"/>

    {/* ════════════════════════════════════════════════
        FILE B — right card
    ════════════════════════════════════════════════ */}
    <rect x="320" y="60" width="176" height="230" rx="14" fill="white" stroke="#E8E1D8" strokeWidth="1.5"/>
    {/* card header */}
    <rect x="320" y="60" width="176" height="38" rx="14" fill="#EBF4F4"/>
    <rect x="320" y="84" width="176" height="14" fill="#EBF4F4"/>
    <circle cx="340" cy="79" r="5" fill="#2D6A6A" opacity="0.7"/>
    <circle cx="354" cy="79" r="5" fill="#2D6A6A" opacity="0.35"/>
    <rect x="366" y="74" width="76" height="10" rx="5" fill="#2D6A6A" opacity="0.25"/>
    {/* code lines (slightly different widths — renamed vars) */}
    {[
      { y: 116, w: 108, color: '#2D6A6A', op: 1 },
      { y: 132, w: 95,  color: '#B8D9D9', op: 1 },
      { y: 148, w: 130, color: '#2D6A6A', op: 0.5 },
      { y: 164, w: 75,  color: '#B8D9D9', op: 1 },
      { y: 180, w: 128, color: '#2D6A6A', op: 1 },   // matched line A
      { y: 196, w: 98,  color: '#B8D9D9', op: 1 },
      { y: 212, w: 110, color: '#2D6A6A', op: 0.4 },
      { y: 228, w: 85,  color: '#B8D9D9', op: 1 },
      { y: 244, w: 122, color: '#2D6A6A', op: 1 },   // matched line B
      { y: 260, w: 90,  color: '#B8D9D9', op: 1 },
    ].map(({ y, w, color, op }, i) => (
      <rect key={i} x="336" y={y} width={w} height="9" rx="4.5" fill={color} opacity={op * 0.6}/>
    ))}
    {/* highlight rows — matched lines */}
    <rect x="320" y="174" width="176" height="18" rx="4" fill="#2D6A6A" opacity="0.08"/>
    <rect x="320" y="238" width="176" height="18" rx="4" fill="#2D6A6A" opacity="0.08"/>

    {/* Student B label */}
    <rect x="332" y="302" width="96" height="20" rx="10" fill="#EBF4F4"/>
    <rect x="338" y="308" width="84" height="8" rx="4" fill="#2D6A6A" opacity="0.5"/>

    {/* ════════════════════════════════════════════════
        CONNECTOR LINES — showing matched fragments
    ════════════════════════════════════════════════ */}
    {/* Match line A (row 180) */}
    <path d="M200 183 C260 183, 260 183, 320 183" stroke="#CF7249" strokeWidth="1.5" strokeDasharray="5 4" opacity="0.6"/>
    {/* Match line B (row 244) */}
    <path d="M200 247 C260 247, 260 247, 320 247" stroke="#CF7249" strokeWidth="1.5" strokeDasharray="5 4" opacity="0.6"/>

    {/* ════════════════════════════════════════════════
        CENTRE SCANNER — magnifying glass + score
    ════════════════════════════════════════════════ */}
    {/* centre circle */}
    <circle cx="260" cy="175" r="46" fill="white" stroke="#E8E1D8" strokeWidth="1.5"/>
    <circle cx="260" cy="175" r="36" fill="#FEF3EC"/>

    {/* scan arc */}
    <circle cx="260" cy="175" r="36" stroke="#CF7249" strokeWidth="2.5" strokeDasharray="226" strokeDashoffset="57" strokeLinecap="round" opacity="0.8"/>

    {/* % score */}
    <text x="260" y="170" textAnchor="middle" fontFamily="'DM Sans', system-ui, sans-serif" fontWeight="800" fontSize="22" fill="#CF7249">87%</text>
    <text x="260" y="186" textAnchor="middle" fontFamily="'DM Sans', system-ui, sans-serif" fontWeight="600" fontSize="9" fill="#A8A29E" letterSpacing="1">MATCH</text>

    {/* ════════════════════════════════════════════════
        BOTTOM — result badge
    ════════════════════════════════════════════════ */}
    <rect x="170" y="352" width="180" height="42" rx="21" fill="white" stroke="#E8E1D8" strokeWidth="1.5"/>
    <circle cx="196" cy="373" r="7" fill="#FAEDEC"/>
    <circle cx="196" cy="373" r="4" fill="#C4827A"/>
    <text x="212" y="377" fontFamily="'DM Sans', system-ui, sans-serif" fontWeight="700" fontSize="12" fill="#1A1714">3 pairs flagged</text>

    {/* ════════════════════════════════════════════════
        TOP RIGHT — accuracy badge
    ════════════════════════════════════════════════ */}
    <rect x="386" y="28" width="110" height="34" rx="17" fill="#CF7249"/>
    <text x="441" y="50" textAnchor="middle" fontFamily="'DM Sans', system-ui, sans-serif" fontWeight="800" fontSize="13" fill="white">99% accuracy</text>

    {/* ════════════════════════════════════════════════
        TOP LEFT — "LIVE" badge
    ════════════════════════════════════════════════ */}
    <rect x="24" y="28" width="72" height="24" rx="12" fill="white" stroke="#E8E1D8" strokeWidth="1.2"/>
    <circle cx="38" cy="40" r="4" fill="#2D6A6A"/>
    <text x="49" y="44" fontFamily="'DM Sans', system-ui, sans-serif" fontWeight="700" fontSize="10" fill="#2D6A6A">LIVE</text>

    {/* ════════════════════════════════════════════════
        TYPE CHIPS
    ════════════════════════════════════════════════ */}
    {[
      { x: 40,  y: 340, label: 'Type-1', color: '#C4827A', bg: '#FAEDEC' },
      { x: 120, y: 340, label: 'Type-2', color: '#CF7249', bg: '#FEF3EC' },
      { x: 360, y: 340, label: 'Type-3', color: '#2D6A6A', bg: '#EBF4F4' },
      { x: 438, y: 340, label: 'Type-4', color: '#8B9BB4', bg: '#EFF2F7' },
    ].map(({ x, y, label, color, bg }) => (
      <g key={label}>
        <rect x={x} y={y} width={62} height={22} rx="11" fill={bg}/>
        <text x={x + 31} y={y + 15} textAnchor="middle"
          fontFamily="'DM Sans', system-ui, sans-serif" fontWeight="800" fontSize="9.5"
          fill={color} letterSpacing="0.5">{label}</text>
      </g>
    ))}
  </svg>
);

const Hero = () => {
  const navigate = useNavigate();

  return (
    <section className="min-h-screen bg-[#F7F3EE] flex items-center pt-14">
      <div className="max-w-6xl mx-auto px-6 py-20 w-full">
        <div className="grid lg:grid-cols-2 gap-16 items-center">

          {/* ── LEFT ── */}
          <div>
            {/* Pill badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-white border border-[#E8E1D8] text-xs font-semibold text-[#CF7249] mb-8 shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-[#CF7249] animate-pulse" />
              Type 1–4 Clone Detection
            </div>

            {/* Headline */}
            <h1 className="text-[clamp(2.8rem,6vw,5rem)] font-bold text-[#1A1714] leading-[1.08] tracking-tight mb-6">
              Detect Code<br />
              <span className="text-[#CF7249]" style={{ fontFamily: "'Pixelify Sans', monospace" }}>
                Plagiarism
              </span>
              <br />
              with Precision.
            </h1>

            <p className="text-lg text-[#6B6560] mb-10 max-w-md leading-relaxed">
              Advanced structural and semantic detection across all 4 clone types.
              Built for educators, designed for accuracy.
            </p>

            <div className="flex flex-wrap gap-3 mb-10">
              <button onClick={() => navigate('/register')}
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-2xl bg-[#CF7249] text-white font-semibold text-base hover:bg-[#B85E38] transition-colors shadow-lg shadow-[#CF7249]/20">
                Get Started
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7"/></svg>
              </button>
              <button onClick={() => navigate('/login')}
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-2xl bg-white border border-[#E8E1D8] text-[#1A1714] font-semibold text-base hover:bg-[#F7F3EE] transition-colors">
                Sign in
              </button>
            </div>

            {/* Language strip */}
            <div className="flex flex-wrap gap-2">
              {['C++', 'Java', 'Python', 'JavaScript', 'TypeScript'].map(l => (
                <span key={l} className="text-xs font-semibold px-3 py-1.5 rounded-full bg-white border border-[#E8E1D8] text-[#6B6560]">{l}</span>
              ))}
            </div>
          </div>

          {/* ── RIGHT — minimalist illustration ── */}
          <div className="relative flex items-center justify-center">
            <PlagiarismScanIllustration />
          </div>

        </div>
      </div>
    </section>
  );
};

export default Hero;
