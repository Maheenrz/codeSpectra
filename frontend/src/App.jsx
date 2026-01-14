// import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
// import { AuthProvider } from './contexts/AuthContext'
// import Layout from './Components/Layout/Layout.jsx'
// import Login from './pages/auth/Login'
// import Register from './pages/auth/Register'
// import Dashboard from './pages/Dashboard'
// import Courses from './pages/Courses'
// import Assignments from './pages/Assignments'
// import Submissions from './pages/Submissions'
// import Analysis from './pages/Analysis'
// import Reports from './pages/Reports'

// function App() {
//   return (
//     <Router>  {/* ✅ Router must be the outermost */}
//       <AuthProvider>  {/* ✅ AuthProvider inside Router */}
//         <Routes>
//           <Route path="/login" element={<Login />} />
//           <Route path="/register" element={<Register />} />
          
//           <Route path="/" element={<Layout />}>
//             <Route index element={<Navigate to="/dashboard" />} />
//             <Route path="dashboard" element={<Dashboard />} />
//             <Route path="courses" element={<Courses />} />
//             <Route path="assignments" element={<Assignments />} />
//             <Route path="submissions" element={<Submissions />} />
//             <Route path="analysis" element={<Analysis />} />
//             <Route path="reports" element={<Reports />} />
//           </Route>
//         </Routes>
//       </AuthProvider>
//     </Router>
//   )
// }

// export default App



import React, { useState } from 'react';
import Type1Detector from './Components/Type1Detector';
import BatchTester from './Components/BatchTester';

function App() {
  const [activeTab, setActiveTab] = useState('type3'); // Default to Type 3

  return (
    <div>
      {/* Navigation Bar */}
      <nav style={{ background: '#333', padding: '15px', display: 'flex', justifyContent: 'center', gap: '20px' }}>
        <button 
          onClick={() => setActiveTab('type1')}
          style={{ 
            background: activeTab === 'type1' ? '#667eea' : 'transparent', 
            color: 'white', border: '1px solid white', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer' 
          }}
        >
          Type 1 (Exact Match)
        </button>
        <button 
          onClick={() => setActiveTab('type3')}
          style={{ 
            background: activeTab === 'type3' ? '#667eea' : 'transparent', 
            color: 'white', border: '1px solid white', padding: '8px 20px', borderRadius: '20px', cursor: 'pointer' 
          }}
        >
          Type 3 (Batch & Logic)
        </button>
      </nav>

      {/* Page Content */}
      <div style={{ background: '#f4f4f4', minHeight: 'calc(100vh - 60px)' }}>
        {activeTab === 'type1' ? <Type1Detector /> : <BatchTester />}
      </div>
    </div>
  );
}

export default App;