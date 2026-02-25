import React from 'react';

const features = [
  {
    icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="3" strokeWidth={2}/><circle cx="12" cy="12" r="8" strokeWidth={2}/></svg>,
    title: 'TYPE-1 DETECTION',
    description: 'Detects exact code copies with only whitespace and comment changes. Perfect for identifying direct plagiarism.',
  },
  {
    icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>,
    title: 'TYPE-2 DETECTION',
    description: 'Identifies renamed variables and modified literals while maintaining the same structure and logic.',
  },
  {
    icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z"/></svg>,
    title: 'TYPE-3 DETECTION',
    description: 'Finds code with added, deleted, or modified statements. Detects subtle structural changes.',
  },
  {
    icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z"/></svg>,
    title: 'TYPE-4 DETECTION',
    description: 'Uses AI to detect semantically similar code with completely different implementations.',
  },
  {
    icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/></svg>,
    title: 'ADVANCED REPORTS',
    description: 'Comprehensive similarity reports with visual highlights, statistics, and detailed analysis.',
  },
  {
    icon: <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>,
    title: 'FAST RESULTS',
    description: 'Lightning-fast analysis powered by optimized algorithms. Get results in seconds, not hours.',
  },
];

const Features = () => (
  <section id="features" className="py-24 bg-gray-50">
    <div className="px-16 xl:px-24 max-w-screen-2xl mx-auto">
      <div className="text-center mb-16">
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          Powerful <span className="text-indigo-500">Detection Features</span>
        </h2>
        <p className="text-gray-400 text-lg">Industry-leading algorithms that catch every type of code plagiarism</p>
      </div>
      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((f, i) => (
          <div key={i} className="bg-white rounded-2xl p-8 hover:shadow-md transition-shadow duration-300 border border-gray-100">
            <div className="w-14 h-14 bg-indigo-500 rounded-2xl flex items-center justify-center mb-6 text-white">
              {f.icon}
            </div>
            <h3 className="text-sm font-bold text-indigo-500 mb-3 tracking-wider">{f.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed">{f.description}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default Features;