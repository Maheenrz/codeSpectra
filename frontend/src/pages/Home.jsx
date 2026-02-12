import React from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  return (
    <div className="home-page">
      <section className="hero">
        <div className="hero-content">
          <h1>🔍 CodeSpectra</h1>
          <p className="hero-subtitle">
            Advanced Code Similarity Analysis for Academic Integrity
          </p>
          <p className="hero-description">
            Detect code clones using structural and semantic analysis. 
            Perfect for educators managing programming assignments.
          </p>
          
          <div className="hero-actions">
            <Link to="/teacher" className="btn btn-primary btn-lg">
              👨‍🏫 Teacher Dashboard
            </Link>
          </div>
        </div>
      </section>

      <section className="features">
        <h2>How It Works</h2>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">📝</div>
            <h3>1. Create Assignment</h3>
            <p>
              Teacher creates an assignment with multiple problems. 
              Define the number of problems and their names.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📤</div>
            <h3>2. Students Submit</h3>
            <p>
              Share the unique code with students. They upload their 
              solution files for each problem.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🔬</div>
            <h3>3. Analyze</h3>
            <p>
              Run similarity analysis on all submissions. Get detailed 
              reports grouped by problem.
            </p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>4. Review Results</h3>
            <p>
              View similarity scores, outlier pairs, and detailed 
              comparisons for review.
            </p>
          </div>
        </div>
      </section>

      <section className="student-section">
        <h2>For Students</h2>
        <p>Have an assignment code from your teacher?</p>
        
        <div className="code-entry-box">
          <StudentCodeEntry />
        </div>
      </section>
    </div>
  );
};

// Student code entry component
const StudentCodeEntry = () => {
  const [code, setCode] = React.useState('');
  const [error, setError] = React.useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (code.trim().length !== 6) {
      setError('Please enter a valid 6-character code');
      return;
    }
    window.location.href = `/submit/${code.toUpperCase()}`;
  };

  return (
    <form onSubmit={handleSubmit} className="code-entry-form">
      <div className="input-group">
        <input
          type="text"
          value={code}
          onChange={(e) => {
            setCode(e.target.value.toUpperCase());
            setError('');
          }}
          placeholder="Enter Assignment Code"
          maxLength={6}
          className="code-input"
        />
        <button type="submit" className="btn btn-primary">
          Go →
        </button>
      </div>
      {error && <p className="error-text">{error}</p>}
    </form>
  );
};

export default Home;