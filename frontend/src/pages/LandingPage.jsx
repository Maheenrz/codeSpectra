import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import iconGif from '../assets/icon.gif';

const LandingPage = () => {
  const [showIcon, setShowIcon] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const iconTimer = setTimeout(() => setShowIcon(true), 1000);
    const navTimer  = setTimeout(() => navigate('/home'), 5000);
    return () => { clearTimeout(iconTimer); clearTimeout(navTimer); };
  }, [navigate]);

  return (
    <div className="relative w-screen h-screen bg-[#F7F3EE] overflow-hidden flex justify-center items-center">

      {/* Subtle dot-grid texture */}
      <div className="absolute inset-0 opacity-20"
        style={{ backgroundImage: 'radial-gradient(circle, #CF7249 1px, transparent 1px)', backgroundSize: '32px 32px' }} />

      {/* Content */}
      <div className="relative z-10 text-center">

        {/* Logo */}
        <div className="opacity-0 animate-fade-in-up">
          <span className="
            font-pixelify font-bold tracking-widest
            text-[clamp(3rem,10vw,8rem)]
            text-[#CF7249]
            [text-shadow:0_0_30px_rgba(207,114,73,0.3),0_0_60px_rgba(207,114,73,0.15)]
          ">
            C
            {showIcon ? (
              <img src={iconGif} alt="o"
                className="inline-block align-middle w-[0.9em] h-[0.9em] mx-[-0.05em] opacity-0 animate-icon-appear mix-blend-multiply" />
            ) : 'o'}
            deSpectra
          </span>
        </div>

        {/* Tagline */}
        <p className="
          opacity-0 animate-fade-in
          mt-4 uppercase tracking-[0.2em]
          text-[clamp(0.75rem,2vw,1rem)]
          text-[#A8A29E]
          font-semibold
        ">
          Code Plagiarism Detection
        </p>

        {/* Loading dots — orange */}
        <div className="flex justify-center gap-3 mt-12">
          <span className="w-2.5 h-2.5 rounded-full bg-[#CF7249] animate-dot-bounce"
            style={{ boxShadow: '0 0 12px rgba(207,114,73,0.5)' }} />
          <span className="w-2.5 h-2.5 rounded-full bg-[#CF7249] animate-dot-bounce-2"
            style={{ boxShadow: '0 0 12px rgba(207,114,73,0.5)' }} />
          <span className="w-2.5 h-2.5 rounded-full bg-[#CF7249] animate-dot-bounce-3"
            style={{ boxShadow: '0 0 12px rgba(207,114,73,0.5)' }} />
        </div>
      </div>

      {/* Version badge — bottom right */}
      <div className="
        absolute bottom-8 right-8
        bg-white/60 backdrop-blur-sm
        border border-[#E8E1D8]
        px-4 py-2 rounded-full
        text-sm font-semibold text-[#CF7249]
        animate-badge-pulse
      ">
        v1.0
      </div>

    </div>
  );
};

export default LandingPage;
