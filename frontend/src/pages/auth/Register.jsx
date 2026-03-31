import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    email: '', password: '', firstName: '', lastName: '',
    role: 'student', institution: '',
  });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate     = useNavigate();

  const handleChange = e => setFormData(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Registration failed. Please try again.');
    } finally { setLoading(false); }
  };

  const inputClass = `w-full px-4 py-3 rounded-xl border border-[#E8E1D8] bg-[#F7F3EE]
    text-sm text-[#1A1714] placeholder-[#A8A29E]
    focus:outline-none focus:ring-2 focus:ring-[#CF7249] focus:border-transparent transition-all`;

  const labelClass = "block text-sm font-semibold text-[#1A1714] mb-1.5";

  return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="font-pixelify text-3xl text-[#CF7249] tracking-wide">
            CodeSpectra
          </Link>
          <h2 className="mt-4 text-2xl font-bold text-[#1A1714]">Create account</h2>
          <p className="mt-1 text-sm text-[#6B6560]">Start detecting plagiarism today</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl border border-[#E8E1D8] shadow-sm p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className={labelClass}>First Name</label>
                <input type="text" name="firstName" required
                  value={formData.firstName} onChange={handleChange}
                  className={inputClass} placeholder="Maheen" />
              </div>
              <div>
                <label className={labelClass}>Last Name</label>
                <input type="text" name="lastName" required
                  value={formData.lastName} onChange={handleChange}
                  className={inputClass} placeholder="Razzaq" />
              </div>
            </div>

            <div>
              <label className={labelClass}>Email Address</label>
              <input type="email" name="email" required
                value={formData.email} onChange={handleChange}
                className={inputClass} placeholder="you@example.com" />
            </div>

            <div>
              <label className={labelClass}>Password</label>
              <input type="password" name="password" required minLength="8"
                value={formData.password} onChange={handleChange}
                className={inputClass} placeholder="••••••••" />
            </div>

            <div>
              <label className={labelClass}>Institution</label>
              <input type="text" name="institution"
                value={formData.institution} onChange={handleChange}
                className={inputClass} placeholder="University name" />
            </div>

            <div>
              <label className={labelClass}>I am a…</label>
              <select name="role" value={formData.role} onChange={handleChange}
                className={inputClass + ' cursor-pointer appearance-none'}>
                <option value="student">Student</option>
                <option value="instructor">Instructor</option>
              </select>
            </div>

            {/* Role hint */}
            <div className="grid grid-cols-2 gap-3">
              {[
                { v: 'student',    label: 'Student',    desc: 'Submit assignments', accent: '#2D6A6A', bg: '#EBF4F4' },
                { v: 'instructor', label: 'Instructor', desc: 'Create & manage',    accent: '#CF7249', bg: '#FEF3EC' },
              ].map(({ v, label, desc, accent, bg }) => (
                <button key={v} type="button" onClick={() => setFormData(p => ({ ...p, role: v }))}
                  className={`p-3 rounded-xl border-2 text-left transition-all`}
                  style={{
                    borderColor: formData.role === v ? accent : '#E8E1D8',
                    background:  formData.role === v ? bg : 'white',
                  }}>
                  <p className="text-xs font-bold" style={{ color: accent }}>{label}</p>
                  <p className="text-[10px] text-[#A8A29E] mt-0.5">{desc}</p>
                </button>
              ))}
            </div>

            <button
              type="submit" disabled={loading}
              className="w-full py-3 rounded-xl bg-[#CF7249] text-white text-sm font-semibold
                hover:bg-[#B85E38] transition-colors disabled:opacity-50 disabled:cursor-not-allowed mt-2">
              {loading ? 'Creating account…' : 'Sign Up'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-[#6B6560]">
            Already have an account?{' '}
            <Link to="/login" className="text-[#CF7249] hover:text-[#B85E38] font-semibold">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
