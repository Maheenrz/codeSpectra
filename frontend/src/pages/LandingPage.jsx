import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import iconGif from '../assets/icon.gif';

const LandingPage = () => {
  const [showIcon, setShowIcon] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const iconTimer = setTimeout(() => setShowIcon(true), 1000);
    const navTimer = setTimeout(() => navigate('/home'), 5000);
    return () => {
      clearTimeout(iconTimer);
      clearTimeout(navTimer);
    };
  }, [navigate]);

  return (
    /* landing-container: full screen, centered, bg matches --bg var */
    <div className="relative w-screen h-screen bg-[#f4f4f4] overflow-hidden flex justify-center items-center">

      {/* landing-content */}
      <div className="relative z-10 text-center">

        {/* logo-text-wrapper: fadeInUp on mount */}
        <div className="opacity-0 animate-fade-in-up">

          {/* logo-text: huge pixelify font, purple, glow via drop-shadow */}
          <span
            className="
              font-pixelify font-bold tracking-widest
              text-[clamp(3rem,10vw,8rem)]
              text-[#9799ff]
              [text-shadow:0_0_20px_#c5c9f8,0_0_40px_#c5c9f8]
            "
          >
            C
            {showIcon ? (
              <img
                src={iconGif}
                alt="o"
                className="
                  inline-block align-middle
                  w-[0.9em] h-[0.9em]
                  mx-[-0.05em]
                  opacity-0 animate-icon-appear
                  mix-blend-screen
                  brightness-130 contrast-120
                "
              />
            ) : (
              'o'
            )}
            deSpectra
          </span>
        </div>

        {/* tagline: fade in with delay */}
        <p
          className="
            opacity-0 animate-fade-in
            mt-4 uppercase tracking-[0.15em]
            text-[clamp(1rem,3vw,1.5rem)]
            text-[#6b7280]
            font-normal
          "
        >
          AI-Powered Code Plagiarism Detection
        </p>

        {/* loading dots */}
        <div className="flex justify-center gap-3 mt-12">
          <span className="w-3 h-3 rounded-full bg-[#9799ff] shadow-[0_0_20px_#c5c9f8] animate-dot-bounce" />
          <span className="w-3 h-3 rounded-full bg-[#9799ff] shadow-[0_0_20px_#c5c9f8] animate-dot-bounce-2" />
          <span className="w-3 h-3 rounded-full bg-[#9799ff] shadow-[0_0_20px_#c5c9f8] animate-dot-bounce-3" />
        </div>
      </div>

      {/* version badge: absolute bottom-right */}
      <div
        className="
          absolute bottom-8 right-8
          bg-[rgba(99,102,241,0.1)]
          border-2 border-[#c5c9f8]
          px-4 py-2 rounded-full
          text-sm font-semibold text-[#9799ff]
          backdrop-blur-sm
          animate-badge-pulse
        "
      >
        v1.0
      </div>
    </div>
  );
};

export default LandingPage;