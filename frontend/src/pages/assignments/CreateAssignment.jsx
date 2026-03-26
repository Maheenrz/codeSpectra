import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import courseService from '../../services/courseService';
import assignmentService from '../../services/assignmentService';

// ─── Design tokens ─────────────────────────────────────────────────────────
// bg:     #F7F3EE  card: white   border: #E8E1D8
// orange: #CF7249  teal: #2D6A6A  pink: #C4827A  slate: #8B9BB4

// ─── Step bar ─────────────────────────────────────────────────────────────
const STEPS = ['Basics', 'Questions', 'Detection', 'Review'];

const StepBar = ({ current }) => (
  <div className="flex items-center mb-10">
    {STEPS.map((label, i) => {
      const done   = i < current;
      const active = i === current;
      return (
        <React.Fragment key={label}>
          <div className="flex flex-col items-center gap-1.5 flex-shrink-0">
            <div className={`w-9 h-9 rounded-full flex items-center justify-center text-xs font-bold transition-all duration-200
              ${done   ? 'bg-[#CF7249] text-white'
              : active ? 'bg-[#1A1714] text-white ring-4 ring-[#1A1714]/10'
                       : 'bg-[#F0EBE3] text-[#A8A29E]'}`}>
              {done
                ? <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                : i + 1}
            </div>
            <span className={`text-[10px] font-semibold uppercase tracking-widest whitespace-nowrap
              ${active ? 'text-[#1A1714]' : done ? 'text-[#CF7249]' : 'text-[#A8A29E]'}`}>
              {label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`flex-1 h-px mx-2 mb-5 transition-all duration-300 ${i < current ? 'bg-[#CF7249]' : 'bg-[#E8E1D8]'}`} />
          )}
        </React.Fragment>
      );
    })}
  </div>
);

// ─── Shared input styles ───────────────────────────────────────────────────
const inputCls = "w-full px-4 py-3 border border-[#E8E1D8] rounded-2xl bg-white text-sm text-[#1A1714] placeholder-[#A8A29E] focus:outline-none focus:ring-2 focus:ring-[#CF7249]/30 focus:border-[#CF7249] transition-all";
const selectCls = inputCls + " appearance-none cursor-pointer";

const Field = ({ label, hint, required, children }) => (
  <div className="flex flex-col gap-1.5">
    <label className="text-xs font-bold uppercase tracking-widest text-[#6B6560]">
      {label}{required && <span className="text-[#C4827A] ml-1">*</span>}
    </label>
    {children}
    {hint && <p className="text-xs text-[#A8A29E]">{hint}</p>}
  </div>
);

// ─── Card wrapper ──────────────────────────────────────────────────────────
const Card = ({ title, subtitle, icon, children }) => (
  <div className="bg-white rounded-3xl border border-[#E8E1D8] overflow-hidden">
    {(title || icon) && (
      <div className="px-7 py-5 border-b border-[#F0EBE3] flex items-center gap-3">
        {icon && (
          <div className="w-9 h-9 rounded-2xl bg-[#FEF3EC] flex items-center justify-center flex-shrink-0">
            <img src={icon} alt="" width="18" height="18" />
          </div>
        )}
        <div>
          {title && <p className="text-sm font-bold text-[#1A1714]">{title}</p>}
          {subtitle && <p className="text-xs text-[#A8A29E] mt-0.5">{subtitle}</p>}
        </div>
      </div>
    )}
    <div className="px-7 py-6 space-y-5">{children}</div>
  </div>
);

