import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import courseService from '../../services/courseService';
import assignmentService from '../../services/assignmentService';
import PageLoader from '../../Components/common/PageLoader';

// ─── Shared style tokens ───────────────────────────────────────────────────
const inputCls = `w-full px-5 py-4 border-2 border-[#E8E1D8] rounded-2xl bg-white
  text-base text-[#1A1714] placeholder-[#C4B8AE]
  focus:outline-none focus:border-[#CF7249] focus:ring-4 focus:ring-[#CF7249]/10
  transition-all duration-150`;

const selectCls = inputCls + ' appearance-none cursor-pointer';

// ─── Step bar ─────────────────────────────────────────────────────────────
const STEPS = ['Basics', 'Questions', 'Detection', 'Review'];

const StepBar = ({ current, editMode }) => (
  <div className="flex items-center gap-0 mb-12">
    {STEPS.map((label, i) => {
      const done   = i < current;
      const active = i === current;
      return (
        <React.Fragment key={label}>
          <div className="flex flex-col items-center gap-2 flex-shrink-0">
            <div className={`w-11 h-11 rounded-full flex items-center justify-center text-sm font-black transition-all duration-200
              ${done   ? 'bg-[#CF7249] text-white shadow-lg shadow-[#CF7249]/30'
              : active ? 'bg-[#1A1714] text-white ring-4 ring-[#1A1714]/10 scale-110'
                       : 'bg-[#F0EBE3] text-[#A8A29E]'}`}>
              {done
                ? <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
                : i + 1}
            </div>
            <span className={`text-xs font-bold uppercase tracking-widest whitespace-nowrap
              ${active ? 'text-[#1A1714]' : done ? 'text-[#CF7249]' : 'text-[#A8A29E]'}`}>
              {label}
            </span>
          </div>
          {i < STEPS.length - 1 && (
            <div className={`flex-1 h-0.5 mx-3 mb-6 transition-all duration-300
              ${i < current ? 'bg-[#CF7249]' : 'bg-[#E8E1D8]'}`} />
          )}
        </React.Fragment>
      );
    })}
  </div>
);

// ─── Big section label ─────────────────────────────────────────────────────
const SectionLabel = ({ children, required }) => (
  <label className="block text-base font-bold text-[#1A1714] mb-2">
    {children}{required && <span className="text-[#CF7249] ml-1">*</span>}
  </label>
);

const Hint = ({ children }) => (
  <p className="text-sm text-[#A8A29E] mt-1.5">{children}</p>
);

// ─── Big card ──────────────────────────────────────────────────────────────
const BigCard = ({ children, accent, title, subtitle, icon: Icon }) => (
  <div className="bg-white rounded-3xl border-2 border-[#E8E1D8] overflow-hidden">
    {(title || Icon) && (
      <div className={`px-8 py-6 border-b-2 border-[#F0EBE3] flex items-center gap-4`}
        style={{ background: accent ? `${accent}08` : 'transparent' }}>
        {Icon && (
          <div className="w-12 h-12 rounded-2xl flex items-center justify-center flex-shrink-0"
            style={{ background: accent ? `${accent}20` : '#F7F3EE' }}>
            <Icon color={accent || '#CF7249'} />
          </div>
        )}
        <div>
          {title && <p className="text-xl font-bold text-[#1A1714]">{title}</p>}
          {subtitle && <p className="text-sm text-[#A8A29E] mt-0.5">{subtitle}</p>}
        </div>
      </div>
    )}
    <div className="px-8 py-8 space-y-7">{children}</div>
  </div>
);

// ─── Mode pill ────────────────────────────────────────────────────────────
const ModePill = ({ value, selected, onClick, label, desc }) => (
  <button type="button" onClick={() => onClick(value)}
    className={`flex-1 py-5 px-5 rounded-2xl border-2 text-left transition-all duration-150
      ${selected ? 'border-[#CF7249] bg-[#FEF3EC] shadow-md shadow-[#CF7249]/10' : 'border-[#E8E1D8] bg-white hover:border-[#D4C9BE]'}`}>
    <p className={`text-base font-bold ${selected ? 'text-[#CF7249]' : 'text-[#1A1714]'}`}>{label}</p>
    <p className={`text-sm mt-1 ${selected ? 'text-[#CF7249]/70' : 'text-[#A8A29E]'}`}>{desc}</p>
  </button>
);

