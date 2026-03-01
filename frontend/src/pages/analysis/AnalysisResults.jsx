import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import analysisService from '../../services/analysisService';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import Card from '../../components/common/Card';

const AnalysisResults = () => {
  const { assignmentId } = useParams();
  const [results, setResults] = useState(null);
  const [threshold, setThreshold] = useState(70);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchResults();
  }, [assignmentId, threshold]);

  const fetchResults = async () => {
    try {
      const data = await analysisService.getAssignmentResults(assignmentId, threshold);
      setResults(data);
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <LoadingSpinner message="Loading analysis results..." />;

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <Link to={`/assignments/${assignmentId}`} className="text-purple-600 hover:text-purple-700 mb-4 inline-block">
            ← Back to Assignment
          </Link>
          <h1 className="text-3xl font-bold text-gray-900">Plagiarism Analysis Results</h1>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {/* Threshold Filter */}
        <Card className="mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-bold text-gray-900 mb-1">Similarity Threshold</h3>
              <p className="text-sm text-gray-600">Show pairs with similarity above</p>
            </div>
            <div className="flex items-center gap-4">
              <input
                type="range"
                min="0"
                max="100"
                value={threshold}
                onChange={(e) => setThreshold(e.target.value)}
                className="w-64"
              />
              <span className="text-2xl font-bold text-purple-600 w-20">{threshold}%</span>
            </div>
          </div>
        </Card>

        {/* High Similarity Pairs */}
        <Card>
          <h2 className="text-xl font-bold text-gray-900 mb-6">
            High Similarity Pairs ({results?.highSimilarityPairs?.length || 0})
          </h2>

          {!results?.highSimilarityPairs || results.highSimilarityPairs.length === 0 ? (
            <p className="text-gray-500 text-center py-8">No high similarity pairs found</p>
          ) : (
            <div className="space-y-4">
              {results.highSimilarityPairs.map((pair, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <span className="font-semibold text-gray-900">{pair.student_a_name}</span>
                        <span className="text-gray-400">↔</span>
                        <span className="font-semibold text-gray-900">{pair.student_b_name}</span>
                      </div>
                      <p className="text-sm text-gray-600">Clone Type: {pair.clone_type}</p>
                    </div>
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${
                        pair.similarity >= 85 ? 'text-red-600' :
                        pair.similarity >= 70 ? 'text-orange-600' :
                        'text-yellow-600'
                      }`}>
                        {pair.similarity.toFixed(1)}%
                      </div>
                      <p className="text-sm text-gray-600">similarity</p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Link 
                      to={`/submissions/${pair.submission_a_id}`}
                      className="btn-secondary text-sm py-2"
                    >
                      View Submission A
                    </Link>
                    <Link 
                      to={`/submissions/${pair.submission_b_id}`}
                      className="btn-secondary text-sm py-2"
                    >
                      View Submission B
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
};

export default AnalysisResults;