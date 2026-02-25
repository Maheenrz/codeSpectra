import React from 'react';

const steps = [
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
    ),
    title: 'Upload Files',
    description: 'Upload your code files or paste code snippets directly into our platform. Supports multiple programming languages and file formats.',
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    ),
    title: 'AI Analysis',
    description: 'Our advanced AI algorithms analyze your code using Type 1–4 detection methods. Deep semantic and structural analysis in seconds.',
  },
  {
    icon: (
      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
    ),
    title: 'Get Results',
    description: 'Receive comprehensive reports with similarity scores, highlighted matches, and detailed insights. Export and share with ease.',
  },
];

const HowItWorks = () => (
  <section id="how-it-works" className="py-24 bg-white">
    <div className="px-16 xl:px-24 max-w-screen-2xl mx-auto">

      {/* Heading */}
      <div className="text-center mb-20">
        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
          How It <span className="text-indigo-500">Works</span>
        </h2>
        <p className="text-gray-400 text-lg">Get started in three simple steps</p>
      </div>

      {/* Steps */}
      <div className="relative grid md:grid-cols-3 gap-8">

        {/* Connector line — sits behind the circles */}
        <div className="hidden md:block absolute top-10 left-[calc(16.67%+1.25rem)] right-[calc(16.67%+1.25rem)] h-0.5 bg-indigo-100 z-0" />

        {steps.map((step, i) => (
          <div key={i} className="relative z-10 flex flex-col items-center text-center group">

            {/* Circle */}
            <div className="w-20 h-20 rounded-full bg-indigo-500 group-hover:bg-indigo-600 flex items-center justify-center text-white shadow-lg mb-8 transition-colors duration-300">
              {step.icon}
            </div>

            {/* Step number badge */}
            <span className="absolute top-0 right-[calc(50%-2.5rem)] -translate-y-1 w-5 h-5 rounded-full bg-indigo-200 text-indigo-700 text-xs font-bold flex items-center justify-center">
              {i + 1}
            </span>

            <h3 className="text-xl font-bold text-gray-900 mb-3">{step.title}</h3>
            <p className="text-gray-400 text-sm leading-relaxed max-w-xs">{step.description}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default HowItWorks;