// ─── Detection type card ──────────────────────────────────────────────────
const DetectionCard = ({ num, label, desc, enabled, onToggle, accent, bg }) => (
  <div onClick={onToggle} className="rounded-2xl border-2 p-6 cursor-pointer transition-all duration-150 select-none"
    style={{ background: enabled ? bg : 'white', borderColor: enabled ? accent : '#E8E1D8' }}>
    <div className="flex items-start justify-between mb-3">
      <span className="text-xs font-black uppercase tracking-widest" style={{ color: enabled ? accent : '#A8A29E' }}>
        Type-{num}
      </span>
      <div className="w-6 h-6 rounded-full border-2 flex items-center justify-center flex-shrink-0"
        style={{ borderColor: enabled ? accent : '#E8E1D8', background: enabled ? accent : 'white' }}>
        {enabled && <svg width="12" height="12" fill="none" stroke="white" strokeWidth="3" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>}
      </div>
    </div>
    <p className="text-base font-bold text-[#1A1714] mb-1">{label}</p>
    <p className="text-sm text-[#6B6560] leading-relaxed">{desc}</p>
  </div>
);

// ─── Toggle ───────────────────────────────────────────────────────────────
const Toggle = ({ checked, onChange, label, sub }) => (
  <div className="flex items-center justify-between gap-4 cursor-pointer py-2" onClick={onChange}>
    <div>
      <p className="text-base font-semibold text-[#1A1714]">{label}</p>
      {sub && <p className="text-sm text-[#A8A29E] mt-0.5">{sub}</p>}
    </div>
    <div className={`relative w-13 h-7 rounded-full transition-colors duration-200 flex-shrink-0 ${checked ? 'bg-[#CF7249]' : 'bg-[#E8E1D8]'}`}
      style={{ width: 52, height: 28 }}>
      <div className={`absolute top-1 left-1 w-5 h-5 rounded-full bg-white shadow-sm transition-transform duration-200 ${checked ? 'translate-x-6' : 'translate-x-0'}`} />
    </div>
  </div>
);

// ─── Question card ─────────────────────────────────────────────────────────
const QuestionCard = ({ q, i, total, onChange, onRemove, onDuplicate, onMove, allowedExtensions }) => (
  <div className="bg-white rounded-3xl border-2 border-[#E8E1D8] overflow-hidden">
    <div className="px-7 py-5 bg-[#F7F3EE] border-b-2 border-[#E8E1D8] flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-2xl bg-[#CF7249] text-white flex items-center justify-center text-sm font-black shadow-md shadow-[#CF7249]/30">
          Q{i + 1}
        </div>
        <p className="text-base font-bold text-[#1A1714] truncate max-w-xs">
          {q.title || <span className="text-[#A8A29E] font-normal italic">Untitled question</span>}
        </p>
      </div>
      <div className="flex items-center gap-1">
        <button type="button" onClick={() => onMove(i, 'up')} disabled={i === 0}
          className="p-2 rounded-xl hover:bg-[#E8E1D8] disabled:opacity-20 text-[#6B6560] transition-colors">
          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M18 15l-6-6-6 6"/></svg>
        </button>
        <button type="button" onClick={() => onMove(i, 'down')} disabled={i === total - 1}
          className="p-2 rounded-xl hover:bg-[#E8E1D8] disabled:opacity-20 text-[#6B6560] transition-colors">
          <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
        </button>
        <button type="button" onClick={() => onDuplicate(i)}
          className="px-3 py-1.5 rounded-xl text-sm font-bold text-[#2D6A6A] hover:bg-[#EBF4F4] transition-colors">Copy</button>
        {total > 1 && (
          <button type="button" onClick={() => onRemove(i)}
            className="px-3 py-1.5 rounded-xl text-sm font-bold text-[#C4827A] hover:bg-[#FAEDEC] transition-colors">Remove</button>
        )}
      </div>
    </div>
    <div className="px-7 py-7 space-y-5">
      <div className="grid md:grid-cols-3 gap-5">
        <div className="md:col-span-2">
          <SectionLabel required>Question Title</SectionLabel>
          <input className={inputCls} value={q.title}
            onChange={e => onChange(i, 'title', e.target.value)}
            placeholder="e.g. Implement a Binary Search Tree" />
        </div>
        <div>
          <SectionLabel required>Max Marks</SectionLabel>
          <input className={inputCls} type="number" min="0" value={q.maxMarks}
            onChange={e => onChange(i, 'maxMarks', e.target.value)} />
        </div>
      </div>
      <div>
        <SectionLabel required>Problem Description</SectionLabel>
        <textarea className={inputCls + ' resize-none'} rows={4} value={q.description}
          onChange={e => onChange(i, 'description', e.target.value)}
          placeholder="Describe the problem, expected behavior, constraints, and edge cases..." />
      </div>
      <div className="grid md:grid-cols-2 gap-5">
        <div>
          <SectionLabel>Expected Files</SectionLabel>
          <input className={inputCls} value={q.expectedFiles}
            onChange={e => onChange(i, 'expectedFiles', e.target.value)}
            placeholder="BinaryTree.cpp, Node.h" />
          <Hint>Comma-separated guide for students</Hint>
        </div>
        <div>
          <SectionLabel>Override Extensions</SectionLabel>
          <input className={inputCls} value={q.allowedExtensions}
            onChange={e => onChange(i, 'allowedExtensions', e.target.value)}
            placeholder="Optional override" />
          <Hint>Leave empty to inherit: {allowedExtensions}</Hint>
        </div>
      </div>
    </div>
  </div>
);

