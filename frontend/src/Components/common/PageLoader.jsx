// frontend/src/Components/common/PageLoader.jsx
// Replaces the plain LoadingSpinner everywhere.
// Uses the same visual identity as LandingPage — dot-grid, CodeSpectra logo,
// animated orange dots — so every loading state feels intentional.
//
// Usage:
//   import PageLoader from '../Components/common/PageLoader';
//   if (loading) return <PageLoader message="Loading courses…" />;
//
// Optionally pass a `message` prop for context-specific text.

import { useState, useEffect } from 'react';
import iconGif from '../../assets/icon.gif';

const PageLoader = ({ message = '' }) => {
  const [showIcon, setShowIcon] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setShowIcon(true), 400);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="relative w-full min-h-screen bg-[#F7F3EE] overflow-hidden flex items-center justify-center">

      {/* Dot-grid — identical to LandingPage */}
      <div
        className="absolute inset-0 opacity-[0.15] pointer-events-none"
        style={{
          backgroundImage: 'radial-gradient(circle, #CF7249 1px, transparent 1px)',
          backgroundSize: '32px 32px',
        }}
      />

      {/* Centre card */}
      <div className="relative z-10 flex flex-col items-center text-center select-none">

        {/* Logo — same font + glow as LandingPage */}
        <div style={{ animation: 'csLoaderFadeUp 0.5s ease forwards' }}>
          <span
            className="font-pixelify font-bold tracking-widest text-[#CF7249]"
            style={{
              fontSize: 'clamp(2.2rem, 7vw, 5rem)',
              textShadow: '0 0 24px rgba(207,114,73,0.28), 0 0 48px rgba(207,114,73,0.12)',
            }}
          >
            C
            {showIcon ? (
              <img
                src={iconGif}
                alt="o"
                className="inline-block align-middle mix-blend-multiply"
                style={{
                  width: '0.9em', height: '0.9em',
                  marginLeft: '-0.05em', marginRight: '-0.05em',
                  animation: 'csLoaderIconAppear 0.35s ease forwards',
                }}
              />
            ) : 'o'}
            deSpectra
          </span>
        </div>

        {/* Context message */}
        {message ? (
          <p
            className="mt-3 text-[#6B6560] font-semibold"
            style={{
              fontSize: 'clamp(0.7rem, 1.5vw, 0.875rem)',
              letterSpacing: '0.04em',
              animation: 'csLoaderFadeUp 0.6s 0.1s ease both',
            }}
          >
            {message}
          </p>
        ) : (
          <p
            className="mt-3 uppercase text-[#A8A29E] font-semibold tracking-[0.2em]"
            style={{
              fontSize: 'clamp(0.65rem, 1.4vw, 0.8rem)',
              animation: 'csLoaderFadeUp 0.6s 0.1s ease both',
            }}
          >
            Code Plagiarism Detection
          </p>
        )}

        {/* Bouncing dots — orange */}
        <div className="flex justify-center gap-3 mt-10">
          {[0, 1, 2].map(i => (
            <span
              key={i}
              className="block w-2.5 h-2.5 rounded-full bg-[#CF7249]"
              style={{
                boxShadow: '0 0 10px rgba(207,114,73,0.45)',
                animation: `csLoaderDot 1.2s ${i * 0.18}s ease-in-out infinite`,
              }}
            />
          ))}
        </div>
      </div>

      {/* Scoped keyframes injected once */}
      <style>{`
        @keyframes csLoaderFadeUp {
          from { opacity: 0; transform: translateY(10px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        @keyframes csLoaderIconAppear {
          from { opacity: 0; transform: scale(0.7); }
          to   { opacity: 1; transform: scale(1); }
        }
        @keyframes csLoaderDot {
          0%, 80%, 100% { transform: translateY(0);    opacity: 0.45; }
          40%           { transform: translateY(-10px); opacity: 1;    }
        }
      `}</style>
    </div>
  );
};

export default PageLoader;
