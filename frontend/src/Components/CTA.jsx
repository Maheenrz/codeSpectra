import React from 'react';
import { useNavigate } from 'react-router-dom';

const CTA = () => {
  const navigate = useNavigate();
  return (
    <section className="py-24 bg-white">
      <div className="px-16 xl:px-24 max-w-screen-2xl mx-auto">
        <div className="bg-gradient-to-br from-indigo-500 to-indigo-700 rounded-3xl p-16 text-center shadow-xl">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Ready to detect plagiarism?
          </h2>
          <p className="text-indigo-200 text-lg mb-10">
            Analyze code submissions and generate detailed reports today!
          </p>
          <button
            onClick={() => navigate('/register')}
            className="bg-white text-indigo-600 hover:bg-indigo-50 px-10 py-4 rounded-xl text-lg font-semibold transition-colors shadow-md"
          >
            Sign Up Now
          </button>
        </div>
      </div>
    </section>
  );
};

export default CTA;