// ─── Toggle switch ─────────────────────────────────────────────────────────
const Toggle = ({ checked, onChange, label, sub }) => (
  <div className="flex items-center justify-between gap-4 cursor-pointer" onClick={onChange}>
    <div>
      <p className="text-sm font-semibold text-[#1A1714]">{label}</p>
      {sub && <p className="text-xs text-[#A8A29E] mt-0.5">{sub}</p>}
    </div>
    <div className={`relative w-11 h-6 rounded-full transition-colors duration-200 flex-shrink-0 ${checked ? 'bg-[#CF7249]' : 'bg-[#E8E1D8]'}`}>
      <div className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white shadow-sm transition-transform duration-200 ${checked ? 'translate-x-5' : 'translate-x-0'}`} />
    </div>
  </div>
);

// ─── Detection type card ───────────────────────────────────────────────────
const DetectionCard = ({ num, label, desc, enabled, onToggle, accent, bg, border }) => (
  <div
    onClick={onToggle}
    className="relative rounded-2xl border-2 p-5 cursor-pointer transition-all duration-150 select-none"
    style={{
      background:   enabled ? bg    : 'white',
      borderColor:  enabled ? accent : '#E8E1D8',
    }}
  >
    <div className="flex items-start justify-between mb-2">
      <span
        className="text-[10px] font-black uppercase tracking-[0.15em]"
        style={{ color: enabled ? accent : '#A8A29E' }}
      >
        Type-{num}
      </span>
      <div
        className="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0"
        style={{ borderColor: enabled ? accent : '#E8E1D8', background: enabled ? accent : 'white' }}
      >
        {enabled && (
          <svg width="10" height="10" fill="none" stroke="white" strokeWidth="3" viewBox="0 0 24 24">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        )}
      </div>
    </div>
    <p className="text-sm font-bold text-[#1A1714] mb-1">{label}</p>
    <p className="text-xs text-[#6B6560] leading-relaxed">{desc}</p>
  </div>
);

// ─── Submission mode pill ──────────────────────────────────────────────────
const ModePill = ({ value, selected, onClick, label, desc }) => (
  <button
    type="button"
    onClick={() => onClick(value)}
    className={`flex-1 py-3 px-4 rounded-2xl border-2 text-left transition-all duration-150
      ${selected ? 'border-[#CF7249] bg-[#FEF3EC]' : 'border-[#E8E1D8] bg-white hover:border-[#D4C9BE]'}`}
  >
    <p className={`text-sm font-bold ${selected ? 'text-[#CF7249]' : 'text-[#1A1714]'}`}>{label}</p>
    <p className={`text-xs mt-0.5 ${selected ? 'text-[#CF7249]/70' : 'text-[#A8A29E]'}`}>{desc}</p>
  </button>
);

// ─── Question card ─────────────────────────────────────────────────────────
const QuestionCard = ({ q, i, total, onChange, onRemove, onDuplicate, onMove, submissionMode, allowedExtensions }) => (
  <div className="bg-white rounded-3xl border border-[#E8E1D8] overflow-hidden">
    <div className="px-6 py-4 bg-[#F7F3EE] border-b border-[#E8E1D8] flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-xl bg-[#CF7249] text-white flex items-center justify-center text-xs font-black">
          Q{i + 1}
        </div>
        <p className="text-sm font-semibold text-[#1A1714] truncate max-w-xs">
          {q.title || <span className="text-[#A8A29E] font-normal">Untitled question</span>}
        </p>
      </div>
      <div className="flex items-center gap-1">
        <button type="button" onClick={() => onMove(i, 'up')}   disabled={i === 0}           className="p-1.5 rounded-xl hover:bg-[#E8E1D8] disabled:opacity-20 text-[#6B6560] transition-colors">
          <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M18 15l-6-6-6 6"/></svg>
        </button>
        <button type="button" onClick={() => onMove(i, 'down')} disabled={i === total - 1}   className="p-1.5 rounded-xl hover:bg-[#E8E1D8] disabled:opacity-20 text-[#6B6560] transition-colors">
          <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <button type="button" onClick={() => onDuplicate(i)} className="px-2.5 py-1 rounded-xl text-xs font-semibold text-[#2D6A6A] hover:bg-[#EBF4F4] transition-colors">
          Copy
        </button>
        {total > 1 && (
          <button type="button" onClick={() => onRemove(i)} className="px-2.5 py-1 rounded-xl text-xs font-semibold text-[#C4827A] hover:bg-[#FAEDEC] transition-colors">
            Remove
          </button>
        )}
      </div>
    </div>
    <div className="px-6 py-5 space-y-4">
      <div className="grid md:grid-cols-3 gap-4">
        <div className="md:col-span-2">
          <Field label="Title" required>
            <input className={inputCls} value={q.title} onChange={e => onChange(i, 'title', e.target.value)} placeholder="e.g. Implement a Binary Search Tree" />
          </Field>
        </div>
        <Field label="Max Marks" required>
          <input className={inputCls} type="number" min="0" value={q.maxMarks} onChange={e => onChange(i, 'maxMarks', e.target.value)} />
        </Field>
      </div>
      <Field label="Problem Description" required>
        <textarea className={inputCls + ' resize-none'} rows={3} value={q.description} onChange={e => onChange(i, 'description', e.target.value)} placeholder="Describe the problem, expected behavior, constraints..." />
      </Field>
      <div className="grid md:grid-cols-2 gap-4">
        <Field label="Expected Files" hint="Guide for students — comma-separated">
          <input className={inputCls} value={q.expectedFiles} onChange={e => onChange(i, 'expectedFiles', e.target.value)} placeholder="BinaryTree.cpp, Node.h" />
        </Field>
        <Field label="Override Extensions" hint={`Leave empty to inherit: ${allowedExtensions}`}>
          <input className={inputCls} value={q.allowedExtensions} onChange={e => onChange(i, 'allowedExtensions', e.target.value)} placeholder="Optional" />
        </Field>
      </div>
    </div>
  </div>
);

// ─── Main ──────────────────────────────────────────────────────────────────
const CreateAssignment = () => {
  const navigate       = useNavigate();
  const [searchParams] = useSearchParams();
  const preCoId        = searchParams.get('courseId');
  const [step, setStep] = useState(0);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState('');

  const [form, setForm] = useState({
    courseId:                  preCoId || '',
    title:                     '',
    description:               '',
    dueDate:                   '',
    primaryLanguage:           'cpp',
    allowedExtensions:         '.cpp,.c,.h',
    submissionMode:            'files',
    maxFileSizeMb:             10,
    enableType1:               true,
    enableType2:               true,
    enableType3:               true,
    enableType4:               true,
    highSimilarityThreshold:   85,
    mediumSimilarityThreshold: 70,
    analysisMode:              'after_deadline',
    showResultsToStudents:     false,
    generateFeedback:          true,
  });

  const [questions, setQuestions] = useState([{
    title: '', description: '', expectedFiles: '', allowedExtensions: '', maxMarks: 10,
  }]);

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));

  useEffect(() => {
    courseService.getInstructorCourses().then(setCourses).catch(() => {});
  }, []);

  useEffect(() => {
    const ext = assignmentService.getExtensionsForLanguage(form.primaryLanguage).join(',');
    set('allowedExtensions', ext);
  }, [form.primaryLanguage]);

  const qChange    = (i, f, v) => { const u = [...questions]; u[i] = { ...u[i], [f]: v }; setQuestions(u); };
  const addQ       = () => setQuestions(p => [...p, { title: '', description: '', expectedFiles: '', allowedExtensions: '', maxMarks: 10 }]);
  const removeQ    = (i) => setQuestions(p => p.filter((_, x) => x !== i));
  const duplicateQ = (i) => { const u = [...questions]; u.splice(i + 1, 0, { ...u[i], title: u[i].title + ' (Copy)' }); setQuestions(u); };
  const moveQ      = (i, dir) => {
    if ((dir === 'up' && i === 0) || (dir === 'down' && i === questions.length - 1)) return;
    const u = [...questions]; const j = dir === 'up' ? i - 1 : i + 1;
    [u[i], u[j]] = [u[j], u[i]]; setQuestions(u);
  };

  const validate = () => {
    if (step === 0) {
      if (!form.courseId)           return 'Select a course.';
      if (!form.title.trim())       return 'Title is required.';
      if (!form.description.trim()) return 'Description is required.';
      if (!form.dueDate)            return 'Due date is required.';
    }
    if (step === 1) {
      for (let i = 0; i < questions.length; i++) {
        if (!questions[i].title.trim())       return `Q${i + 1}: Title is required.`;
        if (!questions[i].description.trim()) return `Q${i + 1}: Description is required.`;
        if (!(parseInt(questions[i].maxMarks) > 0)) return `Q${i + 1}: Marks must be greater than 0.`;
      }
    }
    return null;
  };

  const nextStep = () => { const e = validate(); if (e) { setError(e); return; } setError(''); setStep(s => s + 1); };
  const prevStep = () => { setError(''); setStep(s => s - 1); };

  const handleSubmit = async () => {
    setLoading(true); setError('');
    try {
      const result = await assignmentService.createAssignment({
        ...form,
        questions: questions.map(q => ({
          title:             q.title,
          description:       q.description,
          expectedFiles:     q.expectedFiles ? q.expectedFiles.split(',').map(f => f.trim()) : [],
          allowedExtensions: q.allowedExtensions ? q.allowedExtensions.split(',').map(e => e.trim()) : [],
          maxMarks:          parseInt(q.maxMarks) || 0,
          submissionMode:    form.submissionMode,
        })),
      });
      navigate(`/assignments/${result.assignment.assignment_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create assignment.');
      setLoading(false);
    }
  };

  const totalMarks = questions.reduce((s, q) => s + (parseInt(q.maxMarks) || 0), 0);
  const langs = [
    { value: 'cpp',        label: 'C / C++',          ext: '.cpp,.c,.h,.hpp' },
    { value: 'java',       label: 'Java',              ext: '.java' },
    { value: 'python',     label: 'Python',            ext: '.py' },
    { value: 'javascript', label: 'JavaScript / TS',   ext: '.js,.jsx,.ts,.tsx' },
    { value: 'mixed',      label: 'Mixed languages',   ext: '.cpp,.c,.h,.java,.py,.js' },
  ];

  // ── Step 0: Basics ─────────────────────────────────────────────────────
  const renderStep0 = () => (
    <div className="space-y-5">
      <Card
        title="Assignment Details"
        icon="https://api.iconify.design/lucide:file-text.svg?color=%23CF7249"
        subtitle="Core information visible to all students"
      >
        <div className="grid md:grid-cols-2 gap-5">
          <div className="md:col-span-2">
            <Field label="Course" required>
              <div className="relative">
                <select value={form.courseId} onChange={e => set('courseId', e.target.value)} className={selectCls}>
                  <option value="">Select a course...</option>
                  {courses.map(c => <option key={c.course_id} value={c.course_id}>{c.course_code} — {c.course_name}</option>)}
                </select>
                <svg className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
              </div>
            </Field>
          </div>
          <div className="md:col-span-2">
            <Field label="Title" required>
              <input className={inputCls} value={form.title} onChange={e => set('title', e.target.value)} placeholder="e.g. Assignment 03: Trees and Graphs" />
            </Field>
          </div>
          <div className="md:col-span-2">
            <Field label="Description" required>
              <textarea className={inputCls + ' resize-none'} rows={3} value={form.description} onChange={e => set('description', e.target.value)} placeholder="Objectives, constraints, and grading criteria..." />
            </Field>
          </div>
          <Field label="Due Date & Time" required>
            <input className={inputCls} type="datetime-local" value={form.dueDate} onChange={e => set('dueDate', e.target.value)} />
          </Field>
          <Field label="Primary Language" required>
            <div className="relative">
              <select value={form.primaryLanguage} onChange={e => set('primaryLanguage', e.target.value)} className={selectCls}>
                {langs.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
              <svg className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
            </div>
          </Field>
          <Field label="Allowed File Extensions" hint="Comma-separated">
            <input className={inputCls} value={form.allowedExtensions} onChange={e => set('allowedExtensions', e.target.value)} placeholder=".cpp,.c,.h" />
          </Field>
          <Field label="Max File Size (MB)">
            <input className={inputCls} type="number" min="1" max="200" value={form.maxFileSizeMb} onChange={e => set('maxFileSizeMb', e.target.value)} />
          </Field>
        </div>
      </Card>

      <Card
        title="Submission Format"
        icon="https://api.iconify.design/lucide:upload.svg?color=%232D6A6A"
        subtitle="How students are allowed to submit"
      >
        <div className="flex gap-3">
          <ModePill value="files" selected={form.submissionMode === 'files'} onClick={v => set('submissionMode', v)} label="Individual Files"  desc="Upload source files directly" />
          <ModePill value="zip"   selected={form.submissionMode === 'zip'}   onClick={v => set('submissionMode', v)} label="ZIP Archive"       desc="Single ZIP upload" />
          <ModePill value="both"  selected={form.submissionMode === 'both'}  onClick={v => set('submissionMode', v)} label="Either Allowed"    desc="Student's choice" />
        </div>
      </Card>
    </div>
  );

  // ── Step 1: Questions ──────────────────────────────────────────────────
  const renderStep1 = () => (
    <div className="space-y-4">
      {/* Total marks banner */}
      <div className="flex items-center justify-between px-6 py-4 rounded-2xl bg-[#1A1714] text-white">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-[#A8A29E]">Total Marks</p>
          <p className="text-xs text-[#6B6560] mt-0.5">Calculated across all questions</p>
        </div>
        <span className="text-4xl font-black text-[#CF7249]">{totalMarks}</span>
      </div>

      {questions.map((q, i) => (
        <QuestionCard
          key={i} q={q} i={i} total={questions.length}
          onChange={qChange} onRemove={removeQ}
          onDuplicate={duplicateQ} onMove={moveQ}
          submissionMode={form.submissionMode}
          allowedExtensions={form.allowedExtensions}
        />
      ))}

      <button
        type="button"
        onClick={addQ}
        className="w-full py-4 rounded-3xl border-2 border-dashed border-[#E8E1D8] text-sm font-semibold text-[#A8A29E] hover:border-[#CF7249] hover:text-[#CF7249] hover:bg-[#FEF3EC] transition-all"
      >
        + Add Question
      </button>
    </div>
  );

  // ── Step 2: Detection ──────────────────────────────────────────────────
  const renderStep2 = () => (
    <div className="space-y-5">
      <Card
        title="Detection Types"
        icon="https://api.iconify.design/lucide:scan-search.svg?color=%23CF7249"
        subtitle="Choose which clone types to run during analysis"
      >
        <div className="grid grid-cols-2 gap-3">
          <DetectionCard num={1} label="Exact Copy"      desc="Whitespace and comment differences only."                                 enabled={form.enableType1} onToggle={() => set('enableType1', !form.enableType1)} accent="#C4827A" bg="#FAEDEC" border="#F0C4C0" />
          <DetectionCard num={2} label="Renamed Vars"    desc="Identifier and literal renaming, same structure."                          enabled={form.enableType2} onToggle={() => set('enableType2', !form.enableType2)} accent="#CF7249" bg="#FEF3EC" border="#FCDDC5" />
          <DetectionCard num={3} label="Structural Clone" desc="Modified statements beyond simple renaming."                              enabled={form.enableType3} onToggle={() => set('enableType3', !form.enableType3)} accent="#2D6A6A" bg="#EBF4F4" border="#B8D9D9" />
          <DetectionCard num={4} label="Semantic / I/O"  desc="Same algorithm, different implementation. Caught via I/O testing + PDG."  enabled={form.enableType4} onToggle={() => set('enableType4', !form.enableType4)} accent="#8B9BB4" bg="#EFF2F7" border="#C8D2E0" />
        </div>
      </Card>

      <Card
        title="Similarity Thresholds"
        icon="https://api.iconify.design/lucide:sliders-horizontal.svg?color=%232D6A6A"
        subtitle="Control the sensitivity of flagging"
      >
        <div className="grid md:grid-cols-2 gap-6">
          {[
            { key: 'highSimilarityThreshold',   label: 'High Threshold',   sub: 'Flagged as likely plagiarism',  color: '#CF7249' },
            { key: 'mediumSimilarityThreshold',  label: 'Medium Threshold', sub: 'Flagged as suspicious',         color: '#2D6A6A' },
          ].map(({ key, label, sub, color }) => (
            <div key={key}>
              <div className="flex justify-between items-center mb-2">
                <div>
                  <p className="text-xs font-bold uppercase tracking-widest text-[#6B6560]">{label}</p>
                  <p className="text-xs text-[#A8A29E]">{sub}</p>
                </div>
                <span className="text-2xl font-black" style={{ color }}>{form[key]}%</span>
              </div>
              <input
                type="range" min="30" max="100" value={form[key]}
                onChange={e => set(key, parseInt(e.target.value))}
                className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                style={{ accentColor: color }}
              />
            </div>
          ))}
        </div>
      </Card>

      <Card
        title="Analysis Options"
        icon="https://api.iconify.design/lucide:settings-2.svg?color=%238B9BB4"
      >
        <Field label="When to Run Analysis">
          <div className="relative">
            <select value={form.analysisMode} onChange={e => set('analysisMode', e.target.value)} className={selectCls}>
              <option value="immediate">Immediate — analyze on each submission</option>
              <option value="after_deadline">After Deadline — batch run when deadline passes</option>
              <option value="manual">Manual — instructor triggers analysis</option>
            </select>
            <svg className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </div>
        </Field>
        <div className="space-y-4 pt-1">
          <Toggle checked={form.showResultsToStudents} onChange={() => set('showResultsToStudents', !form.showResultsToStudents)} label="Show results to students" sub="Students can view their similarity scores after analysis." />
          <div className="h-px bg-[#F0EBE3]" />
          <Toggle checked={form.generateFeedback} onChange={() => set('generateFeedback', !form.generateFeedback)} label="Generate feedback reports" sub="Produce detailed per-student reports highlighting flagged code." />
        </div>
      </Card>
    </div>
  );

  // ── Step 3: Review ─────────────────────────────────────────────────────
  const renderStep3 = () => {
    const enabledTypes = [
      form.enableType1 && 'Type-1', form.enableType2 && 'Type-2',
      form.enableType3 && 'Type-3', form.enableType4 && 'Type-4',
    ].filter(Boolean);
    const lang = langs.find(l => l.value === form.primaryLanguage)?.label || form.primaryLanguage;

    return (
      <div className="space-y-5">
        {/* Green banner */}
        <div className="px-6 py-4 rounded-2xl bg-[#EBF4F4] border border-[#B8D9D9]">
          <p className="text-sm font-bold text-[#2D6A6A]">Review and confirm</p>
          <p className="text-xs text-[#2D6A6A]/70 mt-0.5">Once created, students in the selected course can see and submit this assignment.</p>
        </div>

        {/* Summary grid */}
        <div className="grid md:grid-cols-2 gap-4">
          <Card title="Assignment">
            <div className="space-y-3 text-sm">
              {[
                ['Title',       form.title || '—'],
                ['Course',      courses.find(c => String(c.course_id) === String(form.courseId))?.course_name || '—'],
                ['Language',    lang],
                ['Due Date',    form.dueDate ? new Date(form.dueDate).toLocaleString() : '—'],
                ['Submission',  form.submissionMode],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between items-start gap-2">
                  <span className="text-[#A8A29E] flex-shrink-0">{k}</span>
                  <span className="font-semibold text-[#1A1714] text-right">{v}</span>
                </div>
              ))}
            </div>
          </Card>
          <Card title="Detection">
            <div className="space-y-3 text-sm">
              <div className="flex flex-wrap gap-2">
                {enabledTypes.map(t => (
                  <span key={t} className="text-xs font-bold px-2.5 py-1 rounded-full bg-[#FEF3EC] text-[#CF7249]">{t}</span>
                ))}
                {enabledTypes.length === 0 && <span className="text-[#A8A29E] text-xs">No detectors selected</span>}
              </div>
              <div className="h-px bg-[#F0EBE3]" />
              {[
                ['High threshold',   `${form.highSimilarityThreshold}%`],
                ['Medium threshold', `${form.mediumSimilarityThreshold}%`],
                ['Analysis mode',    form.analysisMode.replace('_', ' ')],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between">
                  <span className="text-[#A8A29E]">{k}</span>
                  <span className="font-semibold text-[#1A1714]">{v}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card title={`Questions — ${questions.length} total, ${totalMarks} marks`}>
          <div className="space-y-3">
            {questions.map((q, i) => (
              <div key={i} className="flex items-center gap-4 px-4 py-3 rounded-2xl bg-[#F7F3EE]">
                <div className="w-7 h-7 rounded-xl bg-[#CF7249] text-white flex items-center justify-center text-xs font-black flex-shrink-0">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-[#1A1714] truncate">{q.title || 'Untitled'}</p>
                  {q.description && <p className="text-xs text-[#A8A29E] truncate">{q.description}</p>}
                </div>
                <span className="text-sm font-bold text-[#CF7249] flex-shrink-0">{q.maxMarks || 0} pts</span>
              </div>
            ))}
          </div>
        </Card>
      </div>
    );
  };

  // ── Layout ────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#F7F3EE] pt-14" style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <div className="max-w-3xl mx-auto px-6 py-10">

        {/* Page header */}
        <div className="mb-8">
          <Link to="/courses" className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-4 transition-colors">
            <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>
            Back to courses
          </Link>
          <h1 className="text-2xl font-bold text-[#1A1714]">Create Assignment</h1>
          <p className="text-sm text-[#6B6560] mt-1">Fill in the details below to create a new assignment for your students.</p>
        </div>

        <StepBar current={step} />

        {/* Step content */}
        <div className="mb-8">
          {step === 0 && renderStep0()}
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 px-5 py-3.5 rounded-2xl bg-[#FAEDEC] border border-[#F0C4C0] mb-5">
            <svg width="16" height="16" fill="none" stroke="#C4827A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <p className="text-sm font-semibold text-[#C4827A]">{error}</p>
          </div>
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between items-center">
          {step > 0
            ? <button onClick={prevStep} className="inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl border border-[#E8E1D8] bg-white text-sm font-semibold text-[#1A1714] hover:bg-[#F7F3EE] transition-colors">
                <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>
                Back
              </button>
            : <div />
          }

          {step < STEPS.length - 1 ? (
            <button onClick={nextStep} className="inline-flex items-center gap-2 px-6 py-2.5 rounded-2xl bg-[#CF7249] text-white text-sm font-bold hover:bg-[#B85E38] transition-colors">
              Continue
              <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>
            </button>
          ) : (
            <button onClick={handleSubmit} disabled={loading} className="inline-flex items-center gap-2 px-7 py-2.5 rounded-2xl bg-[#CF7249] text-white text-sm font-bold hover:bg-[#B85E38] disabled:opacity-50 transition-colors">
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  Creating...
                </>
              ) : (
                <>
                  Create Assignment
                  <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateAssignment;
