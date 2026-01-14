import React, { useState } from 'react';
import axios from 'axios';
import CodeViewer from './CodeViewer'; // Ensure you have created this component as discussed!

const BatchTester = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  
  // State for the Side-by-Side Viewer
  const [viewerData, setViewerData] = useState(null);

  const handleSubmit = async () => {
    if (files.length < 2) return alert("Please select at least 2 files");

    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    setLoading(true);
    try {
      const res = await axios.post('http://localhost:3000/api/test/batch-check', formData);
      setReport(res.data);
    } catch (err) {
      alert("Analysis failed. Is Python & Node running?");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Function to open the diff viewer
  const handleViewClone = async (fileNameA, fileNameB) => {
    const fileObjA = Array.from(files).find(f => f.name === fileNameA);
    const fileObjB = Array.from(files).find(f => f.name === fileNameB);

    if (fileObjA && fileObjB) {
      const contentA = await fileObjA.text();
      const contentB = await fileObjB.text();

      setViewerData({
        fileA: fileNameA,
        fileB: fileNameB,
        contentA,
        contentB
      });
    }
  };

  return (
    <div className="p-10 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-indigo-600">Type-3 Hybrid Analysis (AST + Tokens)</h1>
      
      {/* Upload Box */}
      <div className="bg-white p-8 rounded-xl shadow-md border-2 border-dashed border-gray-300 text-center">
        <input 
          type="file" multiple 
          onChange={(e) => setFiles(e.target.files)} 
          className="hidden" 
          id="fileUpload"
        />
        <label htmlFor="fileUpload" className="cursor-pointer text-blue-600 font-semibold text-lg hover:underline">
          Click to Select Files (Assignments)
        </label>
        <p className="text-gray-500 mt-2">{files.length} files selected</p>
        
        <button 
          onClick={handleSubmit} 
          disabled={loading || files.length < 2}
          className={`mt-6 px-8 py-3 rounded-lg text-white font-bold ${loading ? 'bg-gray-400' : 'bg-indigo-600 hover:bg-indigo-700'}`}
        >
          {loading ? 'Running Hybrid Detection (AST)...' : 'Run Batch Analysis'}
        </button>
      </div>

      {/* Results */}
      {report && (
        <div className="mt-10">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Analysis Report</h2>
            <div className="bg-blue-100 text-blue-800 px-4 py-2 rounded-lg">
              {report.suspicious_pairs} Clones Found / {report.comparisons_made || report.results.length} Comparisons
            </div>
          </div>

          <div className="bg-white shadow rounded-lg overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student A</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Student B</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Hybrid Score</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Action</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {report.results.map((item, idx) => (
                  <tr key={idx} className={item.is_clone ? "bg-red-50" : ""}>
                    <td className="px-6 py-4 font-medium text-sm">{item.file_a}</td>
                    <td className="px-6 py-4 font-medium text-sm">{item.file_b}</td>
                    
                    {/* The Breakdown Column */}
                    <td className="px-6 py-4">
                      <div className="font-bold text-gray-800 text-lg">
                        {(item.score * 100).toFixed(1)}%
                      </div>
                      <div className="text-xs text-gray-500 mt-1 space-y-1">
                        <div>🔤 Tokens: <span className="font-medium">{(item.details.token_score * 100).toFixed(0)}%</span></div>
                        <div>📊 Metrics: <span className="font-medium">{(item.details.metric_score * 100).toFixed(0)}%</span></div>
                        {/* New AST Display */}
                        <div>🌳 Structure (AST): <span className={`font-bold ${item.details.ast_score < 0.6 ? 'text-green-600' : 'text-red-600'}`}>
                          {(item.details.ast_score * 100).toFixed(0)}%
                        </span></div>
                      </div>
                    </td>

                    <td className="px-6 py-4">
                      {item.is_clone ? (
                        <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full font-bold">CLONE</span>
                      ) : (
                        <span className="bg-yellow-100 text-yellow-800 text-xs px-2 py-1 rounded-full font-bold">SUSPICIOUS</span>
                      )}
                    </td>

                    {/* Action Button */}
                    <td className="px-6 py-4">
                      <button 
                        onClick={() => handleViewClone(item.file_a, item.file_b)}
                        className="bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 px-3 py-1 rounded text-sm font-medium shadow-sm"
                      >
                        View Code
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Render the Viewer Modal if data exists */}
      {viewerData && (
        <CodeViewer 
          fileA={viewerData.fileA}
          fileB={viewerData.fileB}
          contentA={viewerData.contentA}
          contentB={viewerData.contentB}
          onClose={() => setViewerData(null)}
        />
      )}
    </div>
  );
};

export default BatchTester;