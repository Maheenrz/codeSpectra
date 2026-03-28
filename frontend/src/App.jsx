import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./Components/common/ProtectedRoute";
import Navbar from "./Components/Navbar";

// Public Pages
import LandingPage from "./pages/LandingPage";
import Home from "./pages/Home";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

// Dashboard Pages
import StudentDashboard from "./pages/dashboard/StudentDashboard";
import InstructorDashboard from "./pages/dashboard/InstructorDashboard";

// Course Pages
import CourseList from "./pages/courses/CourseList";
import CourseDetail from "./pages/courses/CourseDetail";
import CreateCourse from "./pages/courses/CreateCourse";
import JoinCourse from "./pages/courses/JoinCourse";

// Assignment Pages
import AssignmentDetail from "./pages/assignments/AssignmentDetail";
import CreateAssignment from "./pages/assignments/CreateAssignment";
import EditAssignment from "./pages/assignments/EditAssignment";

// Submission Pages
import SubmitWork from "./pages/submissions/SubmitWork";
import SubmissionDetail from "./pages/submissions/SubmissionDetail";

// Analysis Pages
import AnalysisResults from "./pages/analysis/AnalysisResults";
import CodeAnalysis from "./pages/analysis/CodeAnalysis";
import ComparisonView from "./pages/analysis/ComparisonView";

import "./index.css";

// ── Hide navbar on the animated splash screen only ────────────────────────────
const HIDE_NAV = ["/"];

function AppLayout() {
  const location = useLocation();
  const hide = HIDE_NAV.includes(location.pathname);

  return (
    <>
      {!hide && <Navbar />}
      <Routes>
        {/* Public */}
        <Route path="/"         element={<LandingPage />} />
        <Route path="/home"     element={<Home />} />
        <Route path="/login"    element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Dashboard */}
        <Route path="/dashboard" element={
          <ProtectedRoute><DashboardRouter /></ProtectedRoute>
        } />

        {/* Courses */}
        <Route path="/courses" element={
          <ProtectedRoute><CourseList /></ProtectedRoute>
        } />
        <Route path="/courses/create" element={
          <ProtectedRoute allowedRoles={["instructor", "admin"]}><CreateCourse /></ProtectedRoute>
        } />
        <Route path="/courses/join" element={
          <ProtectedRoute allowedRoles={["student"]}><JoinCourse /></ProtectedRoute>
        } />
        <Route path="/courses/:courseId" element={
          <ProtectedRoute><CourseDetail /></ProtectedRoute>
        } />

        {/* Assignments */}
        <Route path="/assignments/create" element={
          <ProtectedRoute allowedRoles={["instructor", "admin"]}><CreateAssignment /></ProtectedRoute>
        } />
        <Route path="/assignments/edit/:assignmentId" element={
          <ProtectedRoute allowedRoles={["instructor", "admin"]}><EditAssignment /></ProtectedRoute>
        } />
        <Route path="/assignments/:assignmentId" element={
          <ProtectedRoute><AssignmentDetail /></ProtectedRoute>
        } />

        {/* Submissions */}
        <Route path="/submissions/submit" element={
          <ProtectedRoute allowedRoles={["student"]}><SubmitWork /></ProtectedRoute>
        } />
        <Route path="/submissions/:submissionId" element={
          <ProtectedRoute><SubmissionDetail /></ProtectedRoute>
        } />

        {/* Analysis — open to ALL authenticated users */}
        <Route path="/analysis/assignment/:assignmentId" element={
          <ProtectedRoute allowedRoles={["instructor", "admin"]}><AnalysisResults /></ProtectedRoute>
        } />
        <Route path="/analyze" element={
          <ProtectedRoute><CodeAnalysis /></ProtectedRoute>
        } />
        <Route path="/analysis/pair/:pairId" element={
          <ProtectedRoute><ComparisonView /></ProtectedRoute>
        } />

        {/* Catch-all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <AppLayout />
      </Router>
    </AuthProvider>
  );
}

const DashboardRouter = () => {
  const { user } = useAuth();
  return (user?.role === "instructor" || user?.role === "admin")
    ? <InstructorDashboard />
    : <StudentDashboard />;
};

export default App;