// ─── Icons ────────────────────────────────────────────────────────────────
const IconFile   = ({ color }) => <svg width="20" height="20" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>;
const IconUpload = ({ color }) => <svg width="20" height="20" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>;
const IconScan   = ({ color }) => <svg width="20" height="20" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24"><path d="M3 7V5a2 2 0 012-2h2M17 3h2a2 2 0 012 2v2M21 17v2a2 2 0 01-2 2h-2M7 21H5a2 2 0 01-2-2v-2"/><line x1="7" y1="12" x2="17" y2="12"/></svg>;

// ─── Minimalist vectors ────────────────────────────────────────────────────
const HandVector = () => (
  <svg width="90" height="90" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg" className="opacity-25">
    <path d="M35 58V32a4 4 0 018 0v14" stroke="#CF7249" strokeWidth="2.5" strokeLinecap="round"/>
    <path d="M43 40a4 4 0 018 0v10" stroke="#CF7249" strokeWidth="2.5" strokeLinecap="round"/>
    <path d="M51 42a4 4 0 018 0v8" stroke="#CF7249" strokeWidth="2.5" strokeLinecap="round"/>
    <path d="M35 54c0 0-5-2-5-8v-8a4 4 0 018 0" stroke="#CF7249" strokeWidth="2.5" strokeLinecap="round"/>
    <path d="M59 50v5c0 8-5 13-13 13h-3c-5 0-9-3-11-7" stroke="#CF7249" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
  </svg>
);

const PencilVector = () => (
  <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg" className="opacity-25">
    <path d="M14 56l4-16L50 8l12 12L30 52l-16 4z" stroke="#2D6A6A" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M46 12l12 12" stroke="#2D6A6A" strokeWidth="2.5" strokeLinecap="round"/>
    <path d="M14 56l4-16" stroke="#2D6A6A" strokeWidth="2.5" strokeLinecap="round"/>
    <circle cx="14" cy="56" r="3" fill="#2D6A6A" opacity="0.4"/>
  </svg>
);

// ─── Language list ─────────────────────────────────────────────────────────
const LANGS = [
  { value: 'cpp',        label: 'C / C++',         ext: '.cpp,.c,.h,.hpp' },
  { value: 'java',       label: 'Java',             ext: '.java' },
  { value: 'python',     label: 'Python',           ext: '.py' },
  { value: 'javascript', label: 'JavaScript / TS',  ext: '.js,.jsx,.ts,.tsx' },
  { value: 'mixed',      label: 'Mixed languages',  ext: '.cpp,.c,.h,.java,.py,.js' },
];

// ─── Helpers ───────────────────────────────────────────────────────────────
const blankQuestion = () => ({
  title: '', description: '', expectedFiles: '', allowedExtensions: '', maxMarks: 10,
});

const mapInitialData = (data) => {
  if (!data) return null;
  return {
    courseId:                  String(data.course_id ?? ''),
    title:                     data.title ?? '',
    description:               data.description ?? '',
    dueDate:                   data.due_date
      ? new Date(data.due_date).toISOString().slice(0, 16)
      : '',
    primaryLanguage:           data.primary_language ?? 'cpp',
    allowedExtensions:         data.allowed_extensions ?? '.cpp,.c,.h',
    submissionMode:            data.submission_mode ?? 'files',
    maxFileSizeMb:             data.max_file_size_mb ?? 10,
    enableType1:               data.enable_type1 ?? true,
    enableType2:               data.enable_type2 ?? true,
    enableType3:               data.enable_type3 ?? true,
    enableType4:               data.enable_type4 ?? true,
    highSimilarityThreshold:   data.high_similarity_threshold ?? 85,
    mediumSimilarityThreshold: data.medium_similarity_threshold ?? 70,
    analysisMode:              data.analysis_mode ?? 'after_deadline',
    showResultsToStudents:     data.show_results_to_students ?? false,
    generateFeedback:          data.generate_feedback ?? true,
  };
};

