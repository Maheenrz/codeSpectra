import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import assignmentService from '../../services/assignmentService';
import submissionService from '../../services/submissionService';

/* ── Helpers ── */
const EXT_LANG = {
  '.cpp':'C++','.c':'C','.h':'C/C++','.hpp':'C++','.cc':'C++','.cxx':'C++',
  '.java':'Java','.py':'Python',
  '.js':'JavaScript','.jsx':'JavaScript','.ts':'TypeScript','.tsx':'TypeScript',
  '.html':'HTML','.css':'CSS',
};
const LANG_COLORS = {
  'C++':'bg-blue-100 text-blue-700','C':'bg-sky-100 text-sky-700','C/C++':'bg-sky-100 text-sky-700',
  'Java':'bg-orange-100 text-orange-700','Python':'bg-yellow-100 text-yellow-700',
  'JavaScript':'bg-amber-100 text-amber-700','TypeScript':'bg-blue-100 text-blue-700',
  'HTML':'bg-red-100 text-red-700','CSS':'bg-purple-100 text-purple-700',
};
const getFileExt = (name) => '.' + name.split('.').pop().toLowerCase();
const isZip      = (name) => name.endsWith('.zip');
const fmtSize    = (b)    => b > 1048576 ? `${(b/1048576).toFixed(1)} MB` : `${(b/1024).toFixed(1)} KB`;
const fmtDate    = (d)    => new Date(d).toLocaleString('en-PK', { dateStyle:'medium', timeStyle:'short' });
const isPast     = (d)    => new Date(d) < new Date();

function getModeConfig(assignment) {
  const mode = assignment?.submission_mode || 'both';
  const isWebDev = assignment?.assignment_type === 'webdev';
  if (isWebDev) return { allowFiles:false, allowZip:true, label:'Project ZIP', hint:'Upload your entire project as a .zip file.', accept:'.zip' };
  if (mode === 'files') return { allowFiles:true, allowZip:false, label:'Code Files', hint:`Upload individual source files. Accepted: ${assignment?.allowed_extensions || 'any code file'}`, accept:(assignment?.allowed_extensions||'.cpp,.c,.h,.java,.py,.js,.ts') };
  if (mode === 'zip')   return { allowFiles:false, allowZip:true, label:'ZIP Archive', hint:'Upload all your files as a single .zip archive.', accept:'.zip' };
  return { allowFiles:true, allowZip:true, label:'Files or ZIP', hint:`Upload individual files (${assignment?.allowed_extensions}) or a .zip of your solution.`, accept:(assignment?.allowed_extensions||'.cpp,.c,.h,.java,.py,.js,.ts')+',.zip' };
}

