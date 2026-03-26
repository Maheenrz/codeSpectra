import React from 'react';
import { Link } from 'react-router-dom';

const Footer = () => (
  <footer className="bg-white border-t border-[#E8E1D8] py-12">
    <div className="max-w-6xl mx-auto px-6">
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
        <div>
          <Link to="/" className="font-pixelify text-xl text-[#CF7249] tracking-wide">CodeSpectra</Link>
          <p className="text-sm text-[#A8A29E] mt-2 max-w-xs">
            Academic plagiarism detection powered by Type 1–4 clone analysis.
          </p>
        </div>
        <div className="flex flex-wrap gap-8 text-sm text-[#6B6560]">
          <div className="space-y-2">
            <p className="font-bold text-[#1A1714] text-xs uppercase tracking-wider">Product</p>
            <Link to="/register" className="block hover:text-[#CF7249] transition-colors">Get Started</Link>
            <Link to="/login" className="block hover:text-[#CF7249] transition-colors">Sign In</Link>
          </div>
          <div className="space-y-2">
            <p className="font-bold text-[#1A1714] text-xs uppercase tracking-wider">Detection</p>
            <p>Type-1 Exact Copy</p>
            <p>Type-2 Renamed Vars</p>
            <p>Type-3 Structural</p>
            <p>Type-4 Semantic</p>
          </div>
        </div>
      </div>
      <div className="mt-10 pt-6 border-t border-[#F0EBE3] flex items-center justify-between">
        <p className="text-xs text-[#A8A29E]">© 2025 CodeSpectra. Final Year Project.</p>
        <div className="flex items-center gap-1.5 text-xs text-[#A8A29E]">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
          System operational
        </div>
      </div>
    </div>
  </footer>
);

export default Footer;
