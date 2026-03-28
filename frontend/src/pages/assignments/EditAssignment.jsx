import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import assignmentService from '../../services/assignmentService';
import CreateAssignment from './CreateAssignment';
import PageLoader from '../../Components/common/PageLoader';

const NotFoundVector = () => (
  <svg width="110" height="110" viewBox="0 0 110 110" fill="none" xmlns="http://www.w3.org/2000/svg" className="mx-auto mb-6 opacity-50">
    <rect x="18" y="14" width="74" height="82" rx="9" stroke="#CF7249" strokeWidth="2.5" fill="#FEF3EC"/>
    <rect x="18" y="14" width="20" height="82" rx="6" fill="#FDEEDE" stroke="#CF7249" strokeWidth="2.5"/>
    <circle cx="28" cy="34" r="3" fill="#CF7249"/>
    <circle cx="28" cy="52" r="3" fill="#CF7249"/>
    <circle cx="28" cy="70" r="3" fill="#CF7249"/>
    <circle cx="28" cy="88" r="3" fill="#CF7249"/>
    <line x1="50" y1="42" x2="80" y2="42" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <line x1="50" y1="54" x2="74" y2="54" stroke="#E8D5C8" strokeWidth="2" strokeLinecap="round"/>
    <text x="54" y="86" fontFamily="Georgia, serif" fontSize="28" fontWeight="700" fill="#CF7249" opacity="0.35">?</text>
  </svg>
);

const EditAssignment = () => {
  const { assignmentId } = useParams();
  const [loading,     setLoading]     = useState(true);
  const [initialData, setInitialData] = useState(null);
  const [error,       setError]       = useState('');

  useEffect(() => {
    setLoading(true);
    assignmentService.getAssignmentById(assignmentId)
      .then(data => {
        if (!data) { setError('Assignment not found.'); return; }
        setInitialData(data);
      })
      .catch(() => setError('Failed to load assignment. Please try again.'))
      .finally(() => setLoading(false));
  }, [assignmentId]);

  if (loading) return <PageLoader message="Loading assignment…" />;

  if (error || !initialData) return (
    <div className="min-h-screen bg-[#F7F3EE] flex flex-col items-center justify-center gap-3 px-6 text-center">
      <NotFoundVector />
      <p className="text-xl font-bold text-[#1A1714]">{error || 'Assignment not found.'}</p>
      <p className="text-sm text-[#A8A29E] max-w-xs mt-1">
        The assignment may have been deleted or you may not have permission to edit it.
      </p>
      <Link to="/courses"
        className="mt-4 inline-flex items-center gap-1.5 text-sm font-semibold text-white bg-[#CF7249] px-6 py-3 rounded-xl hover:bg-[#B85E38] transition-colors">
        ← Back to Courses
      </Link>
    </div>
  );

  return (
    <CreateAssignment
      editMode
      initialData={initialData}
      assignmentId={assignmentId}
    />
  );
};

export default EditAssignment;
