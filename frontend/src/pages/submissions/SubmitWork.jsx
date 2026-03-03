import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import assignmentService from '../../services/assignmentService';
import submissionService from '../../services/submissionService';

// ─── Helpers ──────────────────────────────────────────────────────────────────
const EXT_LANG = {
  '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.hpp': 'C++', '.cc': 'C++', '.cxx': 'C++',
  '.java': 'Java',
  '.py': 'Python',
  '.js': 'JavaScript', '.jsx': 'JavaScript', '.ts': 'TypeScript', '.tsx': 'TypeScript',
  '.html': 'HTML', '.css': 'CSS',
};

const getFileExt = (name) => '.' + name.split('.').pop().toLowerCase();
const isZip      = (name) => name.endsWith('.zip');
const fmtSize    = (b) => b > 1048576 ? `${(b / 1048576).toFixed(1)} MB` : `${(b / 1024).toFixed(1)} KB`;
const fmtDate    = (d) => new Date(d).toLocaleString('en-PK', { dateStyle: 'medium', timeStyle: 'short' });
const isPast     = (d) => new Date(d) < new Date();

// Language badge colours
const LANG_COLORS = {
  'C++': 'bg-blue-100 text-blue-700',
  'C': 'bg-sky-100 text-sky-700',
  'C/C++': 'bg-sky-100 text-sky-700',
  'Java': 'bg-orange-100 text-orange-700',
  'Python': 'bg-yellow-100 text-yellow-700',
  'JavaScript': 'bg-amber-100 text-amber-700',
  'TypeScript': 'bg-blue-100 text-blue-700',
  'HTML': 'bg-red-100 text-red-700',
  'CSS': 'bg-purple-100 text-purple-700',
};

// ─── Mode config derived from teacher settings ────────────────────────────────
function getModeConfig(assignment) {
  const mode = assignment?.submission_mode || 'both';
  const isWebDev = assignment?.assignment_type === 'webdev';

  if (isWebDev) return {
    allowFiles: false,
    allowZip:   true,
    label:      'Project ZIP',
    hint:       'Upload your entire project as a .zip file. All folders (frontend, backend, etc.) will be analyzed.',
    accept:     '.zip',
  };

  if (mode === 'files') return {
    allowFiles: true,
    allowZip:   false,
    label:      'Code Files',
    hint:       `Upload individual source files. Accepted: ${assignment?.allowed_extensions || 'any code file'}`,
    accept:     (assignment?.allowed_extensions || '.cpp,.c,.h,.java,.py,.js,.ts'),
  };

  if (mode === 'zip') return {
    allowFiles: false,
    allowZip:   true,
    label:      'ZIP Archive',
    hint:       'Upload all your files as a single .zip archive.',
    accept:     '.zip',
  };

  // both
  return {
    allowFiles: true,
    allowZip:   true,
    label:      'Files or ZIP',
    hint:       `Upload individual files (${assignment?.allowed_extensions}) or a .zip of your solution.`,
    accept:     (assignment?.allowed_extensions || '.cpp,.c,.h,.java,.py,.js,.ts') + ',.zip',
  };
}

