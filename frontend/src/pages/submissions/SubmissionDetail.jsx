import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import submissionService from '../../services/submissionService';
import analysisService from '../../services/analysisService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Card from '../../components/common/Card';

const SubmissionDetail = () => {
  const { submissionId } = useParams();
  const { isInstructor } = useAuth();
  const [submission, setSubmission] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSubmissionData();
  }, [submissionId]);

  const fetchSubmissionData = async () => {
    try {
      const submissionData = await submissionService.getSubmissionById(submissionId);
      setSubmission(submissionData);

      if (submissionData.analysis_status === 'completed') {
        try {
          const resultsData = await analysisService.getSubmissionResults(submissionId);
          setAnalysisResults(resultsData);
        } catch (err) {
          console.log('No analysis results yet');
        }
      }
    } catch (error) {
      console.error('Error fetching submission:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading submission..." />;
  if (!submission) return <div>Submission not found</div>;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <Link 
            to={`/assignments/${submission.assignment_id}`}
            className="text-purple-600 hover:text-purple-700 mb-4 inline-block"
          >
            ← Back to Assignment
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">{submission.assignment_title}</h1>
          <p className="text-gray-600 mt-1">
            Submitted by {submission.student_name} on {new Date(submission.submitted_at).toLocaleString()}
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Files */}
            <Card>
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                Submitted Files ({submission.files?.length || 0})
              </h2>
              <div className="space-y-2">
                {submission.files?.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                      </svg>
                      <div>
                        <p className="font-medium text-gray-900">{file.filename}</p>
                        <p className="text-sm text-gray-600">{(file.file_size / 1024).toFixed(2)} KB</p>
                      </div>
                    </div>
                    <a 
                      href={`http://localhost:3000${file.file_path}`}
                      download
                      className="text-purple-600 hover:text-purple-700 font-semibold"
                    >
                      Download
                    </a>
                  </div>
                ))}
              </div>
            </Card>

            {/* Analysis Results */}
            {analysisResults && (
              <Card>
                <h2 className="text-xl font-bold text-gray-900 mb-4">Analysis Results</h2>
                
                <div className="mb-6">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Overall Similarity</span>
                    <span className="text-3xl font-bold text-purple-600">
                      {analysisResults.overall_similarity?.toFixed(1)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4">
                    <div 
                      className={`h-4 rounded-full ${
                        analysisResults.overall_similarity >= 85 ? 'bg-red-600' :
                        analysisResults.overall_similarity >= 70 ? 'bg-orange-600' :
                        'bg-green-600'
                      }`}
                      style={{ width: `${analysisResults.overall_similarity}%` }}
                    ></div>
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Type-1</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {analysisResults.type1_score?.toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Type-2</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {analysisResults.type2_score?.toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Type-3</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {analysisResults.type3_score?.toFixed(1)}%
                    </p>
                  </div>
                  <div className="text-center p-4 bg-gray-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-1">Type-4</p>
                    <p className="text-2xl font-bold text-purple-600">
                      {analysisResults.type4_score?.toFixed(1)}%
                    </p>
                  </div>
                </div>

                {analysisResults.clonePairs?.length > 0 && (
                  <div className="mt-6">
                    <h3 className="font-bold text-gray-900 mb-3">Similar Submissions</h3>
                    <div className="space-y-2">
                      {analysisResults.clonePairs.map((pair, index) => (
                        <div key={index} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <div>
                            <p className="font-medium text-gray-900">{pair.student_b_name}</p>
                            <p className="text-sm text-gray-600">{pair.clone_type} clone</p>
                          </div>
                          <div className="text-right">
                            <p className="text-lg font-bold text-purple-600">
                              {pair.similarity?.toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <h3 className="font-bold text-gray-900 mb-4">Status</h3>
              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Analysis Status</p>
                  <span className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${
                    submission.analysis_status === 'completed' ? 'bg-green-100 text-green-700' :
                    submission.analysis_status === 'processing' ? 'bg-blue-100 text-blue-700' :
                    submission.analysis_status === 'failed' ? 'bg-red-100 text-red-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {submission.analysis_status}
                  </span>
                </div>
                {submission.analyzed_at && (
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Analyzed At</p>
                    <p className="font-medium text-gray-900">
                      {new Date(submission.analyzed_at).toLocaleString()}
                    </p>
                  </div>
                )}
              </div>
            </Card>

            <Card>
              <h3 className="font-bold text-gray-900 mb-4">Course Info</h3>
              <div className="space-y-2 text-sm">
                <div>
                  <p className="text-gray-600">Course</p>
                  <p className="font-medium text-gray-900">{submission.course_name}</p>
                </div>
                <div>
                  <p className="text-gray-600">Code</p>
                  <p className="font-medium text-gray-900">{submission.course_code}</p>
                </div>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SubmissionDetail;