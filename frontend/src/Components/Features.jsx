import React from 'react';

const FEATURES = [
  {
    type: 'Type-1', title: 'Exact Copy',
    desc: 'Identical code with only whitespace, comment, or formatting differences.',
    accent: '#C4827A', bg: '#FAEDEC', num: '01',
    icon: 'https://api.iconify.design/lucide:copy.svg?color=%23C4827A',
  },
  {
    type: 'Type-2', title: 'Renamed Variables',
    desc: 'Identifiers and literals renamed but overall structure is preserved.',
    accent: '#CF7249', bg: '#FEF3EC', num: '02',
    icon: 'https://api.iconify.design/lucide:pen-line.svg?color=%23CF7249',
  },
  {
    type: 'Type-3', title: 'Structural Clones',
    desc: 'Near-miss clones — statements added, removed, or modified beyond simple renaming.',
    accent: '#2D6A6A', bg: '#EBF4F4', num: '03',
    icon: 'https://api.iconify.design/lucide:git-branch.svg?color=%232D6A6A',
  },
  {
    type: 'Type-4', title: 'Semantic / I/O',
    desc: 'Same algorithm implemented differently — caught via I/O behavioral testing + PDG analysis.',
    accent: '#8B9BB4', bg: '#EFF2F7', num: '04',
    icon: 'https://api.iconify.design/lucide:brain-circuit.svg?color=%238B9BB4',
  },
  {
    type: 'Languages', title: '5 Languages',
    desc: 'C/C++, Java, Python, JavaScript, TypeScript — each with language-specific AST parsing.',
    accent: '#1A1714', bg: '#F7F3EE', num: '05',
    icon: 'https://api.iconify.design/lucide:globe-2.svg?color=%231A1714',
  },
  {
    type: 'Reports', title: 'Detailed Reports',
    desc: 'Side-by-side diffs, fragment highlights, confidence scores, and CSV export.',
    accent: '#2D6A6A', bg: '#EBF4F4', num: '06',
    icon: 'https://api.iconify.design/lucide:bar-chart-3.svg?color=%232D6A6A',
  },
];

const Features = () => (
  <section id="features" className="bg-white py-28">
    <div className="max-w-6xl mx-auto px-6">
      <div className="text-center mb-16">
        <span className="inline-block text-xs font-bold tracking-[0.2em] uppercase text-[#CF7249] px-4 py-1.5 rounded-full bg-[#FEF3EC] border border-[#FCDDC5] mb-4">
          Detection Engine
        </span>
        <h2 className="text-4xl font-bold text-[#1A1714] mb-4">Four Clone Types. One Tool.</h2>
        <p className="text-[#6B6560] max-w-xl mx-auto leading-relaxed">
          Based on the Bellon et al. research taxonomy — the same classification used by NiCad, MOSS, and JPlag.
        </p>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
        {FEATURES.map(({ type, title, desc, accent, bg, num, icon }) => (
          <div
            key={type}
            className="group rounded-3xl border border-[#E8E1D8] p-6 hover:shadow-lg hover:border-transparent transition-all duration-200 cursor-default"
            style={{ background: bg }}
          >
            <div className="flex items-center justify-between mb-5">
              <div
                className="w-11 h-11 rounded-2xl flex items-center justify-center bg-white shadow-sm"
              >
                <img src={icon} alt="" width="20" height="20" />
              </div>
              <span className="text-[10px] font-black tracking-widest text-[#A8A29E]">{num}</span>
            </div>
            <span
              className="inline-block text-[10px] font-black uppercase tracking-[0.15em] px-2.5 py-1 rounded-full mb-3"
              style={{ background: 'white', color: accent }}
            >
              {type}
            </span>
            <h3 className="text-base font-bold text-[#1A1714] mb-2">{title}</h3>
            <p className="text-sm text-[#6B6560] leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default Features;
