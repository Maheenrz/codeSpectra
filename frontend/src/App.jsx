import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import ProtectedRoute from "./components/common/ProtectedRoute";
import JoinCourse from './pages/courses/JoinCourse';

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

// Assignment Pages
import AssignmentDetail from "./pages/assignments/AssignmentDetail";
import CreateAssignment from "./pages/assignments/CreateAssignment";

// Submission Pages
import SubmitAssignment from "./pages/submissions/SubmitAssignment";
import SubmissionDetail from "./pages/submissions/SubmissionDetail";

// Analysis Pages
import AnalysisResults from "./pages/analysis/AnalysisResults";

import "./index.css";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/home" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Dashboard */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardRouter />
              </ProtectedRoute>
            }
          />

          {/* Course Routes */}
          <Route
            path="/courses"
            element={
              <ProtectedRoute>
                <CourseList />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/create"
            element={
              <ProtectedRoute allowedRoles={["instructor", "admin"]}>
                <CreateCourse />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/join"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <JoinCourse />
              </ProtectedRoute>
            }
          />
          <Route
            path="/courses/:courseId"
            element={
              <ProtectedRoute>
                <CourseDetail />
              </ProtectedRoute>
            }
          />

          {/* Assignment Routes */}
          <Route
            path="/assignments/:assignmentId"
            element={
              <ProtectedRoute>
                <AssignmentDetail />
              </ProtectedRoute>
            }
          />
          <Route
            path="/assignments/create"
            element={
              <ProtectedRoute allowedRoles={["instructor", "admin"]}>
                <CreateAssignment />
              </ProtectedRoute>
            }
          />

          {/* Submission Routes */}
          <Route
            path="/submissions/submit"
            element={
              <ProtectedRoute allowedRoles={["student"]}>
                <SubmitAssignment />
              </ProtectedRoute>
            }
          />
          <Route
            path="/submissions/:submissionId"
            element={
              <ProtectedRoute>
                <SubmissionDetail />
              </ProtectedRoute>
            }
          />

          {/* Analysis Routes */}
          <Route
            path="/analysis/assignment/:assignmentId"
            element={
              <ProtectedRoute allowedRoles={["instructor", "admin"]}>
                <AnalysisResults />
              </ProtectedRoute>
            }
          />

          {/* Catch all */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

// Dashboard Router Component
const DashboardRouter = () => {
  const { user } = useAuth();

  if (user?.role === "instructor" || user?.role === "admin") {
    return <InstructorDashboard />;
  }

  return <StudentDashboard />;
};

export default App;