/* ── SVG Icons ── */
const Ico = {
  ArrowLeft: () => (
    <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M19 12H5M12 5l-7 7 7 7"/>
    </svg>
  ),
  Upload: () => (
    <svg width="22" height="22" fill="none" stroke="#CF7249" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="16 16 12 12 8 16"/>
      <line x1="12" y1="12" x2="12" y2="21"/>
      <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/>
    </svg>
  ),
  UploadCloud: () => (
    <svg width="52" height="52" fill="none" stroke="#CF7249" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="16 16 12 12 8 16"/>
      <line x1="12" y1="12" x2="12" y2="21"/>
      <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/>
    </svg>
  ),
  Archive: () => (
    <svg width="52" height="52" fill="none" stroke="#CF7249" strokeWidth="1.2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polyline points="21 8 21 21 3 21 3 8"/>
      <rect x="1" y="3" width="22" height="5"/>
      <line x1="10" y1="12" x2="14" y2="12"/>
    </svg>
  ),
  FileCode: () => (
    <svg width="18" height="18" fill="none" stroke="#CF7249" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
      <polyline points="14 2 14 8 20 8"/>
      <polyline points="10 13 8 15 10 17"/>
      <polyline points="14 13 16 15 14 17"/>
    </svg>
  ),
  Box: () => (
    <svg width="18" height="18" fill="none" stroke="#8B5CF6" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M21 16V8a2 2 0 00-1-1.73l-7-4a2 2 0 00-2 0l-7 4A2 2 0 003 8v8a2 2 0 001 1.73l7 4a2 2 0 002 0l7-4A2 2 0 0021 16z"/>
      <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
      <line x1="12" y1="22.08" x2="12" y2="12"/>
    </svg>
  ),
  Calendar: () => (
    <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <rect x="3" y="4" width="18" height="18" rx="2"/>
      <line x1="16" y1="2" x2="16" y2="6"/>
      <line x1="8" y1="2" x2="8" y2="6"/>
      <line x1="3" y1="10" x2="21" y2="10"/>
    </svg>
  ),
  Layers: () => (
    <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <polygon points="12 2 2 7 12 12 22 7 12 2"/>
      <polyline points="2 17 12 22 22 17"/>
      <polyline points="2 12 12 17 22 12"/>
    </svg>
  ),
  Ruler: () => (
    <svg width="15" height="15" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M21.3 15.3a1 1 0 010 1.4l-2.6 2.6a1 1 0 01-1.4 0L2.7 4.7a1 1 0 010-1.4l2.6-2.6a1 1 0 011.4 0z"/>
      <path d="M7.5 7.5l3 3M11.5 11.5l3 3"/>
    </svg>
  ),
  X: () => (
    <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" viewBox="0 0 24 24">
      <line x1="18" y1="6" x2="6" y2="18"/>
      <line x1="6" y1="6" x2="18" y2="18"/>
    </svg>
  ),
  CheckCircle: () => (
    <svg width="16" height="16" fill="none" stroke="#059669" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/>
      <polyline points="22 4 12 14.01 9 11.01"/>
    </svg>
  ),
  AlertTriangle: () => (
    <svg width="16" height="16" fill="none" stroke="#D97706" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/>
      <line x1="12" y1="9" x2="12" y2="13"/>
      <line x1="12" y1="17" x2="12.01" y2="17"/>
    </svg>
  ),
  AlertCircle: () => (
    <svg width="16" height="16" fill="none" stroke="#DC2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="8" x2="12" y2="12"/>
      <line x1="12" y1="16" x2="12.01" y2="16"/>
    </svg>
  ),
  Info: () => (
    <svg width="16" height="16" fill="none" stroke="#2563EB" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10"/>
      <line x1="12" y1="16" x2="12" y2="12"/>
      <line x1="12" y1="8" x2="12.01" y2="8"/>
    </svg>
  ),
};

/* ── Reusable components ── */
const InfoCard = ({ icon, label, value, sub, accent = false }) => (
  <div className={`rounded-2xl px-5 py-4 border ${accent ? 'bg-[#FEF3EC] border-[#F4C9AA]' : 'bg-[#F7F3EE] border-[#E8E1D8]'}`}>
    <div className="flex items-center gap-2 mb-1.5">
      <span className="text-[#A8A29E]">{icon}</span>
      <span className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E]">{label}</span>
    </div>
    <p className={`font-black text-sm ${accent ? 'text-[#CF7249]' : 'text-[#1A1714]'}`}>{value}</p>
    {sub && <p className="text-xs text-[#A8A29E] mt-0.5">{sub}</p>}
  </div>
);