const mapInitialQuestions = (data) => {
  if (!data?.questions?.length) return [blankQuestion()];
  return data.questions.map(q => ({
    question_id:      q.question_id ?? q.id ?? undefined,
    title:            q.title ?? '',
    description:      q.description ?? '',
    expectedFiles:    Array.isArray(q.expectedFiles)
      ? q.expectedFiles.join(', ')
      : (q.expected_files ? (Array.isArray(q.expected_files) ? q.expected_files.join(', ') : q.expected_files) : ''),
    allowedExtensions: Array.isArray(q.allowedExtensions)
      ? q.allowedExtensions.join(', ')
      : (q.allowed_extensions ? (Array.isArray(q.allowed_extensions) ? q.allowed_extensions.join(', ') : q.allowed_extensions) : ''),
    maxMarks: q.maxMarks ?? q.max_marks ?? 10,
  }));
};

// ─── Main component ────────────────────────────────────────────────────────
const CreateAssignment = ({ editMode = false, initialData = null, assignmentId = null }) => {
  const navigate       = useNavigate();
  const [searchParams] = useSearchParams();
  const preCoId        = searchParams.get('courseId');

  const [step,    setStep]    = useState(0);
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState('');

  // ── Form state — pre-filled from initialData in edit mode ──────────────
  const defaultForm = {
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
  };

  const [form, setForm] = useState(() =>
    editMode && initialData ? { ...defaultForm, ...mapInitialData(initialData) } : defaultForm
  );

  const [questions, setQuestions] = useState(() =>
    editMode && initialData ? mapInitialQuestions(initialData) : [blankQuestion()]
  );

  // Duplicate title detection
  const [existingAssignments, setExistingAssignments] = useState([]);

  const set = (k, v) => setForm(p => ({ ...p, [k]: v }));

  useEffect(() => {
    courseService.getInstructorCourses().then(setCourses).catch(() => {});
  }, []);

  // Re-populate if initialData arrives later (EditAssignment passes it via prop)
  useEffect(() => {
    if (editMode && initialData) {
      setForm(prev => ({ ...prev, ...mapInitialData(initialData) }));
      setQuestions(mapInitialQuestions(initialData));
    }
  }, [initialData]);

  // Sync extensions when language changes (only in create mode)
  useEffect(() => {
    if (!editMode) {
      const ext = assignmentService.getExtensionsForLanguage(form.primaryLanguage).join(',');
      set('allowedExtensions', ext);
    }
  }, [form.primaryLanguage]);

  // Duplicate detection
  useEffect(() => {
    if (!form.courseId || editMode) return;
    assignmentService.getCourseAssignments(form.courseId)
      .then(d => setExistingAssignments(Array.isArray(d) ? d : []))
      .catch(() => setExistingAssignments([]));
  }, [form.courseId]);

  const duplicateTitleMatch = !editMode && form.title.trim() !== '' &&
    existingAssignments.some(a => a.title?.trim().toLowerCase() === form.title.trim().toLowerCase());

  // ── Questions helpers ──────────────────────────────────────────────────
  const qChange    = (i, f, v) => { const u = [...questions]; u[i] = { ...u[i], [f]: v }; setQuestions(u); };
  const addQ       = () => setQuestions(p => [...p, blankQuestion()]);
  const removeQ    = (i) => setQuestions(p => p.filter((_, x) => x !== i));
  const duplicateQ = (i) => { const u = [...questions]; u.splice(i + 1, 0, { ...u[i], title: u[i].title + ' (Copy)' }); setQuestions(u); };
  const moveQ      = (i, dir) => {
    if ((dir === 'up' && i === 0) || (dir === 'down' && i === questions.length - 1)) return;
    const u = [...questions]; const j = dir === 'up' ? i - 1 : i + 1;
    [u[i], u[j]] = [u[j], u[i]]; setQuestions(u);
  };

  const totalMarks = questions.reduce((s, q) => s + (parseInt(q.maxMarks) || 0), 0);

  // ── Validation ─────────────────────────────────────────────────────────
  const validate = () => {
    if (step === 0) {
      if (!editMode && !form.courseId)  return 'Please select a course.';
      if (!form.title.trim())           return 'Assignment title is required.';
      if (!form.description.trim())     return 'Description is required.';
      if (!form.dueDate)                return 'Due date is required.';
      if (duplicateTitleMatch) {
        if (!window.confirm(`An assignment named "${form.title.trim()}" already exists in this course.\n\nCreate it anyway?`))
          return 'Rename the assignment or confirm to continue.';
      }
    }
    if (step === 1) {
      for (let i = 0; i < questions.length; i++) {
        if (!questions[i].title.trim())       return `Question ${i + 1}: Title is required.`;
        if (!questions[i].description.trim()) return `Question ${i + 1}: Description is required.`;
        if (!(parseInt(questions[i].maxMarks) > 0)) return `Question ${i + 1}: Marks must be greater than 0.`;
      }
    }
    return null;
  };

  const nextStep = () => { const e = validate(); if (e) { setError(e); return; } setError(''); setStep(s => s + 1); };
  const prevStep = () => { setError(''); setStep(s => s - 1); };

  // ── Submit ─────────────────────────────────────────────────────────────
  // Helper to map camelCase to snake_case for backend
  function toSnakeCase(obj) {
    const map = {
      courseId: 'course_id',
      dueDate: 'due_date',
      primaryLanguage: 'primary_language',
      allowedExtensions: 'allowed_extensions',
      maxFileSizeMb: 'max_file_size_mb',
      enableType1: 'enable_type1',
      enableType2: 'enable_type2',
      enableType3: 'enable_type3',
      enableType4: 'enable_type4',
      highSimilarityThreshold: 'high_similarity_threshold',
      mediumSimilarityThreshold: 'medium_similarity_threshold',
      analysisMode: 'analysis_mode',
      showResultsToStudents: 'show_results_to_students',
      generateFeedback: 'generate_feedback',
      submissionMode: 'submission_mode',
    };
    const out = {};
    for (const k in obj) {
      out[map[k] || k] = obj[k];
    }
    return out;
  }

  const handleSubmit = async () => {
    setLoading(true); setError('');
    const payload = {
      ...toSnakeCase(form),
      questions: questions.map(q => ({
        ...(q.question_id ? { question_id: q.question_id } : {}),
        title:             q.title,
        description:       q.description,
        expectedFiles:     q.expectedFiles ? q.expectedFiles.split(',').map(f => f.trim()).filter(Boolean) : [],
        allowedExtensions: q.allowedExtensions ? q.allowedExtensions.split(',').map(e => e.trim()).filter(Boolean) : [],
        maxMarks:          parseInt(q.maxMarks) || 0,
        submissionMode:    form.submissionMode,
      })),
    };
    try {
      if (editMode && assignmentId) {
        await assignmentService.updateAssignment(assignmentId, payload);
        navigate(`/assignments/${assignmentId}`);
      } else {
        const result = await assignmentService.createAssignment(payload);
        navigate(`/assignments/${result.assignment.assignment_id}`);
      }
    } catch (err) {
      setError(err.response?.data?.error || `Failed to ${editMode ? 'update' : 'create'} assignment.`);
      setLoading(false);
    }
  };

  // ── Step 0: Basics ─────────────────────────────────────────────────────
  const renderStep0 = () => (
    <div className="space-y-6">
      <BigCard
        title="Assignment Details"
        subtitle="Core information visible to all students in this course"
        icon={IconFile}
        accent="#CF7249"
      >
        {/* Course selector — hidden in edit mode */}
        {!editMode && (
          <div>
            <SectionLabel required>Select Course</SectionLabel>
            <div className="relative">
              <select value={form.courseId} onChange={e => set('courseId', e.target.value)} className={selectCls}>
                <option value="">Choose a course...</option>
                {courses.map(c => <option key={c.course_id} value={c.course_id}>{c.course_code} — {c.course_name}</option>)}
              </select>
              <svg className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
            </div>
          </div>
        )}

        {/* Title */}
        <div>
          <SectionLabel required>Assignment Title</SectionLabel>
          <input
            className={inputCls + (duplicateTitleMatch ? ' border-amber-400 focus:border-amber-500 focus:ring-amber-200' : '')}
            value={form.title}
            onChange={e => set('title', e.target.value)}
            placeholder="e.g. Assignment 03: Trees and Graphs" />
          {duplicateTitleMatch && (
            <p className="text-sm text-amber-600 font-semibold mt-2">
              ⚠ An assignment with this name already exists in this course.
            </p>
          )}
        </div>

        {/* Description */}
        <div>
          <SectionLabel required>Description</SectionLabel>
          <textarea className={inputCls + ' resize-none'} rows={5}
            value={form.description}
            onChange={e => set('description', e.target.value)}
            placeholder="Explain the objectives, constraints, grading breakdown, and any important notes for students..." />
        </div>

        {/* Due date + Language */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <SectionLabel required>Due Date & Time</SectionLabel>
            <input className={inputCls} type="datetime-local" value={form.dueDate}
              onChange={e => set('dueDate', e.target.value)} />
          </div>
          <div>
            <SectionLabel required>Primary Language</SectionLabel>
            <div className="relative">
              <select value={form.primaryLanguage}
                onChange={e => set('primaryLanguage', e.target.value)} className={selectCls}>
                {LANGS.map(l => <option key={l.value} value={l.value}>{l.label}</option>)}
              </select>
              <svg className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
            </div>
          </div>
        </div>

        {/* Extensions + Max size */}
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <SectionLabel>Allowed Extensions</SectionLabel>
            <input className={inputCls} value={form.allowedExtensions}
              onChange={e => set('allowedExtensions', e.target.value)} placeholder=".cpp,.c,.h" />
            <Hint>Comma-separated</Hint>
          </div>
          <div>
            <SectionLabel>Max File Size (MB)</SectionLabel>
            <input className={inputCls} type="number" min="1" max="200"
              value={form.maxFileSizeMb} onChange={e => set('maxFileSizeMb', e.target.value)} />
          </div>
        </div>
      </BigCard>

      {/* Submission format */}
      <BigCard title="Submission Format" subtitle="How students submit their work" icon={IconUpload} accent="#2D6A6A">
        <div className="flex flex-col sm:flex-row gap-4">
          <ModePill value="files"  selected={form.submissionMode === 'files'}  onClick={v => set('submissionMode', v)} label="Individual Files"  desc="Upload source files directly" />
          <ModePill value="zip"    selected={form.submissionMode === 'zip'}    onClick={v => set('submissionMode', v)} label="ZIP Archive"      desc="Single ZIP upload" />
          <ModePill value="both"   selected={form.submissionMode === 'both'}   onClick={v => set('submissionMode', v)} label="Either Allowed"   desc="Student's choice" />
        </div>
      </BigCard>
    </div>
  );

  // ── Step 1: Questions ──────────────────────────────────────────────────
  const renderStep1 = () => (
    <div className="space-y-5">
      {/* Total marks banner */}
      <div className="flex items-center justify-between px-8 py-6 rounded-3xl bg-[#1A1714] text-white">
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-[#6B6560] mb-1">Total Marks</p>
          <p className="text-sm text-[#A8A29E]">Calculated across all questions</p>
        </div>
        <span className="text-5xl font-black text-[#CF7249]">{totalMarks}</span>
      </div>

      {questions.map((q, i) => (
        <QuestionCard key={i} q={q} i={i} total={questions.length}
          onChange={qChange} onRemove={removeQ}
          onDuplicate={duplicateQ} onMove={moveQ}
          allowedExtensions={form.allowedExtensions} />
      ))}

      <button type="button" onClick={addQ}
        className="w-full py-6 rounded-3xl border-2 border-dashed border-[#E8E1D8] text-base font-bold text-[#A8A29E]
          hover:border-[#CF7249] hover:text-[#CF7249] hover:bg-[#FEF3EC] transition-all">
        + Add Another Question
      </button>
    </div>
  );

  // ── Step 2: Detection ──────────────────────────────────────────────────
  const renderStep2 = () => (
    <div className="space-y-6">
      <BigCard title="Detection Types" subtitle="Choose which clone detection algorithms to run" icon={IconScan} accent="#CF7249">
        <div className="grid grid-cols-2 gap-4">
          <DetectionCard num={1} label="Exact Copy"       desc="Whitespace and comment differences only."                                enabled={form.enableType1} onToggle={() => set('enableType1', !form.enableType1)} accent="#C4827A" bg="#FAEDEC" />
          <DetectionCard num={2} label="Renamed Variables" desc="Identifier renaming, same structure."                                    enabled={form.enableType2} onToggle={() => set('enableType2', !form.enableType2)} accent="#CF7249" bg="#FEF3EC" />
          <DetectionCard num={3} label="Structural Clone"  desc="Modified statements beyond simple renaming."                             enabled={form.enableType3} onToggle={() => set('enableType3', !form.enableType3)} accent="#2D6A6A" bg="#EBF4F4" />
          <DetectionCard num={4} label="Semantic / I/O"   desc="Same algorithm, different implementation. Caught via I/O testing + PDG." enabled={form.enableType4} onToggle={() => set('enableType4', !form.enableType4)} accent="#8B9BB4" bg="#EFF2F7" />
        </div>
      </BigCard>

      <BigCard title="Similarity Thresholds" subtitle="Control how sensitive the detection is">
        <div className="space-y-8">
          {[
            { key: 'highSimilarityThreshold',   label: 'High — Likely Plagiarism',  color: '#CF7249' },
            { key: 'mediumSimilarityThreshold',  label: 'Medium — Suspicious',       color: '#2D6A6A' },
          ].map(({ key, label, color }) => (
            <div key={key}>
              <div className="flex justify-between items-center mb-3">
                <p className="text-base font-bold text-[#1A1714]">{label}</p>
                <span className="text-4xl font-black" style={{ color }}>{form[key]}%</span>
              </div>
              <input type="range" min="30" max="100" value={form[key]}
                onChange={e => set(key, parseInt(e.target.value))}
                className="w-full h-2 rounded-full appearance-none cursor-pointer"
                style={{ accentColor: color }} />
            </div>
          ))}
        </div>
      </BigCard>

      <BigCard title="Analysis Options">
        <div>
          <SectionLabel>When to Run Analysis</SectionLabel>
          <div className="relative">
            <select value={form.analysisMode} onChange={e => set('analysisMode', e.target.value)} className={selectCls}>
              <option value="immediate">Immediate — analyze on each submission</option>
              <option value="after_deadline">After Deadline — batch run when deadline passes</option>
              <option value="manual">Manual — instructor triggers analysis</option>
            </select>
            <svg className="absolute right-5 top-1/2 -translate-y-1/2 pointer-events-none text-[#A8A29E]" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </div>
        </div>
        <div className="space-y-4 pt-2 divide-y divide-[#F0EBE3]">
          <Toggle checked={form.showResultsToStudents}
            onChange={() => set('showResultsToStudents', !form.showResultsToStudents)}
            label="Show results to students"
            sub="Students can see their similarity scores after analysis completes." />
          <div className="pt-4">
            <Toggle checked={form.generateFeedback}
              onChange={() => set('generateFeedback', !form.generateFeedback)}
              label="Generate feedback reports"
              sub="Produce detailed per-student reports highlighting flagged code sections." />
          </div>
        </div>
      </BigCard>
    </div>
  );

  // ── Step 3: Review ─────────────────────────────────────────────────────
  const renderStep3 = () => {
    const enabledTypes = [
      form.enableType1 && 'Type-1', form.enableType2 && 'Type-2',
      form.enableType3 && 'Type-3', form.enableType4 && 'Type-4',
    ].filter(Boolean);
    const lang    = LANGS.find(l => l.value === form.primaryLanguage)?.label || form.primaryLanguage;
    const course  = courses.find(c => String(c.course_id) === String(form.courseId));

    return (
      <div className="space-y-6">
        {/* Banner */}
        <div className="px-8 py-6 rounded-3xl bg-[#EBF4F4] border-2 border-[#B8D9D9] flex items-center gap-5">
          <div className="w-14 h-14 rounded-2xl bg-[#2D6A6A] flex items-center justify-center flex-shrink-0">
            <svg width="24" height="24" fill="none" stroke="white" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
          </div>
          <div>
            <p className="text-lg font-bold text-[#2D6A6A]">{editMode ? 'Ready to update' : 'Ready to publish'}</p>
            <p className="text-sm text-[#2D6A6A]/70 mt-0.5">
              {editMode
                ? 'Review your changes below then click Update Assignment.'
                : 'Once created, students in the selected course can see and submit this assignment.'}
            </p>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-5">
          <BigCard title="Assignment">
            <div className="space-y-4">
              {[
                ['Title',       form.title || '—'],
                ['Course',      editMode ? initialData?.course_name || '—' : (course?.course_name || '—')],
                ['Language',    lang],
                ['Due Date',    form.dueDate ? new Date(form.dueDate).toLocaleString() : '—'],
                ['Submission',  form.submissionMode],
                ['Max Size',    `${form.maxFileSizeMb} MB`],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between items-start gap-4 py-2 border-b border-[#F0EBE3] last:border-0">
                  <span className="text-sm text-[#A8A29E]">{k}</span>
                  <span className="text-sm font-bold text-[#1A1714] text-right">{v}</span>
                </div>
              ))}
            </div>
          </BigCard>

          <BigCard title="Detection">
            <div className="space-y-4">
              <div className="flex flex-wrap gap-2">
                {enabledTypes.map(t => (
                  <span key={t} className="text-sm font-bold px-3 py-1.5 rounded-full bg-[#FEF3EC] text-[#CF7249]">{t}</span>
                ))}
                {enabledTypes.length === 0 && <span className="text-sm text-[#A8A29E]">No detectors selected</span>}
              </div>
              {[
                ['High threshold',   `${form.highSimilarityThreshold}%`],
                ['Medium threshold', `${form.mediumSimilarityThreshold}%`],
                ['Analysis mode',    form.analysisMode.replace('_', ' ')],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-2 border-b border-[#F0EBE3] last:border-0">
                  <span className="text-sm text-[#A8A29E]">{k}</span>
                  <span className="text-sm font-bold text-[#1A1714]">{v}</span>
                </div>
              ))}
            </div>
          </BigCard>
        </div>

        <BigCard title={`${questions.length} Question${questions.length !== 1 ? 's' : ''} — ${totalMarks} total marks`}>
          <div className="space-y-3">
            {questions.map((q, i) => (
              <div key={i} className="flex items-center gap-5 px-5 py-4 rounded-2xl bg-[#F7F3EE]">
                <div className="w-9 h-9 rounded-xl bg-[#CF7249] text-white flex items-center justify-center text-sm font-black flex-shrink-0">
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-base font-bold text-[#1A1714] truncate">{q.title || 'Untitled'}</p>
                  {q.description && <p className="text-sm text-[#A8A29E] truncate">{q.description}</p>}
                </div>
                <span className="text-base font-black text-[#CF7249] flex-shrink-0">{q.maxMarks || 0} pts</span>
              </div>
            ))}
          </div>
        </BigCard>
      </div>
    );
  };

  // ── Layout ─────────────────────────────────────────────────────────────
  const backLink = editMode
    ? `/assignments/${assignmentId}`
    : (form.courseId ? `/courses/${form.courseId}` : '/courses');

  return (
    <div className="min-h-screen bg-[#F7F3EE] pt-14">
      <div className="max-w-3xl mx-auto px-6 py-10">

        {/* Page header */}
        <div className="mb-10">
          <Link to={backLink}
            className="inline-flex items-center gap-1.5 text-sm font-semibold text-[#A8A29E] hover:text-[#1A1714] mb-5 transition-colors">
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>
            {editMode ? 'Back to Assignment' : 'Back to Courses'}
          </Link>

          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.2em] text-[#CF7249] mb-2">
                {editMode ? 'Edit Mode' : 'Instructor'}
              </p>
              <h1 className="text-4xl font-black text-[#1A1714]">
                {editMode ? 'Edit Assignment' : 'Create Assignment'}
              </h1>
              <p className="text-base text-[#6B6560] mt-2">
                {editMode
                  ? 'Update the details below. Changes are saved when you click Update Assignment.'
                  : 'Fill in the details to create a new assignment for your students.'}
              </p>
            </div>
            {editMode ? <PencilVector /> : <HandVector />}
          </div>
        </div>

        <StepBar current={step} editMode={editMode} />

        {/* Step content */}
        <div className="mb-8">
          {step === 0 && renderStep0()}
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
        </div>

        {/* Error */}
        {error && (
          <div className="flex items-center gap-3 px-6 py-4 rounded-2xl bg-[#FAEDEC] border-2 border-[#F0C4C0] mb-6">
            <svg width="18" height="18" fill="none" stroke="#C4827A" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
              <line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <p className="text-base font-semibold text-[#C4827A]">{error}</p>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center pt-2">
          {step > 0
            ? <button onClick={prevStep}
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-2xl border-2 border-[#E8E1D8] bg-white text-base font-bold text-[#1A1714] hover:bg-[#F7F3EE] transition-colors">
                <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M15 18l-6-6 6-6"/></svg>
                Back
              </button>
            : <div />}

          {step < STEPS.length - 1 ? (
            <button onClick={nextStep}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-[#CF7249] text-white text-base font-bold hover:bg-[#B85E38] transition-colors shadow-lg shadow-[#CF7249]/25">
              Continue
              <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M9 5l7 7-7 7"/></svg>
            </button>
          ) : (
            <button onClick={handleSubmit} disabled={loading}
              className="inline-flex items-center gap-2 px-8 py-3.5 rounded-2xl bg-[#CF7249] text-white text-base font-bold hover:bg-[#B85E38] disabled:opacity-50 transition-colors shadow-lg shadow-[#CF7249]/25">
              {loading ? (
                <>
                  <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  {editMode ? 'Saving...' : 'Creating...'}
                </>
              ) : (
                <>
                  {editMode ? 'Update Assignment' : 'Create Assignment'}
                  <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"/></svg>
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
