import React from 'react';
import { useNavigate } from 'react-router-dom';

const stats = [
  { title: '99% Accuracy',        sub: 'Industry-leading precision' },
  { title: '10K+ Files Analyzed', sub: 'Trusted by developers'      },
  { title: '500+ Happy Users',    sub: 'Growing community'          },
];

const CheckIcon = () => (
  <svg className="w-5 h-5 text-indigo-400 flex-shrink-0" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const Hero = () => {
  const navigate = useNavigate();
  return (
    <section className="min-h-screen bg-white pt-20">
      <div className="flex items-center min-h-screen">

        {/* ── LEFT: Text ── push it in from left, right padding keeps gap from card */}
        <div className="w-1/2 pl-16 xl:pl-24 pr-6 flex flex-col justify-center py-16">

          <h1 className="font-extrabold text-gray-900 leading-tight mb-6" style={{ fontSize: 'clamp(2.4rem, 3.8vw, 3.6rem)' }}>
            {/* Line 1: Detect + "Code Plagiarism" in indigo — stays on one line */}
            <span className="block whitespace-nowrap">
              Detect <span className="text-indigo-400">Code Plagiarism</span>
            </span>
            {/* Line 2 */}
            <span className="block whitespace-nowrap">
              with <span className="text-indigo-400">AI-powered</span>
            </span>
            {/* Line 3 */}
            <span className="block">precision.</span>
          </h1>

          <p className="text-gray-400 text-lg mb-10 max-w-md leading-relaxed">
            Advanced detection powered by Type 1–4 semantic and structural algorithms.
          </p>

          <div className="flex flex-wrap gap-4">
            <button
              onClick={() => navigate('/register')}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-4 rounded-xl text-base font-semibold transition-colors shadow-md"
            >
              Get Started →
            </button>
            <button className="border-2 border-indigo-400 text-indigo-500 hover:bg-indigo-50 px-8 py-4 rounded-xl text-base font-semibold transition-colors">
              Watch Demo ▶
            </button>
          </div>
        </div>

        {/* ── RIGHT: Card — minimal right padding so it sits close to screen edge ── */}
        <div className="w-1/2 pr-20 pl-4 flex items-center justify-end">
          <div className="bg-indigo-100 rounded-3xl p-4 w-full max-w-lg shadow-lg">

            {/* Top white card */}
            <div className="bg-white rounded-2xl px-10 py-10 flex flex-col items-center text-center mb-4 shadow-sm">
              <div className="w-20 h-20 bg-indigo-400 rounded-full flex items-center justify-center mb-5 shadow-md">
                <svg className="w-9 h-9 text-white" fill="none" stroke="currentColor" strokeWidth={2} viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
                </svg>
              </div>
              <h3 className="text-3xl font-bold text-indigo-600 mb-1">AI Analysis</h3>
              <p className="text-gray-400 text-sm">Deep code analysis in seconds</p>
            </div>

            {/* Stat rows */}
            <div className="flex flex-col gap-3">
              {stats.map((s, i) => (
                <div key={i} className="bg-white rounded-2xl px-5 py-4 flex items-center gap-4 shadow-sm">
                  <CheckIcon />
                  <div>
                    <p className="font-bold text-gray-800 text-sm">{s.title}</p>
                    <p className="text-gray-400 text-xs mt-0.5">{s.sub}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>
    </section>
  );
};

export default Hero;