const FileRow = ({ file, onRemove }) => {
  const ext  = getFileExt(file.name);
  const lang = EXT_LANG[ext];
  const zip  = isZip(file.name);
  return (
    <div className="flex items-center gap-4 px-5 py-4 rounded-2xl bg-[#F7F3EE] border border-[#E8E1D8] group hover:border-[#CF7249]/30 transition-colors">
      <div className="w-10 h-10 rounded-xl bg-white border border-[#E8E1D8] flex items-center justify-center flex-shrink-0">
        {zip ? <Ico.Box /> : <Ico.FileCode />}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-bold text-[#1A1714] truncate">{file.name}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className="text-xs text-[#A8A29E]">{fmtSize(file.size)}</span>
          {lang && <span className={`text-[10px] font-black px-2 py-0.5 rounded-lg ${LANG_COLORS[lang] || 'bg-gray-100 text-gray-600'}`}>{lang}</span>}
          {zip  && <span className="text-[10px] font-black px-2 py-0.5 rounded-lg bg-purple-100 text-purple-700">ZIP</span>}
        </div>
      </div>
      <button
        type="button"
        onClick={onRemove}
        className="opacity-0 group-hover:opacity-100 w-8 h-8 rounded-lg flex items-center justify-center text-[#A8A29E] hover:text-red-500 hover:bg-red-50 transition-all"
      >
        <Ico.X />
      </button>
    </div>
  );
};

const DropZone = ({ modeConfig, onChange, hasFiles }) => {
  const [dragging, setDragging] = useState(false);
  const onDragOver  = (e) => { e.preventDefault(); setDragging(true); };
  const onDragLeave = ()  => setDragging(false);
  const onDrop      = (e) => { e.preventDefault(); setDragging(false); if (e.dataTransfer?.files?.length) onChange({ target: { files: e.dataTransfer.files } }); };

  return (
    <label
      onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}
      className={`block border-2 border-dashed rounded-3xl p-12 text-center cursor-pointer transition-all duration-200
        ${dragging
          ? 'border-[#CF7249] bg-[#FEF3EC]'
          : hasFiles
          ? 'border-emerald-300 bg-emerald-50/40'
          : 'border-[#E8E1D8] hover:border-[#CF7249]/50 hover:bg-[#FEF3EC]/40'}`}
    >
      <div className={`flex justify-center mb-5 transition-transform ${dragging ? 'scale-110' : ''}`}>
        {modeConfig.allowZip && !modeConfig.allowFiles ? <Ico.Archive /> : <Ico.UploadCloud />}
      </div>
      <p className="font-black text-[#1A1714] text-lg mb-1.5">
        {hasFiles ? 'Add more files' : 'Drop files here or click to browse'}
      </p>
      <p className="text-sm text-[#6B6560] mb-6 max-w-xs mx-auto leading-relaxed">{modeConfig.hint}</p>
      <span className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-[#CF7249] text-white text-sm font-black hover:bg-[#B85E38] transition-colors shadow-sm">
        <Ico.Upload /> Browse Files
      </span>
      <input type="file" multiple className="hidden" accept={modeConfig.accept} onChange={onChange} />
    </label>
  );
};

/* ── Main ── */
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
  const overdue    = assignment && isPast(assignment.due_date);
  const hasZip     = files.some(f => isZip(f.name));
  const hasFiles   = files.length > 0;

  const validateAndAdd = (incoming) => {
    setError('');
    const newFiles = [];
    for (const file of incoming) {
      const ext = getFileExt(file.name); const zipFile = isZip(file.name);
      const maxMB = assignment?.max_file_size_mb || 10;
      if (zipFile) {
        if (!modeConfig.allowZip) { setError('ZIP files are not allowed for this assignment.'); return; }
        if (file.size > 200 * 1024 * 1024) { setError(`${file.name} exceeds the 200 MB ZIP limit.`); return; }
        newFiles.push(file); continue;
      }
      if (!modeConfig.allowFiles) { setError('Please upload a .zip archive for this assignment.'); return; }
      const allowedExts = (assignment?.allowed_extensions || '').split(',').map(e => e.trim()).filter(Boolean);
      if (allowedExts.length && !allowedExts.includes(ext)) { setError(`"${file.name}" is not allowed. Accepted: ${allowedExts.join(', ')}`); return; }
      if (file.size > maxMB * 1024 * 1024) { setError(`"${file.name}" exceeds the ${maxMB} MB file limit.`); return; }
      newFiles.push(file);
    }
    const existingHasZip = files.some(f => isZip(f.name)); const newHasZip = newFiles.some(f => isZip(f.name));
    const existingHasCode = files.some(f => !isZip(f.name)); const newHasCode = newFiles.some(f => !isZip(f.name));
    if ((existingHasZip && newHasCode) || (existingHasCode && newHasZip)) { setError('Cannot mix ZIP files with individual code files.'); return; }
    const existingNames = new Set(files.map(f => f.name));
    const unique = newFiles.filter(f => !existingNames.has(f.name));
    if (unique.length < newFiles.length) setDragInfo(`${newFiles.length - unique.length} duplicate file(s) skipped.`);
    setFiles(prev => [...prev, ...unique]);
  };

  const handleFileChange = (e) => { const sel = Array.from(e.target.files || []); if (sel.length) validateAndAdd(sel); e.target.value = ''; };
  const removeFile = (i) => setFiles(prev => prev.filter((_, idx) => idx !== i));

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

  /* Language grouping */
  const langGroups = {};
  files.filter(f => !isZip(f.name)).forEach(f => {
    const lang = EXT_LANG[getFileExt(f.name)] || 'Other';
    langGroups[lang] = (langGroups[lang] || 0) + 1;
  });

  if (loading) return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#CF7249] border-t-transparent rounded-full animate-spin" />
    </div>
  );
  if (!assignment) return (
    <div className="min-h-screen bg-[#F7F3EE] flex items-center justify-center">
      <p className="text-[#6B6560]">Assignment not found.</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#F7F3EE]">

      {/* ── Breadcrumb bar ── */}
      <div className="bg-white/90 backdrop-blur-sm border-b border-[#E8E1D8] sticky top-16 z-40">
        <div className="max-w-2xl mx-auto px-6 py-3.5 flex items-center justify-between">
          <Link
            to={`/assignments/${assignmentId}`}
            className="inline-flex items-center gap-2 text-xs font-semibold text-[#A8A29E] hover:text-[#CF7249] transition-colors"
          >
            <Ico.ArrowLeft />
            Back to Assignment
          </Link>
          <span className="text-[10px] font-black uppercase tracking-widest text-[#A8A29E]">Submit Work</span>
          <div className="w-28" />
        </div>
      </div>

      <div className="max-w-2xl mx-auto px-6 py-10 space-y-8">

        {/* ── Big orange heading ── */}
        <div>
          <div className="flex flex-wrap items-center gap-2 mb-4">
            {assignment.assignment_type === 'webdev'
              ? <span className="text-xs font-black px-3 py-1 rounded-full bg-purple-100 text-purple-700">Web Dev Project</span>
              : <span className="text-xs font-black px-3 py-1 rounded-full bg-[#F0EBE3] text-[#6B6560]">Standard Assignment</span>}
            {overdue && <span className="text-xs font-black px-3 py-1 rounded-full bg-red-100 text-red-600">Past Due</span>}
          </div>
          <h1 className="text-4xl font-black text-[#CF7249] tracking-tight leading-tight">{assignment.title}</h1>
          <p className="text-sm text-[#A8A29E] mt-2 flex items-center gap-1.5">
            <Ico.Calendar /> Due {fmtDate(assignment.due_date)}
          </p>
        </div>

        {/* ── Overdue warning ── */}
        {overdue && (
          <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-red-50 border border-red-200 text-sm text-red-700 font-medium">
            <span className="flex-shrink-0 mt-0.5"><Ico.AlertTriangle /></span>
            This assignment is past its deadline. Late submissions may not be accepted.
          </div>
        )}

        {/* ── Alerts ── */}
        {error && (
          <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-red-50 border border-red-200 text-sm text-red-700 font-medium">
            <span className="flex-shrink-0 mt-0.5"><Ico.AlertCircle /></span>
            {error}
          </div>
        )}
        {dragInfo && !error && (
          <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-amber-50 border border-amber-200 text-sm text-amber-700 font-medium">
            <span className="flex-shrink-0 mt-0.5"><Ico.AlertTriangle /></span>
            {dragInfo}
          </div>
        )}

        {/* ── Info cards ── */}
        <div className="grid grid-cols-2 gap-3">
          <InfoCard icon={<Ico.Layers />}   label="Submission type" value={modeConfig.label} accent={modeConfig.allowZip && !modeConfig.allowFiles} />
          <InfoCard icon={<Ico.Calendar />} label="Due"             value={fmtDate(assignment.due_date)} accent={overdue} />
          {assignment.allowed_extensions && modeConfig.allowFiles && (
            <InfoCard icon={<Ico.FileCode />} label="Allowed extensions" value={assignment.allowed_extensions} sub="Per language pool" />
          )}
          <InfoCard icon={<Ico.Ruler />} label="Max size" value={modeConfig.allowZip ? '200 MB (ZIP)' : `${assignment.max_file_size_mb || 10} MB`} />
        </div>

        {/* ── Both-mode explainer ── */}
        {modeConfig.allowZip && modeConfig.allowFiles && (
          <div className="grid grid-cols-2 gap-3">
            <div className="p-5 rounded-2xl bg-[#F7F3EE] border border-[#E8E1D8]">
              <p className="text-xs font-black uppercase tracking-widest text-[#A8A29E] mb-2">Individual Files</p>
              <p className="text-sm text-[#6B6560] font-medium leading-relaxed">Upload source files directly ({assignment.allowed_extensions})</p>
            </div>
            <div className="p-5 rounded-2xl bg-purple-50 border border-purple-200">
              <p className="text-xs font-black uppercase tracking-widest text-purple-500 mb-2">ZIP Archive</p>
              <p className="text-sm text-purple-700 font-medium leading-relaxed">Upload a .zip of your project folder (max 200 MB)</p>
            </div>
          </div>
        )}

        {/* ── Upload form ── */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <DropZone modeConfig={modeConfig} onChange={handleFileChange} hasFiles={hasFiles} />

          {/* ZIP notice */}
          {hasZip && (
            <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-purple-50 border border-purple-200 text-sm text-purple-800 font-medium">
              <span className="flex-shrink-0 mt-0.5"><Ico.Info /></span>
              <span><strong>ZIP detected.</strong> All source files inside your archive will be extracted and analyzed per language group.</span>
            </div>
          )}

          {/* Language detection note */}
          {!hasZip && hasFiles && Object.keys(langGroups).length > 0 && (
            <div className="flex items-start gap-3 px-5 py-4 rounded-2xl bg-blue-50 border border-blue-200 text-sm text-blue-800 font-medium">
              <span className="flex-shrink-0 mt-0.5"><Ico.Info /></span>
              <span>
                Files are analyzed within their own language group.{' '}
                {Object.entries(langGroups).map(([lang, count]) => (
                  <span key={lang} className="font-black">{count} {lang}{count > 1 ? ' files' : ' file'}</span>
                )).reduce((acc, el, i) => i === 0 ? [el] : [...acc, ', ', el], [])}
                {' '}will be compared against other students' same-language submissions.
              </span>
            </div>
          )}

          {/* File list */}
          {hasFiles && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Ico.CheckCircle />
                  <p className="text-sm font-black text-[#1A1714]">
                    {files.length} file{files.length !== 1 ? 's' : ''} selected
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => { setFiles([]); setDragInfo(''); }}
                  className="text-xs font-black text-[#A8A29E] hover:text-red-500 transition-colors"
                >
                  Clear all
                </button>
              </div>
              {files.map((f, i) => <FileRow key={i} file={f} onRemove={() => removeFile(i)} />)}
            </div>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-2">
            <Link
              to={`/assignments/${assignmentId}`}
              className="flex-1 py-3.5 rounded-2xl border border-[#E8E1D8] bg-white text-sm font-black text-[#6B6560] text-center hover:bg-[#F7F3EE] transition-colors"
            >
              Cancel
            </Link>
            <button
              type="submit"
              disabled={uploading || !hasFiles}
              className="flex-[2] py-3.5 rounded-2xl text-sm font-black bg-[#CF7249] text-white hover:bg-[#B85E38] shadow-sm disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            >
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
