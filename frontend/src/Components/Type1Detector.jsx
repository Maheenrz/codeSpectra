import React, { useState } from 'react';

const Type1Detector = () => {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  // Styles object (converted from your CSS)
  const styles = {
    container: { maxWidth: '1200px', margin: '0 auto', background: 'white', borderRadius: '20px', padding: '40px', boxShadow: '0 20px 60px rgba(0,0,0,0.3)' },
    header: { textAlign: 'center', color: '#667eea', marginBottom: '10px', fontSize: '2.5em' },
    uploadSection: { border: '3px dashed #667eea', borderRadius: '15px', padding: '40px', textAlign: 'center', background: '#f8f9ff', cursor: 'pointer' },
    btn: { background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white', border: 'none', padding: '12px 30px', borderRadius: '25px', cursor: 'pointer', fontSize: '1em', marginTop: '20px' },
    badge: { padding: '4px 12px', borderRadius: '12px', fontSize: '0.85em', fontWeight: 'bold', color: 'white' }
  };

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const startAnalysis = async () => {
    if (files.length === 0) return;
    setLoading(true);

    const formData = new FormData();
    files.forEach(file => formData.append('files', file));

    try {
      // NOTE: Pointing to Python Engine directly for Type 1 as per your original code
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      alert("Analysis Failed! Is the Python Engine running on port 8000?");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', padding: '20px', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', fontFamily: 'Segoe UI, sans-serif' }}>
      <div style={styles.container}>
        <h1 style={styles.header}>🔍 CodeSpectra</h1>
        <p style={{ textAlign: 'center', color: '#666', marginBottom: '40px' }}>Type 1 Exact Match Detector</p>

        {/* Upload Area */}
        <div style={styles.uploadSection}>
          <div style={{ fontSize: '4em', marginBottom: '20px' }}>📁</div>
          <p>Drag & Drop files or click to browse</p>
          <input type="file" multiple onChange={handleFileChange} style={{ marginTop: '20px' }} />
        </div>

        {/* File List */}
        {files.length > 0 && (
          <div style={{ background: '#f8f9ff', padding: '15px', borderRadius: '10px', marginBottom: '20px' }}>
            <h4>📄 Selected Files ({files.length})</h4>
            <ul>
              {files.map((f, i) => <li key={i}>{f.name}</li>)}
            </ul>
          </div>
        )}

        <div style={{ textAlign: 'center' }}>
          <button 
            style={{ ...styles.btn, opacity: loading || files.length === 0 ? 0.5 : 1 }} 
            onClick={startAnalysis} 
            disabled={loading || files.length === 0}
          >
            {loading ? 'Analyzing...' : '🚀 Start Analysis'}
          </button>
        </div>

        {/* Results Area */}
        {results && (
          <div style={{ marginTop: '30px', borderTop: '2px solid #eee', paddingTop: '20px' }}>
            <h3 style={{ color: '#667eea' }}>📊 Analysis Results</h3>
            
            {/* Summary */}
            <div style={{ background: '#f8f9ff', padding: '20px', borderRadius: '10px', marginBottom: '20px' }}>
              <p><strong>Total Clones:</strong> {results.summary.total_clones}</p>
              <p><strong>Best Method:</strong> {results.summary.best_method}</p>
            </div>

            {/* Matches */}
            {results.matches.map((match, idx) => (
              <div key={idx} style={{ background: 'white', border: '1px solid #ddd', padding: '15px', margin: '10px 0', borderRadius: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <div>
                  <strong>{match.file1}</strong> vs <strong>{match.file2}</strong>
                </div>
                <span style={{ ...styles.badge, background: '#4caf50' }}>100% Match</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Type1Detector;