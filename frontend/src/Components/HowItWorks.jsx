import React from 'react';

const STEPS = [
  {
    n: '01', title: 'Create an Assignment',
    desc: 'Set title, due date, language, and which detection types to enable. Add per-question breakdowns if needed.',
    accent: '#CF7249', bg: '#FEF3EC', border: '#FCDDC5',
    icon: 'https://api.iconify.design/lucide:folder-plus.svg?color=%23CF7249',
  },
  {
    n: '02', title: 'Students Submit Code',
    desc: 'Students upload individual files or ZIP archives. Files are stored and grouped by language automatically.',
    accent: '#2D6A6A', bg: '#EBF4F4', border: '#B8D9D9',
    icon: 'https://api.iconify.design/lucide:upload-cloud.svg?color=%232D6A6A',
  },
  {
    n: '03', title: 'Engine Runs Analysis',
    desc: 'Every pair is compared across all 4 detection types simultaneously — Type-1 through Type-4.',
    accent: '#C4827A', bg: '#FAEDEC', border: '#F0C4C0',
    icon: 'https://api.iconify.design/lucide:cpu.svg?color=%23C4827A',
  },
  {
    n: '04', title: 'Review the Report',
    desc: 'See ranked similarity pairs, confidence scores, flagged fragments, and side-by-side code diff.',
    accent: '#8B9BB4', bg: '#EFF2F7', border: '#C8D2E0',
    icon: 'https://api.iconify.design/lucide:file-search.svg?color=%238B9BB4',
  },
];

const HowItWorks = () => (
  <section id="how-it-works" className="bg-[#F7F3EE] py-28">
    <div className="max-w-6xl mx-auto px-6">
      <div className="text-center mb-16">
        <span className="inline-block text-xs font-bold tracking-[0.2em] uppercase text-[#CF7249] px-4 py-1.5 rounded-full bg-[#FEF3EC] border border-[#FCDDC5] mb-4">
          Workflow
        </span>
        <h2 className="text-4xl font-bold text-[#1A1714] mb-4">Four steps to a full report.</h2>
        <p className="text-[#6B6560] max-w-md mx-auto">From assignment creation to plagiarism report in minutes.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        {STEPS.map(({ n, title, desc, accent, bg, border, icon }) => (
          <div
            key={n}
            className="rounded-3xl p-7 border transition-all hover:shadow-md"
            style={{ background: bg, borderColor: border }}
          >
            <div className="flex items-start gap-5">
              <div className="w-12 h-12 rounded-2xl bg-white flex items-center justify-center shadow-sm flex-shrink-0">
                <img src={icon} alt="" width="22" height="22" />
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] font-black tracking-widest" style={{ color: accent }}>{n}</span>
                  <h3 className="text-base font-bold text-[#1A1714]">{title}</h3>
                </div>
                <p className="text-sm text-[#6B6560] leading-relaxed">{desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  </section>
);

export default HowItWorks;
