import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Login = () => {
  const [formData, setFormData] = useState({ email: '', password: '' });
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);
  const { login }  = useAuth();
  const navigate   = useNavigate();

  const handleChange = e => setFormData(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(''); setLoading(true);
    try {
      await login(formData);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed. Please try again.');
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center px-4">
      <div className="w-full max-w-md">

        {/* Logo */}
        <div className="text-center mb-8">
          <Link to="/" className="font-pixelify text-3xl text-[#CF7249] tracking-wide">
            CodeSpectra
          </Link>
          <h2 className="mt-4 text-2xl font-bold text-[#1A1714]">Welcome back</h2>
          <p className="mt-1 text-sm text-[#6B6560]">Sign in to your account</p>
        </div>

        {/* Card */}
        <div className="bg-white rounded-2xl border border-[#E8E1D8] shadow-sm p-8">
          {error && (
            <div className="mb-5 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">
                Email Address
              </label>
              <input
                type="email" name="email" required
                value={formData.email} onChange={handleChange}
                placeholder="you@example.com"
                className="w-full px-4 py-3 rounded-xl border border-[#E8E1D8] bg-[#F7F3EE]
                  text-sm text-[#1A1714] placeholder-[#A8A29E]
                  focus:outline-none focus:ring-2 focus:ring-[#CF7249] focus:border-transparent transition-all"
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-[#1A1714] mb-1.5">
                Password
              </label>
              <input
                type="password" name="password" required
                value={formData.password} onChange={handleChange}
                placeholder="••••••••"
                className="w-full px-4 py-3 rounded-xl border border-[#E8E1D8] bg-[#F7F3EE]
                  text-sm text-[#1A1714] placeholder-[#A8A29E]
                  focus:outline-none focus:ring-2 focus:ring-[#CF7249] focus:border-transparent transition-all"
              />
            </div>

            <button
              type="submit" disabled={loading}
              className="w-full py-3 rounded-xl bg-[#CF7249] text-white text-sm font-semibold
                hover:bg-[#B85E38] transition-colors disabled:opacity-50 disabled:cursor-not-allowed">
              {loading ? 'Signing in…' : 'Sign In'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-[#6B6560]">
            Don't have an account?{' '}
            <Link to="/register" className="text-[#CF7249] hover:text-[#B85E38] font-semibold">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
