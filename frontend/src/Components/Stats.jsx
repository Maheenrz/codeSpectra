import React from 'react';

const stats = [
  { number: '10K+', label: 'Files Analyzed' },
  { number: '500+', label: 'Active Users'    },
  { number: '99%',  label: 'Detection Accuracy' },
  { number: '24/7', label: 'Support'         },
];

const Stats = () => (
  <section className="py-20 bg-gray-50">
    <div className="px-16 xl:px-24 max-w-screen-2xl mx-auto">
      <div className="bg-indigo-100 rounded-3xl px-12 py-14 shadow-sm">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10">
          {stats.map((s, i) => (
            <div key={i} className="text-center">
              {/* Big number */}
              <div className="text-5xl xl:text-6xl font-extrabold text-indigo-600 mb-2 tracking-tight">
                {s.number}
              </div>
              {/* Divider */}
              <div className="w-8 h-0.5 bg-indigo-300 mx-auto mb-3 rounded-full" />
              {/* Label */}
              <div className="text-gray-500 text-sm font-medium tracking-wide uppercase">
                {s.label}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  </section>
);

export default Stats;