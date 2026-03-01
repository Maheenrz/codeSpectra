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
    if (assignmentId) {
      fetchAssignment();
    }
  }, [assignmentId]);

  const fetchAssignment = async () => {
    try {
      const data = await assignmentService.getAssignmentById(assignmentId);
      setAssignment(data);
    } catch (error) {
      console.error('Error fetching assignment:', error);
      setError('Failed to load assignment details');
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Validate file extensions
    const allowedExtensions = assignment?.allowed_extensions?.split(',') || [];
    const invalidFiles = selectedFiles.filter(file => {
      const ext = '.' + file.name.split('.').pop().toLowerCase();
      return !allowedExtensions.includes(ext);
    });

    if (invalidFiles.length > 0) {
      setError(`Invalid file type. Allowed: ${assignment.allowed_extensions}`);
      return;
    }

    // Validate file size
    const maxSize = (assignment?.max_file_size_mb || 10) * 1024 * 1024;
    const oversizedFiles = selectedFiles.filter(file => file.size > maxSize);

    if (oversizedFiles.length > 0) {
      setError(`File size exceeds ${assignment.max_file_size_mb}MB limit`);
      return;
    }

    setFiles(selectedFiles);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please select at least one file');
      return;
    }

    setUploading(true);
    setError('');

    try {
      const formData = new FormData();
      formData.append('assignmentId', assignmentId);
      files.forEach(file => {
        formData.append('files', file);
      });

      const result = await submissionService.createSubmission(formData);
      navigate(`/submissions/${result.submission.submission_id}`);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit assignment');
    } finally {
      setUploading(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!assignment) return <div>Assignment not found</div>;

  const isPastDue = new Date(assignment.due_date) < new Date();

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-4xl mx-auto px-6 py-6">
          <Link 
            to={`/assignments/${assignmentId}`}
            className="text-purple-600 hover:text-purple-700 mb-4 inline-block"
          >
            ← Back to Assignment
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Submit Assignment</h1>
          <p className="text-gray-600 mt-2">{assignment.title}</p>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {isPastDue && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            ⚠️ This assignment is past due. Late submissions may receive penalties.
          </div>
        )}

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 text-red-700 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <Card>
            <h2 className="text-xl font-bold text-gray-900 mb-4">Upload Files</h2>
            
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
              <svg className="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              
              <label className="cursor-pointer">
                <span className="btn-primary inline-block">
                  Choose Files
                </span>
                <input
                  type="file"
                  multiple
                  onChange={handleFileChange}
                  className="hidden"
                  accept={assignment.allowed_extensions}
                />
              </label>
              
              <p className="text-gray-600 mt-4">
                or drag and drop files here
              </p>
              <p className="text-sm text-gray-500 mt-2">
                Allowed: {assignment.allowed_extensions} • Max: {assignment.max_file_size_mb}MB per file
              </p>
            </div>

            {files.length > 0 && (
              <div className="mt-6">
                <h3 className="font-semibold text-gray-900 mb-3">Selected Files ({files.length})</h3>
                <div className="space-y-2">
                  {files.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <svg className="w-5 h-5 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                        </svg>
                        <div>
                          <p className="font-medium text-gray-900">{file.name}</p>
                          <p className="text-sm text-gray-600">{(file.size / 1024).toFixed(2)} KB</p>
                        </div>
                      </div>
                      <button
                        type="button"
                        onClick={() => setFiles(files.filter((_, i) => i !== index))}
                        className="text-red-600 hover:text-red-700"
                      >
                        <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>

          <div className="flex justify-end gap-4">
            <Link to={`/assignments/${assignmentId}`} className="btn-secondary">
              Cancel
            </Link>
            <button
              type="submit"
              disabled={uploading || files.length === 0}
              className="btn-primary disabled:bg-gray-400"
            >
              {uploading ? 'Uploading...' : 'Submit Assignment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SubmitAssignment;