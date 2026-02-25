import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    /* White always — matches hero background perfectly */
    <nav className={`fixed top-0 left-0 right-0 z-50 bg-white transition-all duration-300 ${scrolled ? 'shadow-sm border-b border-gray-100' : ''}`}>
      <div className="px-16 xl:px-24 py-4">
        <div className="flex items-center justify-between">

          {/* Logo — aligns with hero left content */}
          <Link to="/" className="font-pixelify text-2xl text-indigo-500 hover:text-indigo-600 transition-colors">
            CodeSpectra
          </Link>

          {/* Nav links — centered */}
          <div className="hidden md:flex items-center gap-10">
            {[['Features','#features'],['How It Works','#how-it-works'],['Pricing','#pricing'],['About','#about']].map(([label, href]) => (
              <a key={label} href={href} className="text-gray-500 hover:text-indigo-500 text-sm font-medium transition-colors">
                {label}
              </a>
            ))}
          </div>

          {/* Auth — aligns with right side */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => navigate('/login')}
              className="border border-gray-300 hover:border-indigo-400 text-gray-600 hover:text-indigo-500 px-5 py-2 rounded-lg text-sm font-medium transition-all"
            >
              Login
            </button>
            <button
              onClick={() => navigate('/register')}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm"
            >
              Sign Up
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;