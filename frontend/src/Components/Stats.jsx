import React from 'react';

const STATS = [
  { value: '4',    label: 'Clone Types',         sub: 'Type 1–4 detection',        accent: '#CF7249', bg: '#FEF3EC', border: '#FCDDC5' },
  { value: '99%',  label: 'Detection Accuracy',  sub: 'On benchmark datasets',     accent: '#2D6A6A', bg: '#EBF4F4', border: '#B8D9D9' },
  { value: '5',    label: 'Languages',            sub: 'C++, Java, Python, JS, TS', accent: '#C4827A', bg: '#FAEDEC', border: '#F0C4C0' },
  { value: '<2s',  label: 'Analysis Speed',       sub: 'Per file pair',             accent: '#8B9BB4', bg: '#EFF2F7', border: '#C8D2E0' },
];

const Stats = () => (
  <section className="bg-white py-20 border-y border-[#E8E1D8]">
    <div className="max-w-6xl mx-auto px-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {STATS.map(({ value, label, sub, accent, bg, border }) => (
          <div
            key={label}
            className="rounded-3xl p-7 border flex flex-col"
            style={{ background: bg, borderColor: border }}
          >
            <p className="text-4xl font-black mb-1.5 tracking-tight" style={{ color: accent }}>{value}</p>
            <p className="text-sm font-bold text-[#1A1714] mb-0.5">{label}</p>
            <p className="text-xs text-[#6B6560]">{sub}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default Stats;
