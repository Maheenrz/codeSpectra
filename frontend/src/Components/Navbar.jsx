import React, { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const IconBook = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M4 19.5A2.5 2.5 0 016.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"/>
  </svg>
);
const IconGrid = () => (
  <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
    <rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/>
  </svg>
);
const IconPlus = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);
const IconLogOut = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/>
    <polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/>
  </svg>
);
const IconKey = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 11-7.778 7.778 5.5 5.5 0 017.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
  </svg>
);
const IconScan = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/>
    <line x1="7" y1="12" x2="17" y2="12"/>
  </svg>
);
const IconChevron = () => (
  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
    <polyline points="6 9 12 15 18 9"/>
  </svg>
);

const Navbar = () => {
  const { isAuthenticated, user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = useState(false);

  const isInstructor = user?.role === 'instructor' || user?.role === 'admin';
  const isStudent    = user?.role === 'student';
  const at = (p) => location.pathname === p || location.pathname.startsWith(p + '/');

  const NavLink = ({ to, children }) => (
    <Link to={to}
      className={`flex items-center gap-1.5 text-sm font-medium transition-colors px-1 py-0.5
        ${at(to) ? 'text-[#CF7249]' : 'text-[#6B6560] hover:text-[#1A1714]'}`}>
      {children}
    </Link>
  );

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-[#F7F3EE]/95 backdrop-blur-sm border-b border-[#E8E1D8]/80">
      <div className="max-w-6xl mx-auto px-6 py-3.5 flex items-center justify-between gap-6">

        <Link to={isAuthenticated ? '/dashboard' : '/'}
          className="font-pixelify text-xl text-[#CF7249] tracking-wide hover:opacity-80 transition-opacity flex-shrink-0">
          CodeSpectra
        </Link>

        {isAuthenticated && (
          <div className="hidden md:flex items-center gap-5 flex-1">
            <NavLink to="/dashboard"><IconGrid /> Dashboard</NavLink>
            <NavLink to="/courses"><IconBook /> My Courses</NavLink>
            {isInstructor && (
              <NavLink to="/assignments/create"><IconPlus /> New Assignment</NavLink>
            )}
            <NavLink to="/analyze"><IconScan /> Analysis Tool</NavLink>
            {isStudent && (
              <NavLink to="/courses/join"><IconKey /> Join Course</NavLink>
            )}
          </div>
        )}

        {!isAuthenticated && (
          <div className="hidden md:flex items-center gap-7">
            {['Features', 'How It Works'].map(l => (
              <a key={l} href={`#${l.toLowerCase().replace(' ', '-')}`}
                className="text-sm text-[#78716C] hover:text-[#1A1714] transition-colors font-medium">
                {l}
              </a>
            ))}
          </div>
        )}

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-white border border-[#E8E1D8]">
                <div className="w-5 h-5 rounded-full bg-[#CF7249] flex items-center justify-center text-white text-[10px] font-bold">
                  {(user?.firstName?.[0] || '?').toUpperCase()}
                </div>
                <span className="text-xs font-medium text-[#1A1714]">{user?.firstName}</span>
                <span className={`text-[9px] font-bold uppercase tracking-wide px-1.5 py-0.5 rounded-full
                  ${isInstructor ? 'bg-[#FEF3EC] text-[#CF7249]' : 'bg-[#EBF4F4] text-[#2D6A6A]'}`}>
                  {user?.role}
                </span>
              </div>
              <button onClick={logout}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#E8E1D8] text-xs font-semibold text-[#6B6560] hover:bg-[#F0EBE3] transition-colors">
                <IconLogOut /> Sign out
              </button>
              <button onClick={() => setMobileOpen(o => !o)}
                className="md:hidden flex items-center justify-center w-9 h-9 rounded-lg border border-[#E8E1D8] text-[#6B6560]">
                <IconChevron />
              </button>
            </>
          ) : (
            <>
              <button onClick={() => navigate('/login')} className="btn-ghost text-sm px-4 py-2">Sign in</button>
              <button onClick={() => navigate('/register')} className="btn-orange text-sm px-4 py-2">Get started</button>
            </>
          )}
        </div>
      </div>

      {isAuthenticated && mobileOpen && (
        <div className="md:hidden bg-white border-b border-[#E8E1D8] px-6 py-4 space-y-3">
          <Link to="/dashboard" onClick={() => setMobileOpen(false)} className="flex items-center gap-2 text-sm font-medium text-[#1A1714] py-2"><IconGrid /> Dashboard</Link>
          <Link to="/courses" onClick={() => setMobileOpen(false)} className="flex items-center gap-2 text-sm font-medium text-[#1A1714] py-2"><IconBook /> My Courses</Link>
          {isInstructor && (
            <Link to="/assignments/create" onClick={() => setMobileOpen(false)} className="flex items-center gap-2 text-sm font-medium text-[#1A1714] py-2"><IconPlus /> New Assignment</Link>
          )}
          <Link to="/analyze" onClick={() => setMobileOpen(false)} className="flex items-center gap-2 text-sm font-medium text-[#1A1714] py-2"><IconScan /> Analysis Tool</Link>
          {isStudent && <Link to="/courses/join" onClick={() => setMobileOpen(false)} className="flex items-center gap-2 text-sm font-medium text-[#1A1714] py-2"><IconKey /> Join Course</Link>}
          <div className="pt-2 border-t border-[#E8E1D8]">
            <button onClick={() => { logout(); setMobileOpen(false); }} className="flex items-center gap-2 text-sm font-medium text-[#6B6560] py-2"><IconLogOut /> Sign out</button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