// ─── File row component ────────────────────────────────────────────────────────
const FileRow = ({ file, onRemove }) => {
  const ext  = getFileExt(file.name);
  const lang = EXT_LANG[ext];
  const zip  = isZip(file.name);

  return (
    <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-white border border-gray-100 shadow-sm group">
      <span className="text-2xl flex-shrink-0">{zip ? '📦' : '📄'}</span>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-semibold text-gray-900 truncate">{file.name}</p>
        <div className="flex items-center gap-2 mt-0.5">
          <span className="text-xs text-gray-400">{fmtSize(file.size)}</span>
          {lang && (
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-md ${LANG_COLORS[lang] || 'bg-gray-100 text-gray-600'}`}>
              {lang}
            </span>
          )}
          {zip && <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-md bg-violet-100 text-violet-700">ZIP</span>}
        </div>
      </div>
      <button type="button" onClick={onRemove}
        className="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 transition-all text-xs font-bold px-2 py-1 rounded-lg hover:bg-red-50">
        Remove
      </button>
    </div>
  );
};

// ─── Drop zone ─────────────────────────────────────────────────────────────────
const DropZone = ({ modeConfig, onChange, hasFiles }) => {
  const [dragging, setDragging] = useState(false);

  const onDragOver  = (e) => { e.preventDefault(); setDragging(true); };
  const onDragLeave = ()  => setDragging(false);
  const onDrop      = (e) => {
    e.preventDefault(); setDragging(false);
    const dt = e.dataTransfer;
    if (dt?.files?.length) onChange({ target: { files: dt.files } });
  };

  return (
    <label
      onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}
      className={`block border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-150
        ${dragging ? 'border-slate-600 bg-slate-50' : hasFiles ? 'border-emerald-300 bg-emerald-50/40' : 'border-gray-200 hover:border-gray-400 hover:bg-gray-50/60'}`}>
      <div className={`text-5xl mb-4 transition-transform ${dragging ? 'scale-110' : ''}`}>
        {modeConfig.allowZip && !modeConfig.allowFiles ? '📦' : '📂'}
      </div>
      <p className="font-bold text-gray-800 text-base mb-1">
        {hasFiles ? 'Add more files' : 'Drop files here or click to browse'}
      </p>
      <p className="text-sm text-gray-500 mb-4">{modeConfig.hint}</p>
      <span className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-slate-900 text-white text-sm font-bold hover:bg-slate-700 transition-colors">
        Browse Files
      </span>
      <input type="file" multiple className="hidden" accept={modeConfig.accept} onChange={onChange} />
    </label>
  );
};

// ─── Info card ─────────────────────────────────────────────────────────────────
const InfoCard = ({ icon, title, value, sub, color = 'gray' }) => {
  const bg = { gray: 'bg-gray-50', blue: 'bg-blue-50', amber: 'bg-amber-50', emerald: 'bg-emerald-50' };
  return (
    <div className={`${bg[color]} rounded-xl px-5 py-4`}>
      <div className="flex items-center gap-2 mb-1">
        <span>{icon}</span>
        <span className="text-[10px] font-bold uppercase tracking-widest text-gray-500">{title}</span>
      </div>
      <p className="font-bold text-gray-900 text-sm">{value}</p>
      {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
    </div>
  );
};

// ─── Main Component ────────────────────────────────────────────────────────────
const SubmitWork = () => {
  const [searchParams] = useSearchParams();
  const navigate        = useNavigate();
  const assignmentId    = searchParams.get('assignmentId');

  const [assignment, setAssignment] = useState(null);
  const [files,      setFiles]      = useState([]);
  const [loading,    setLoading]    = useState(true);
  const [uploading,  setUploading]  = useState(false);
  const [error,      setError]      = useState('');
  const [dragInfo,   setDragInfo]   = useState('');

  useEffect(() => {
    if (assignmentId) {
      assignmentService.getAssignmentById(assignmentId)
        .then(setAssignment)
        .catch(() => setError('Failed to load assignment.'))
        .finally(() => setLoading(false));
    }
  }, [assignmentId]);

  const modeConfig = getModeConfig(assignment);

  // ── File validation ──────────────────────────────────────────────────────────
  const validateAndAdd = (incoming) => {
    setError('');
    const newFiles = [];

    for (const file of incoming) {
      const ext      = getFileExt(file.name);
      const isZipFile = isZip(file.name);
      const maxMB    = assignment?.max_file_size_mb || 10;
      const zipMaxMB = 200;

      // Check if zip is allowed
      if (isZipFile) {
        if (!modeConfig.allowZip) {
          setError('ZIP files are not allowed for this assignment. Upload individual code files.');
          return;
        }
        if (file.size > zipMaxMB * 1024 * 1024) {
          setError(`${file.name} exceeds the ${zipMaxMB}MB ZIP limit.`);
          return;
        }
        newFiles.push(file);
        continue;
      }

      // Check if individual files are allowed
      if (!modeConfig.allowFiles) {
        setError('Individual files are not allowed. Please upload a .zip archive.');
        return;
      }

      // Check extension
      const allowedExts = (assignment?.allowed_extensions || '')
        .split(',').map(e => e.trim()).filter(Boolean);

      if (allowedExts.length > 0 && !allowedExts.includes(ext)) {
        setError(`"${file.name}" is not allowed. Accepted extensions: ${allowedExts.join(', ')}`);
        return;
      }

      if (file.size > maxMB * 1024 * 1024) {
        setError(`"${file.name}" exceeds the ${maxMB}MB file limit.`);
        return;
      }

      newFiles.push(file);
    }

    // Don't allow mixing zip + individual files
    const existingHasZip  = files.some(f => isZip(f.name));
    const newHasZip       = newFiles.some(f => isZip(f.name));
    const existingHasCode = files.some(f => !isZip(f.name));
    const newHasCode      = newFiles.some(f => !isZip(f.name));

    if ((existingHasZip && newHasCode) || (existingHasCode && newHasZip)) {
      setError('You cannot mix ZIP files with individual code files in the same submission.');
      return;
    }

    // Avoid duplicates by name
    const existingNames = new Set(files.map(f => f.name));
    const unique = newFiles.filter(f => !existingNames.has(f.name));
    if (unique.length < newFiles.length) {
      setDragInfo(`${newFiles.length - unique.length} duplicate file(s) skipped.`);
    }

    setFiles(prev => [...prev, ...unique]);
  };

  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files || []);
    if (selected.length) validateAndAdd(selected);
    e.target.value = '';
  };

  const removeFile = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i));

  // ── Submit ───────────────────────────────────────────────────────────────────
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!files.length) { setError('Please select at least one file.'); return; }

    setUploading(true); setError('');
    try {
      const formData = new FormData();
      formData.append('assignmentId', assignmentId);
      files.forEach(f => formData.append('files', f));
      const result = await submissionService.createSubmission(formData);
      navigate(`/submissions/${result.submission.submission_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed. Please try again.');
      setUploading(false);
    }
  };

  // ── Derived state ─────────────────────────────────────────────────────────────
  const hasZip    = files.some(f => isZip(f.name));
  const hasFiles  = files.length > 0;
  const overdue   = assignment && isPast(assignment.due_date);

  // Group selected code files by language
  const langGroups = {};
  files.filter(f => !isZip(f.name)).forEach(f => {
    const lang = EXT_LANG[getFileExt(f.name)] || 'Other';
    langGroups[lang] = (langGroups[lang] || 0) + 1;
  });

  // ── Loading ───────────────────────────────────────────────────────────────────
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <div className="w-10 h-10 border-2 border-slate-900 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-sm text-gray-500 font-medium">Loading assignment…</p>
      </div>
    </div>
  );

  if (!assignment) return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <p className="text-gray-500">Assignment not found.</p>
    </div>
  );

  // ── Render ────────────────────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-gray-50" style={{ fontFamily: "'DM Sans', system-ui, sans-serif" }}>
      <style>{`@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800;900&display=swap');`}</style>

      {/* Top bar */}
      <div className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-6 py-4 flex items-center justify-between">
          <Link to={`/assignments/${assignmentId}`}
            className="flex items-center gap-2 text-xs font-semibold text-gray-500 hover:text-gray-800">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Assignment
          </Link>
          <p className="text-xs font-black uppercase tracking-widest text-gray-400">Submit Work</p>
          <div className="w-16" />
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-6 py-10 space-y-6">

        {/* Assignment header */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            {assignment.assignment_type === 'webdev'
              ? <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-violet-100 text-violet-700">🌐 Web Dev Project</span>
              : <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-slate-100 text-slate-700">📝 Standard</span>}
            {overdue && <span className="text-xs font-bold px-2.5 py-1 rounded-full bg-red-100 text-red-600">Past Due</span>}
          </div>
          <h1 className="text-2xl font-black text-gray-900 tracking-tight">{assignment.title}</h1>
          <p className="text-sm text-gray-500 mt-1">Due {fmtDate(assignment.due_date)}</p>
        </div>

        {/* Overdue warning */}
        {overdue && (
          <div className="px-5 py-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 font-medium">
            ⚠️ This assignment is past its deadline. Late submissions may not be accepted.
          </div>
        )}

        {/* Errors / info */}
        {error && (
          <div className="px-5 py-4 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700 font-medium">
            {error}
          </div>
        )}
        {dragInfo && !error && (
          <div className="px-5 py-4 rounded-xl bg-amber-50 border border-amber-200 text-sm text-amber-700 font-medium">
            ℹ️ {dragInfo}
          </div>
        )}

        {/* Mode info cards */}
        <div className="grid grid-cols-2 gap-3">
          <InfoCard icon="📤" title="Submission type" value={modeConfig.label}
            sub={modeConfig.allowZip && modeConfig.allowFiles ? 'Your choice' : undefined}
            color={modeConfig.allowZip && !modeConfig.allowFiles ? 'blue' : 'gray'} />
          <InfoCard icon="🗓️" title="Due" value={fmtDate(assignment.due_date)}
            color={overdue ? 'amber' : 'gray'} />
          {assignment.allowed_extensions && modeConfig.allowFiles && (
            <InfoCard icon="📎" title="Allowed extensions" value={assignment.allowed_extensions}
              sub="Same-language files are compared against each other" color="gray" />
          )}
          <InfoCard icon="📏" title="Max size"
            value={`${modeConfig.allowZip ? '200 MB (ZIP)' : `${assignment.max_file_size_mb || 10} MB`}`}
            color="gray" />
        </div>

        {/* Submission type explainer */}
        {modeConfig.allowZip && modeConfig.allowFiles && (
          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200">
              <p className="text-xs font-black uppercase tracking-widest text-slate-500 mb-1">Individual Files</p>
              <p className="text-sm text-slate-700 font-medium">Upload your source files directly ({assignment.allowed_extensions})</p>
            </div>
            <div className="p-4 rounded-xl bg-violet-50 border border-violet-200">
              <p className="text-xs font-black uppercase tracking-widest text-violet-500 mb-1">ZIP Archive</p>
              <p className="text-sm text-violet-700 font-medium">Upload a .zip of your project folder (max 200 MB)</p>
            </div>
          </div>
        )}

        {/* Drop zone */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <DropZone modeConfig={modeConfig} onChange={handleFileChange} hasFiles={hasFiles} />

          {/* ZIP notice */}
          {hasZip && (
            <div className="px-5 py-4 rounded-xl bg-violet-50 border border-violet-200 text-sm text-violet-800">
              <span className="font-bold">📦 ZIP detected.</span> All source files inside your archive will be
              extracted and analyzed. Files are grouped by language — each language pool is checked independently.
              Make sure your ZIP contains only your own code.
            </div>
          )}

          {/* Language grouping note for code files */}
          {!hasZip && hasFiles && Object.keys(langGroups).length > 0 && (
            <div className="px-5 py-4 rounded-xl bg-blue-50 border border-blue-200 text-sm text-blue-800">
              <span className="font-bold">🔍 Detection note:</span> Files are analyzed within their own language group.{' '}
              {Object.entries(langGroups).map(([lang, count]) => (
                <span key={lang} className="font-semibold">{count} {lang} file{count > 1 ? 's' : ''}</span>
              )).reduce((acc, el, i) => i === 0 ? [el] : [...acc, ', ', el], [])}
              {' '}will be compared against other students' same-language submissions.
            </div>
          )}

          {/* File list */}
          {hasFiles && (
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <p className="text-sm font-bold text-gray-900">
                  {files.length} file{files.length !== 1 ? 's' : ''} selected
                </p>
                <button type="button" onClick={() => { setFiles([]); setDragInfo(''); }}
                  className="text-xs text-red-500 hover:text-red-700 font-semibold">
                  Clear all
                </button>
              </div>
              {files.map((f, i) => <FileRow key={i} file={f} onRemove={() => removeFile(i)} />)}
            </div>
          )}

          {/* Submit button */}
          <div className="flex gap-3 pt-2">
            <Link to={`/assignments/${assignmentId}`}
              className="flex-1 py-3.5 rounded-xl border border-gray-200 text-sm font-bold text-gray-600 text-center hover:bg-gray-50 transition-colors">
              Cancel
            </Link>
            <button type="submit" disabled={uploading || !hasFiles}
              className="flex-[2] py-3.5 rounded-xl text-sm font-black bg-slate-900 text-white hover:bg-slate-700
                         shadow-lg shadow-slate-200 disabled:opacity-40 disabled:cursor-not-allowed transition-all">
              {uploading ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {hasZip ? 'Uploading & Extracting…' : 'Uploading…'}
                </span>
              ) : `Submit ${modeConfig.label}`}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SubmitWork;
