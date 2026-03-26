import React from 'react';
import { useNavigate } from 'react-router-dom';

// ─── Animated counter (CSS-only via Tailwind) ─────────────────────────────────

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

            {/* Headline — Pixelify for "Plagiarism", DM Sans for rest */}
            <h1 className="text-[clamp(2.8rem,6vw,5rem)] font-bold text-[#1A1714] leading-[1.08] tracking-tight mb-6">
              Detect Code<br />
              <span
                className="text-[#CF7249]"
                style={{ fontFamily: "'Pixelify Sans', monospace" }}
              >
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
              <button
                onClick={() => navigate('/register')}
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-2xl bg-[#CF7249] text-white font-semibold text-base hover:bg-[#B85E38] transition-colors shadow-lg shadow-[#CF7249]/20"
              >
                Get Started
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
              <button
                onClick={() => navigate('/login')}
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-2xl bg-white border border-[#E8E1D8] text-[#1A1714] font-semibold text-base hover:bg-[#F7F3EE] transition-colors"
              >
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

          {/* ── RIGHT — redesigned card cluster ── */}
          <div className="relative">
            {/* Main analysis card */}
            <div className="bg-white rounded-3xl border border-[#E8E1D8] shadow-xl shadow-black/5 p-7">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#A8A29E] mb-1">Live Analysis</p>
                  <p className="text-base font-bold text-[#1A1714]">Assignment #3 — Data Structures</p>
                </div>
                <span className="flex items-center gap-1.5 text-[11px] font-bold px-3 py-1.5 rounded-full bg-[#EBF4F4] text-[#2D6A6A]">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#2D6A6A] animate-pulse" />
                  Running
                </span>
              </div>

              {/* Score rows — big orange bar cards */}
              <div className="space-y-2.5 mb-6">
                {[
                  { label: 'Type-1 Exact Copy',   val: 92, color: '#C4827A', bg: '#FAEDEC' },
                  { label: 'Type-2 Renamed Vars',  val: 78, color: '#CF7249', bg: '#FEF3EC' },
                  { label: 'Type-3 Structural',    val: 61, color: '#2D6A6A', bg: '#EBF4F4' },
                  { label: 'Type-4 Semantic',      val: 44, color: '#8B9BB4', bg: '#EFF2F7' },
                ].map(({ label, val, color, bg }) => (
                  <div key={label} className="flex items-center gap-3 px-4 py-3 rounded-2xl" style={{ background: bg }}>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-center mb-1.5">
                        <span className="text-xs font-semibold" style={{ color }}>{label}</span>
                        <span className="text-sm font-black" style={{ color }}>{val}%</span>
                      </div>
                      <div className="h-1.5 bg-white/70 rounded-full overflow-hidden">
                        <div className="h-full rounded-full" style={{ width: `${val}%`, background: color }} />
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Alert row */}
              <div className="flex items-center gap-3 px-4 py-3.5 rounded-2xl bg-[#FAEDEC] border border-[#F0C4C0]">
                <div className="w-7 h-7 rounded-xl bg-[#C4827A]/20 flex items-center justify-center flex-shrink-0">
                  <svg width="14" height="14" fill="none" stroke="#C4827A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
                    <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
                    <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
                  </svg>
                </div>
                <p className="text-sm font-semibold text-[#C4827A]">3 pairs flagged for review</p>
              </div>
            </div>

            {/* Floating stat chips */}
            <div className="absolute -top-4 -right-4 bg-[#CF7249] text-white px-4 py-2.5 rounded-2xl shadow-lg shadow-[#CF7249]/30 text-xs font-bold">
              99% accuracy
            </div>
            <div className="absolute -bottom-4 -left-4 bg-white border border-[#E8E1D8] px-4 py-2.5 rounded-2xl shadow-lg text-xs font-bold text-[#1A1714] flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#2D6A6A]" />
              24 submissions analyzed
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
