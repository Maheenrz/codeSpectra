import React, { useState, useEffect } from 'react';
import { Link, useSearchParams, useNavigate } from 'react-router-dom';
import assignmentService from '../../services/assignmentService';
import submissionService from '../../services/submissionService';
import Card from '../../components/common/Card';

const SubmitAssignment = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const assignmentId = searchParams.get('assignmentId');

  const [assignment, setAssignment] = useState(null);
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (assignmentId) fetchAssignment();
  }, [assignmentId]);

  const fetchAssignment = async () => {
    try {
      const data = await assignmentService.getAssignmentById(assignmentId);
      setAssignment(data);
    } catch {
      setError('Failed to load assignment details');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selected = Array.from(e.target.files);
    const codeExts = ['.cpp','.c','.h','.hpp','.cc','.cxx','.java','.py','.js','.jsx','.ts','.tsx'];

    for (const file of selected) {
      const ext = '.' + file.name.split('.').pop().toLowerCase();

      // Zip is always allowed
      if (ext === '.zip') {
        if (file.size > 100 * 1024 * 1024) {
          setError(`${file.name} exceeds 100MB zip limit`);
          return;
        }
        continue;
      }

      // Code files: check against assignment extensions
      const allowed = assignment?.allowed_extensions?.split(',').map(e => e.trim()) || codeExts;
      if (!allowed.includes(ext)) {
        setError(`"${file.name}" not allowed. Accepted: ${allowed.join(', ')} or .zip`);
        return;
      }

      const maxSize = (assignment?.max_file_size_mb || 10) * 1024 * 1024;
      if (file.size > maxSize) {
        setError(`"${file.name}" exceeds ${assignment?.max_file_size_mb || 10}MB limit`);
        return;
      }
    }

    setFiles(selected);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) { setError('Please select at least one file'); return; }

    setUploading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('assignmentId', assignmentId);
      files.forEach(file => formData.append('files', file));
      const result = await submissionService.createSubmission(formData);
      navigate(`/submissions/${result.submission.submission_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit assignment');
    } finally {
      setUploading(false);
    }
  };

  const isZip = (file) => file.name.endsWith('.zip');
  const formatSize = (bytes) => bytes > 1024*1024
    ? `${(bytes/1024/1024).toFixed(1)} MB`
    : `${(bytes/1024).toFixed(1)} KB`;

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!assignment) return <div>Assignment not found</div>;

  const isPastDue = new Date(assignment.due_date) < new Date();
  const hasZip = files.some(isZip);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <Link to={`/assignments/${assignmentId}`} className="text-purple-600 hover:text-purple-700 mb-4 inline-block">
            ← Back to Assignment
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Submit Assignment</h1>
          <p className="text-gray-600 mt-2">{assignment.title}</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {isPastDue && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            ⚠️ This assignment is past due.
          </div>
        )}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">

          {/* Submission type info */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="font-semibold text-blue-900 mb-1">📄 Individual Files</p>
              <p className="text-sm text-blue-700">
                Upload your .cpp, .java, .py files directly.
                Accepted: {assignment.allowed_extensions}
              </p>
            </div>
            <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
              <p className="font-semibold text-purple-900 mb-1">📦 ZIP Folder</p>
              <p className="text-sm text-purple-700">
                Upload a .zip of your project folder. All code files inside will be extracted automatically. Max 100MB.
              </p>
            </div>
          </div>

          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Your Submission</h2>

            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-purple-400 transition-colors">
              <div className="text-5xl mb-4">📁</div>
              <label className="cursor-pointer">
                <span className="btn-primary inline-block">Choose Files or ZIP</span>
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                  accept=".cpp,.c,.h,.hpp,.cc,.cxx,.java,.py,.js,.jsx,.ts,.tsx,.zip"
                />
              </label>
              <p className="text-gray-500 text-sm mt-4">
                Individual code files <strong>or</strong> a .zip folder of your project
              </p>
            </div>

            {/* ZIP warning */}
            {hasZip && (
              <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-sm text-yellow-800">
                  📦 <strong>ZIP detected:</strong> All code files inside your zip will be extracted and analyzed. Make sure your zip contains only your own code.
                </p>
              </div>
            )}

            {/* Selected files list */}
            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold text-gray-900 mb-3">
                  Selected ({files.length} file{files.length !== 1 ? 's' : ''})
                </h3>
                <div className="space-y-2">
                  {files.map((file, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{isZip(file) ? '📦' : '📄'}</span>
                        <div>
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-xs text-gray-500">
                            {formatSize(file.size)}
                            {isZip(file) && ' · Will be extracted automatically'}
                          </p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setFiles(files.filter((_, idx) => idx !== i))}
                        className="text-red-500 hover:text-red-700 text-sm font-medium"
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>

          <div className="flex justify-end gap-4">
            <Link to={`/assignments/${assignmentId}`} className="btn-secondary">Cancel</Link>
            <button
              type="submit"
              disabled={uploading || files.length === 0}
              className="btn-primary disabled:bg-gray-400"
            >
              {uploading ? (
                <span className="flex items-center gap-2">
                  <svg className="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
                  </svg>
                  {hasZip ? 'Uploading & Extracting...' : 'Uploading...'}
                </span>
              ) : 'Submit Assignment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SubmitAssignment;