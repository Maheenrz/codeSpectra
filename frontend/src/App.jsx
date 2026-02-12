import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AssignmentProvider } from './contexts/AssignmentContext';

// Pages
import Home from './pages/Home';
import TeacherDashboard from './pages/TeacherDashboard';
import CreateAssignment from './pages/CreateAssignment';
import StudentSubmission from './pages/StudentSubmission';
import AssignmentResults from './pages/AssignmentResults';
import NotFound from './pages/NotFound';

// Components
import Navbar from './Components/Navbar';
import Footer from './Components/Footer';

function App() {
  return (
    <AssignmentProvider>
      <Router>
        <div className="app">
          <Navbar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/teacher" element={<TeacherDashboard />} />
              <Route path="/teacher/create" element={<CreateAssignment />} />
              <Route path="/teacher/results/:assignmentId" element={<AssignmentResults />} />
              <Route path="/submit/:assignmentCode" element={<StudentSubmission />} />
              <Route path="*" element={<NotFound />} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </AssignmentProvider>
  );
}

export default App;