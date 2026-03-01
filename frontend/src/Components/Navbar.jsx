import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const navigate = useNavigate();
  const { isAuthenticated, logout } = useAuth();

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <nav className={`fixed top-0 left-0 right-0 z-50 bg-white transition-all duration-300 ${
      scrolled ? 'shadow-sm border-b border-gray-100' : ''
    }`}>
      <div className="px-16 xl:px-24 py-4">
        <div className="flex items-center justify-between">

          {/* Logo - Goes to dashboard if logged in, home if not */}
          <Link 
            to={isAuthenticated ? "/dashboard" : "/"} 
            className="font-pixelify text-2xl text-indigo-500 hover:text-indigo-600 transition-colors"
          >
            CodeSpectra
          </Link>

          {/* Nav links - Only show if NOT logged in */}
          {!isAuthenticated && (
            <div className="hidden md:flex items-center gap-10">
              <a href="#features" className="text-gray-500 hover:text-indigo-500 text-sm font-medium transition-colors">
                Features
              </a>
              <a href="#how-it-works" className="text-gray-500 hover:text-indigo-500 text-sm font-medium transition-colors">
                How It Works
              </a>
              <a href="#pricing" className="text-gray-500 hover:text-indigo-500 text-sm font-medium transition-colors">
                Pricing
              </a>
              <a href="#about" className="text-gray-500 hover:text-indigo-500 text-sm font-medium transition-colors">
                About
              </a>
            </div>
          )}

          {/* Auth buttons */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="border border-gray-300 hover:border-indigo-400 text-gray-600 hover:text-indigo-500 px-5 py-2 rounded-lg text-sm font-medium transition-all">
                  Dashboard
                </Link>
                <button
                  onClick={logout}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-colors shadow-sm"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
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
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;