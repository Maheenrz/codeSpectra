import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import courseService from '../../services/courseService';
import assignmentService from '../../services/assignmentService';

// ─── Step indicator ───────────────────────────────────────────────────────────
const STEPS = ['Basics', 'Questions', 'Detection', 'Review'];

const StepBar = ({ current }) => (
  <div className="flex items-center gap-0 mb-10">
    {STEPS.map((label, i) => {
      const done    = i < current;
      const active  = i === current;
      return (
        <React.Fragment key={label}>
          <div className="flex flex-col items-center gap-1.5 min-w-[56px]">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-300
              ${done   ? 'bg-emerald-500 text-white shadow-lg shadow-emerald-200'
              : active ? 'bg-slate-900 text-white ring-2 ring-slate-900 ring-offset-2'
                       : 'bg-gray-100 text-gray-400'}`}>
              {done ? '✓' : i + 1}
            </div>
            <span className={`text-[10px] font-semibold uppercase tracking-widest
              ${active ? 'text-slate-900' : done ? 'text-emerald-600' : 'text-gray-400'}`}>
              {label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`flex-1 h-0.5 mb-5 transition-all duration-500
              ${i < current ? 'bg-emerald-400' : 'bg-gray-200'}`} />
          )}
        </React.Fragment>
      );
    })}
  </div>
);

// ─── Field wrappers ───────────────────────────────────────────────────────────
const Field = ({ label, hint, required, children }) => (
  <div>
    <label className="block text-xs font-bold uppercase tracking-widest text-gray-500 mb-2">
      {label}{required && <span className="text-red-400 ml-1">*</span>}
    </label>
    {children}
    {hint && <p className="text-xs text-gray-400 mt-1.5">{hint}</p>}
  </div>
);

const inputCls = "w-full px-4 py-3 border border-gray-200 rounded-xl bg-white text-sm text-gray-900 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all";
const selectCls = "w-full px-4 py-3 border border-gray-200 rounded-xl bg-white text-sm text-gray-900 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all appearance-none cursor-pointer";

// ─── Toggle switch ─────────────────────────────────────────────────────────────
const Toggle = ({ checked, onChange, label, sub }) => (
  <label className="flex items-start gap-4 cursor-pointer group">
    <div className={`relative mt-0.5 w-11 h-6 rounded-full transition-colors duration-200 flex-shrink-0
      ${checked ? 'bg-slate-900' : 'bg-gray-200'}`}
      onClick={onChange}>
      <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white shadow transition-transform duration-200
        ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
    </div>
    <div>
      <p className="text-sm font-semibold text-gray-900 group-hover:text-slate-700">{label}</p>
      {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
    </div>
  </label>
);

// ─── Section card ─────────────────────────────────────────────────────────────
const Section = ({ icon, title, subtitle, children }) => (
  <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
    <div className="px-8 py-5 border-b border-gray-100 bg-gray-50/60 flex items-center gap-3">
      <span className="text-2xl">{icon}</span>
      <div>
        <h2 className="font-bold text-gray-900 text-base">{title}</h2>
        {subtitle && <p className="text-xs text-gray-500 mt-0.5">{subtitle}</p>}
      </div>
    </div>
    <div className="px-8 py-6 space-y-6">{children}</div>
  </div>
);

// ─── Assignment type chip ─────────────────────────────────────────────────────
const TypeChip = ({ value, selected, onClick, icon, label, desc }) => (
  <button type="button" onClick={() => onClick(value)}
    className={`flex-1 px-5 py-4 rounded-xl border-2 text-left transition-all duration-150
      ${selected
        ? 'border-slate-900 bg-slate-900 text-white shadow-lg'
        : 'border-gray-200 bg-white text-gray-700 hover:border-gray-400'}`}>
    <div className="flex items-center gap-2 mb-1">
      <span className="text-xl">{icon}</span>
      <span className="font-bold text-sm">{label}</span>
    </div>
    <p className={`text-xs leading-relaxed ${selected ? 'text-slate-300' : 'text-gray-500'}`}>{desc}</p>
  </button>
);

// ─── Submission mode chip ─────────────────────────────────────────────────────
const SubChip = ({ value, selected, onClick, icon, label }) => (
  <button type="button" onClick={() => onClick(value)}
    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg border text-xs font-semibold transition-all
      ${selected ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-gray-200 bg-white text-gray-600 hover:border-gray-400'}`}>
    <span>{icon}</span>{label}
  </button>
);

// ─── Clone type badge ─────────────────────────────────────────────────────────
const CloneBadge = ({ type, enabled, onToggle, label, desc, color }) => {
  const colors = {
    blue:   { on: 'bg-blue-600 border-blue-600', off: 'border-gray-200', dot: 'bg-blue-500' },
    violet: { on: 'bg-violet-600 border-violet-600', off: 'border-gray-200', dot: 'bg-violet-500' },
    amber:  { on: 'bg-amber-500 border-amber-500', off: 'border-gray-200', dot: 'bg-amber-500' },
    rose:   { on: 'bg-rose-600 border-rose-600', off: 'border-gray-200', dot: 'bg-rose-500' },
  };
  const c = colors[color];
  return (
    <div className={`relative p-5 rounded-xl border-2 transition-all duration-200 cursor-pointer
      ${enabled ? c.on + ' text-white shadow-md' : c.off + ' bg-white text-gray-700'}`}
      onClick={onToggle}>
      <div className="flex justify-between items-start mb-2">
        <span className={`text-xs font-black uppercase tracking-widest ${enabled ? 'text-white/70' : 'text-gray-400'}`}>
          Type-{type}
        </span>
        <div className={`w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0
          ${enabled ? 'border-white bg-white' : 'border-gray-300'}`}>
          {enabled && <div className={`w-2.5 h-2.5 rounded-full ${c.dot}`} />}
        </div>
      </div>
      <p className={`text-sm font-bold ${enabled ? 'text-white' : 'text-gray-900'}`}>{label}</p>
      <p className={`text-xs mt-1 leading-relaxed ${enabled ? 'text-white/70' : 'text-gray-500'}`}>{desc}</p>
    </div>
  );
};

// ─── Main Component ───────────────────────────────────────────────────────────
const CreateAssignment = () => {
  const navigate       = useNavigate();
  const [searchParams] = useSearchParams();
  const preCoId        = searchParams.get('courseId');
  const [step, setStep] = useState(0);

  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const [formData, setFormData] = useState({
    courseId:                preCoId || '',
    title:                   '',
    description:             '',
    dueDate:                 '',
    assignmentType:          'standard',        // 'standard' | 'webdev'
    primaryLanguage:         'cpp',
    allowedExtensions:       '.cpp,.c,.h',
    submissionMode:          'files',           // 'files' | 'zip' | 'both'
    maxFileSizeMb:           10,
    enableType1:             true,
    enableType2:             true,
    enableType3:             true,
    enableType4:             false,
    highSimilarityThreshold:   85,
    mediumSimilarityThreshold: 70,
    analysisMode:            'after_deadline',
    showResultsToStudents:   false,
    generateFeedback:        true,
  });

  const [questions, setQuestions] = useState([{
    title: '', description: '', expectedFiles: '',
    allowedExtensions: '', maxMarks: 10, submissionMode: 'inherit',
  }]);

  const totalMarks = questions.reduce((s, q) => s + (parseInt(q.maxMarks) || 0), 0);

  useEffect(() => { courseService.getInstructorCourses().then(setCourses).catch(() => {}); }, []);

  useEffect(() => {
    const ext = assignmentService.getExtensionsForLanguage(formData.primaryLanguage).join(',');
    setFormData(p => ({ ...p, allowedExtensions: ext }));
  }, [formData.primaryLanguage]);

  // ── Handlers ────────────────────────────────────────────────────────────────
  const set = (name, val) => setFormData(p => ({ ...p, [name]: val }));

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    set(name, type === 'checkbox' ? checked : value);
  };

  const qChange = (i, field, val) => {
    const u = [...questions]; u[i] = { ...u[i], [field]: val }; setQuestions(u);
  };
  const addQ    = () => setQuestions(p => [...p, { title: '', description: '', expectedFiles: '', allowedExtensions: '', maxMarks: 10, submissionMode: 'inherit' }]);
  const removeQ = (i) => { if (questions.length > 1) setQuestions(p => p.filter((_, x) => x !== i)); };
  const dupQ    = (i) => { const u = [...questions]; u.splice(i+1, 0, { ...u[i], title: u[i].title + ' (Copy)' }); setQuestions(u); };
  const moveQ   = (i, dir) => {
    if ((dir === 'up' && i === 0) || (dir === 'down' && i === questions.length - 1)) return;
    const u = [...questions]; const j = dir === 'up' ? i-1 : i+1;
    [u[i], u[j]] = [u[j], u[i]]; setQuestions(u);
  };

  // ── Validation ───────────────────────────────────────────────────────────────
  const validate = () => {
    if (step === 0) {
      if (!formData.courseId)           return 'Please select a course.';
      if (!formData.title.trim())       return 'Assignment title is required.';
      if (!formData.description.trim()) return 'Description is required.';
      if (!formData.dueDate)            return 'Due date is required.';
    }
    if (step === 1) {
      for (let i = 0; i < questions.length; i++) {
        if (!questions[i].title.trim())       return `Q${i+1}: Title is required.`;
        if (!questions[i].description.trim()) return `Q${i+1}: Description is required.`;
        if (!(parseInt(questions[i].maxMarks) > 0)) return `Q${i+1}: Marks must be > 0.`;
      }
    }
    return null;
  };

  const nextStep = () => {
    const err = validate(); if (err) { setError(err); return; }
    setError(''); setStep(s => s + 1);
  };
  const prevStep = () => { setError(''); setStep(s => s - 1); };

  const handleSubmit = async () => {
    setLoading(true); setError('');
    try {
      const result = await assignmentService.createAssignment({
        ...formData,
        questions: questions.map(q => ({
          title: q.title, description: q.description,
          expectedFiles: q.expectedFiles ? q.expectedFiles.split(',').map(f => f.trim()) : [],
          allowedExtensions: q.allowedExtensions ? q.allowedExtensions.split(',').map(e => e.trim()) : [],
          maxMarks: parseInt(q.maxMarks) || 0,
          submissionMode: q.submissionMode === 'inherit' ? formData.submissionMode : q.submissionMode,
        })),
      });
      navigate(`/assignments/${result.assignment.assignment_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create assignment.'); setLoading(false);
    }
  };

  const langs = [
    { value: 'cpp',        label: 'C / C++',       ext: '.cpp,.c,.h,.hpp' },
    { value: 'java',       label: 'Java',           ext: '.java' },
    { value: 'python',     label: 'Python',         ext: '.py' },
    { value: 'javascript', label: 'JavaScript / TS', ext: '.js,.jsx,.ts,.tsx' },
    { value: 'mixed',      label: 'Mixed',          ext: '.cpp,.c,.h,.java,.py,.js' },
  ];

  // ── Render steps ─────────────────────────────────────────────────────────────

  const renderStep0 = () => (
    <div className="space-y-6">
      <Section icon="📋" title="Assignment Basics" subtitle="Core details visible to all students">
        <Field label="Course" required>
          <div className="relative">
            <select name="courseId" value={formData.courseId} onChange={handleChange} className={selectCls}>
              <option value="">Select a course…</option>
              {courses.map(c => <option key={c.course_id} value={c.course_id}>{c.course_code} — {c.course_name}</option>)}
            </select>
            <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 text-xs">▼</div>
          </div>
        </Field>

        <Field label="Title" required>
          <input className={inputCls} name="title" value={formData.title} onChange={handleChange}
            placeholder="e.g., Assignment 02: Trees & Graphs" />
        </Field>

        <Field label="Description" required>
          <textarea className={inputCls + ' resize-none'} name="description" value={formData.description}
            onChange={handleChange} rows={3} placeholder="Overall assignment objectives and instructions…" />
        </Field>

        <Field label="Due Date & Time" required>
          <input className={inputCls} type="datetime-local" name="dueDate" value={formData.dueDate} onChange={handleChange} />
        </Field>
      </Section>

      <Section icon="🎯" title="Assignment Type" subtitle="Defines how students submit their work">
        <div className="flex gap-3">
          <TypeChip value="standard" selected={formData.assignmentType === 'standard'} onClick={v => set('assignmentType', v)}
            icon="📝" label="Standard Assignment"
            desc="DSA, OOP, PF — students submit individual code files or a ZIP of their solution." />
          <TypeChip value="webdev" selected={formData.assignmentType === 'webdev'} onClick={v => set('assignmentType', v)}
            icon="🌐" label="Web Dev Project"
            desc="Full-stack project — students submit a ZIP of their entire project (frontend + backend folders)." />
        </div>

        {formData.assignmentType === 'webdev' && (
          <div className="mt-2 p-4 rounded-xl bg-slate-50 border border-slate-200 text-sm text-slate-700 leading-relaxed">
            <span className="font-bold">ℹ️ Web Dev mode:</span> The detector will analyze all source files across all folders in the ZIP.
            Same-language files are compared cross-folder (e.g. <code className="bg-slate-200 px-1 rounded text-xs">frontend/utils.js</code> vs <code className="bg-slate-200 px-1 rounded text-xs">backend/helpers.js</code>).
          </div>
        )}
      </Section>

      {formData.assignmentType === 'standard' && (
        <Section icon="📤" title="Submission Format" subtitle="How students are allowed to submit their files">
          <div className="flex flex-wrap gap-3">
            <SubChip value="files" selected={formData.submissionMode === 'files'} onClick={v => set('submissionMode', v)} icon="📄" label="Individual Files Only" />
            <SubChip value="zip"   selected={formData.submissionMode === 'zip'}   onClick={v => set('submissionMode', v)} icon="📦" label="ZIP Only" />
            <SubChip value="both"  selected={formData.submissionMode === 'both'}  onClick={v => set('submissionMode', v)} icon="🔀" label="Files or ZIP (Both Allowed)" />
          </div>
          <p className="text-xs text-gray-500">
            {formData.submissionMode === 'files' && 'Students upload individual source files (.cpp, .java, etc.)'}
            {formData.submissionMode === 'zip'   && 'Students must upload a single .zip file.'}
            {formData.submissionMode === 'both'  && 'Students can upload individual files or a .zip — their choice.'}
          </p>
        </Section>
      )}
    </div>
  );

  const renderStep1 = () => (
    <div className="space-y-5">
      <Section icon="⚙️" title="File Settings" subtitle="Default file constraints applied to all questions">
        <div className="grid md:grid-cols-3 gap-5">
          <Field label="Primary Language" required>
            <div className="relative">
              <select name="primaryLanguage" value={formData.primaryLanguage} onChange={handleChange} className={selectCls}>
                {langs.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
              <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 text-xs">▼</div>
            </div>
          </Field>
          <Field label="Allowed Extensions" hint="Comma-separated">
            <input className={inputCls} name="allowedExtensions" value={formData.allowedExtensions} onChange={handleChange} placeholder=".cpp,.c,.h" />
          </Field>
          <Field label="Max File Size (MB)">
            <input className={inputCls} type="number" name="maxFileSizeMb" min="1" max="200" value={formData.maxFileSizeMb} onChange={handleChange} />
          </Field>
        </div>
      </Section>

      {/* Total marks banner */}
      <div className="flex items-center justify-between px-6 py-4 bg-slate-900 rounded-xl text-white">
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-widest font-bold">Total Marks</p>
          <p className="text-xs text-slate-500 mt-0.5">Auto-calculated from questions</p>
        </div>
        <span className="text-4xl font-black tracking-tight">{totalMarks}</span>
      </div>

      {/* Questions */}
      <div className="space-y-4">
        {questions.map((q, i) => (
          <div key={i} className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
            {/* Question header */}
            <div className="px-6 py-4 bg-gray-50/60 border-b border-gray-100 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="w-8 h-8 rounded-lg bg-slate-900 text-white flex items-center justify-center text-xs font-black">Q{i+1}</span>
                <p className="font-semibold text-gray-800 text-sm truncate max-w-xs">{q.title || <span className="text-gray-400 font-normal">Untitled Question</span>}</p>
              </div>
              <div className="flex items-center gap-1.5">
                <button type="button" onClick={() => moveQ(i, 'up')}  disabled={i===0}                    className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-200 disabled:opacity-20 text-xs">↑</button>
                <button type="button" onClick={() => moveQ(i, 'down')} disabled={i===questions.length-1} className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-200 disabled:opacity-20 text-xs">↓</button>
                <button type="button" onClick={() => dupQ(i)}    className="px-2.5 py-1.5 rounded-lg text-xs text-blue-600 hover:bg-blue-50 font-semibold">Duplicate</button>
                {questions.length > 1 &&
                  <button type="button" onClick={() => removeQ(i)} className="px-2.5 py-1.5 rounded-lg text-xs text-red-500 hover:bg-red-50 font-semibold">Remove</button>}
              </div>
            </div>

            {/* Question body */}
            <div className="px-6 py-5 space-y-4">
              <div className="grid md:grid-cols-3 gap-4">
                <div className="md:col-span-2">
                  <Field label="Question Title" required>
                    <input className={inputCls} value={q.title} onChange={e => qChange(i, 'title', e.target.value)} placeholder="e.g., Implement Binary Search Tree" />
                  </Field>
                </div>
                <Field label="Max Marks" required>
                  <input className={inputCls} type="number" min="0" value={q.maxMarks} onChange={e => qChange(i, 'maxMarks', e.target.value)} />
                </Field>
              </div>

              <Field label="Problem Description" required>
                <textarea className={inputCls + ' resize-none'} rows={3} value={q.description}
                  onChange={e => qChange(i, 'description', e.target.value)}
                  placeholder="Describe the problem, constraints, expected behavior…" />
              </Field>

              <div className="grid md:grid-cols-2 gap-4">
                <Field label="Expected Files" hint="Comma-separated — guideline for students">
                  <input className={inputCls} value={q.expectedFiles} onChange={e => qChange(i, 'expectedFiles', e.target.value)} placeholder="BinaryTree.cpp, BinaryTree.h" />
                </Field>
                <Field label="Override Extensions" hint={`Leave empty to use: ${formData.allowedExtensions}`}>
                  <input className={inputCls} value={q.allowedExtensions} onChange={e => qChange(i, 'allowedExtensions', e.target.value)} placeholder="Optional override…" />
                </Field>
              </div>

              {/* Per-question submission mode (standard only) */}
              {formData.assignmentType === 'standard' && (
                <Field label="Submission Mode for This Question" hint="Override the assignment-level setting for this question">
                  <div className="flex flex-wrap gap-2">
                    {[
                      { value: 'inherit', icon: '↩', label: `Inherit (${formData.submissionMode})` },
                      { value: 'files',   icon: '📄', label: 'Files Only' },
                      { value: 'zip',     icon: '📦', label: 'ZIP Only' },
                      { value: 'both',    icon: '🔀', label: 'Both' },
                    ].map(opt => (
                      <SubChip key={opt.value} value={opt.value} selected={q.submissionMode === opt.value}
                        onClick={v => qChange(i, 'submissionMode', v)} icon={opt.icon} label={opt.label} />
                    ))}
                  </div>
                </Field>
              )}
            </div>
          </div>
        ))}

        <button type="button" onClick={addQ}
          className="w-full py-4 rounded-2xl border-2 border-dashed border-gray-200 text-sm text-gray-500 hover:border-slate-400 hover:text-slate-700 hover:bg-gray-50 font-semibold transition-all">
          + Add Question
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <Section icon="🔍" title="Detection Types" subtitle="Choose which clone types to run during analysis">
        <div className="grid grid-cols-2 gap-4">
          <CloneBadge type={1} enabled={formData.enableType1} onToggle={() => set('enableType1', !formData.enableType1)}
            label="Exact Copies" desc="Whitespace & comment variations only" color="blue" />
          <CloneBadge type={2} enabled={formData.enableType2} onToggle={() => set('enableType2', !formData.enableType2)}
            label="Renamed Variables" desc="Identifier & literal renaming" color="violet" />
          <CloneBadge type={3} enabled={formData.enableType3} onToggle={() => set('enableType3', !formData.enableType3)}
            label="Near-Miss Clones" desc="Modified statements, logic changes" color="amber" />
          <CloneBadge type={4} enabled={formData.enableType4} onToggle={() => set('enableType4', !formData.enableType4)}
            label="Semantic / AI" desc="Different code, same algorithm" color="rose" />
        </div>
      </Section>

      <Section icon="📊" title="Similarity Thresholds" subtitle="Control sensitivity of flagging">
        <div className="grid md:grid-cols-2 gap-6">
          <Field label="High Similarity Threshold (%)" hint="Flagged as likely plagiarism">
            <div className="space-y-2">
              <input type="range" min="50" max="100" value={formData.highSimilarityThreshold}
                onChange={e => set('highSimilarityThreshold', e.target.value)}
                className="w-full accent-slate-900" />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">50%</span>
                <span className="text-2xl font-black text-slate-900">{formData.highSimilarityThreshold}%</span>
                <span className="text-xs text-gray-500">100%</span>
              </div>
            </div>
          </Field>
          <Field label="Medium Similarity Threshold (%)" hint="Flagged as suspicious, review needed">
            <div className="space-y-2">
              <input type="range" min="30" max="100" value={formData.mediumSimilarityThreshold}
                onChange={e => set('mediumSimilarityThreshold', e.target.value)}
                className="w-full accent-slate-900" />
              <div className="flex justify-between items-center">
                <span className="text-xs text-gray-500">30%</span>
                <span className="text-2xl font-black text-slate-900">{formData.mediumSimilarityThreshold}%</span>
                <span className="text-xs text-gray-500">100%</span>
              </div>
            </div>
          </Field>
        </div>
      </Section>

      <Section icon="⚙️" title="Analysis Options">
        <Field label="When to Run Analysis">
          <div className="relative">
            <select name="analysisMode" value={formData.analysisMode} onChange={handleChange} className={selectCls}>
              <option value="immediate">Immediate — analyze on each submission</option>
              <option value="after_deadline">After Deadline — batch run once deadline passes</option>
              <option value="manual">Manual — instructor triggers analysis</option>
            </select>
            <div className="pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-gray-400 text-xs">▼</div>
          </div>
        </Field>
        <div className="space-y-4">
          <Toggle checked={formData.showResultsToStudents} onChange={() => set('showResultsToStudents', !formData.showResultsToStudents)}
            label="Show results to students" sub="Students can see their similarity scores after analysis." />
          <Toggle checked={formData.generateFeedback} onChange={() => set('generateFeedback', !formData.generateFeedback)}
            label="Generate feedback reports" sub="Produce detailed per-student reports highlighting flagged regions." />
        </div>
      </Section>
    </div>
  );

  const renderStep3 = () => {
    const langLabel = langs.find(l => l.value === formData.primaryLanguage)?.label || formData.primaryLanguage;
    const enabledTypes = [
      formData.enableType1 && 'Type-1', formData.enableType2 && 'Type-2',
      formData.enableType3 && 'Type-3', formData.enableType4 && 'Type-4',
    ].filter(Boolean);

    return (
      <div className="space-y-5">
        <div className="bg-emerald-50 border border-emerald-200 rounded-2xl px-6 py-5">
          <p className="text-emerald-800 font-bold text-sm mb-1">✅ All set! Review your assignment before creating.</p>
          <p className="text-emerald-700 text-xs">Once created, students in the course will be able to see and submit this assignment.</p>
        </div>

        {/* Summary grid */}
        <div className="grid md:grid-cols-2 gap-4">
          {[
            { label: 'Course',           value: courses.find(c => c.course_id == formData.courseId)?.course_name || '—' },
            { label: 'Due Date',         value: formData.dueDate ? new Date(formData.dueDate).toLocaleString() : '—' },
            { label: 'Assignment Type',  value: formData.assignmentType === 'webdev' ? '🌐 Web Dev Project' : '📝 Standard' },
            { label: 'Submission Mode',  value: formData.assignmentType === 'webdev' ? 'ZIP (Project)' : formData.submissionMode },
            { label: 'Language',         value: langLabel },
            { label: 'Extensions',       value: formData.allowedExtensions },
            { label: 'Total Marks',      value: totalMarks },
            { label: 'Questions',        value: questions.length },
            { label: 'Detection Types',  value: enabledTypes.join(', ') || 'None' },
            { label: 'Analysis Mode',    value: formData.analysisMode.replace('_', ' ') },
          ].map(({ label, value }) => (
            <div key={label} className="bg-white border border-gray-100 rounded-xl px-5 py-4">
              <p className="text-[10px] font-bold uppercase tracking-widest text-gray-400 mb-1">{label}</p>
              <p className="text-sm font-semibold text-gray-900 break-words">{String(value)}</p>
            </div>
          ))}
        </div>

        {/* Questions summary */}
        <Section icon="❓" title="Questions Summary">
          <div className="space-y-3">
            {questions.map((q, i) => (
              <div key={i} className="flex items-center justify-between py-3 border-b border-gray-100 last:border-0">
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center text-xs font-black">{i+1}</span>
                  <div>
                    <p className="text-sm font-semibold text-gray-900">{q.title}</p>
                    <p className="text-xs text-gray-500 mt-0.5">{q.description.slice(0, 60)}{q.description.length > 60 ? '…' : ''}</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-slate-900 flex-shrink-0">{q.maxMarks} pts</span>
              </div>
            ))}
          </div>
        </Section>
      </div>
    );
  };

  const steps = [renderStep0, renderStep1, renderStep2, renderStep3];

  // ── Layout ───────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen" style={{ background: '#f8f8f7', fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700;800;900&display=swap');
        * { font-family: 'DM Sans', system-ui, sans-serif; }
        input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: #0f172a; cursor: pointer; }
        input[type=range]::-webkit-slider-runnable-track { height: 4px; border-radius: 2px; background: #e2e8f0; }
        input[type=range]::-moz-range-progress { background: #0f172a; height: 4px; border-radius: 2px; }
      `}</style>

      {/* Top bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-3xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/dashboard" className="flex items-center gap-2 text-xs font-semibold text-gray-500 hover:text-gray-800 transition-colors">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" /></svg>
            Dashboard
          </Link>
          <div className="text-center">
            <p className="text-xs font-black uppercase tracking-widest text-gray-400">Create Assignment</p>
          </div>
          <div className="w-16" />
        </div>
      </div>

      {/* Content */}
      <div className="max-w-3xl mx-auto px-6 py-10">
        {/* Hero */}
        {step === 0 && (
          <div className="mb-8">
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">New Assignment</h1>
            <p className="text-gray-500 mt-1.5">Set up your assignment in a few steps. Students will be notified once it's published.</p>
          </div>
        )}

        <StepBar current={step} />

        {/* Error */}
        {error && (
          <div className="mb-6 px-5 py-4 bg-red-50 border border-red-200 rounded-xl text-sm text-red-700 font-medium">
            ⚠️ {error}
          </div>
        )}

        {/* Step content */}
        {steps[step]()}

        {/* Navigation */}
        <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
          <button type="button" onClick={prevStep} disabled={step === 0}
            className="px-5 py-3 rounded-xl text-sm font-semibold text-gray-600 hover:text-gray-900 hover:bg-gray-100 disabled:opacity-0 transition-all">
            ← Back
          </button>

          <div className="flex gap-2">
            {step < STEPS.length - 1 ? (
              <button type="button" onClick={nextStep}
                className="px-7 py-3 rounded-xl text-sm font-bold bg-slate-900 text-white hover:bg-slate-700 shadow-lg shadow-slate-200 transition-all">
                Continue →
              </button>
            ) : (
              <button type="button" onClick={handleSubmit} disabled={loading}
                className="px-7 py-3 rounded-xl text-sm font-bold bg-emerald-600 text-white hover:bg-emerald-500 shadow-lg shadow-emerald-200 disabled:opacity-50 transition-all">
                {loading ? 'Creating…' : '🚀 Create Assignment'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CreateAssignment;
