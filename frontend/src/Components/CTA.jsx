import React from 'react';
import { useNavigate } from 'react-router-dom';

const CTA = () => {
  const navigate = useNavigate();
  return (
    <section className="bg-[#F7F3EE] py-28">
      <div className="max-w-6xl mx-auto px-6">
        <div
          className="rounded-[2rem] p-14 md:p-20 text-center relative overflow-hidden"
          style={{ background: '#1A1714' }}
        >
          {/* dot-grid */}
          <div className="absolute inset-0 opacity-10 pointer-events-none"
            style={{ backgroundImage: 'radial-gradient(circle, #CF7249 1px, transparent 1px)', backgroundSize: '28px 28px' }} />

          {/* decorative orange blobs */}
          <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-[#CF7249]/10 blur-3xl pointer-events-none" />
          <div className="absolute -bottom-12 -left-12 w-48 h-48 rounded-full bg-[#CF7249]/10 blur-3xl pointer-events-none" />

          <div className="relative z-10">
            <span className="inline-block text-xs font-bold tracking-[0.2em] uppercase text-[#CF7249] px-4 py-1.5 rounded-full bg-[#CF7249]/10 border border-[#CF7249]/20 mb-6">
              Get Started Today
            </span>
            <h2
              className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight"
              style={{ fontFamily: "'Pixelify Sans', monospace" }}
            >
              Ready to detect<br />
              <span className="text-[#CF7249]">plagiarism</span> accurately?
            </h2>
            <p className="text-[#A8A29E] text-lg mb-10 max-w-lg mx-auto leading-relaxed">
              Create your first course, set up an assignment, and run analysis in minutes.
            </p>
            <div className="flex flex-wrap gap-4 justify-center">
              <button
                onClick={() => navigate('/register')}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl bg-[#CF7249] text-white text-base font-bold hover:bg-[#B85E38] transition-colors shadow-xl shadow-[#CF7249]/25"
              >
                Create Free Account
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7"/>
                </svg>
              </button>
              <button
                onClick={() => navigate('/login')}
                className="inline-flex items-center gap-2 px-8 py-4 rounded-2xl border border-white/20 text-white text-base font-semibold hover:bg-white/10 transition-colors"
              >
                Sign In
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default CTA;
