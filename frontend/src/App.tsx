import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { useUser } from './context/UserContext';
import './App.css';

// Pages
import Dashboard from './pages/Dashboard';
import Todos from './pages/Todos';
import Habits from './pages/Habits';
import Pomodoro from './pages/Pomodoro';
import Login from './pages/Login';
import Register from './pages/Register';
import Profile from './pages/Profile';
import NotFound from './pages/NotFound';
import AdminDashboard from './pages/AdminDashboard';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import MobileNav from './components/MobileNav';
import HabitDetail from './pages/HabitDetail';
import VerifyOTPPage from './pages/VerifyOTP';

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isVerifying, logout } = useUser();
  const navigate = useNavigate();
  
  useEffect(() => {
    const handleLogout = () => {
      logout();
      navigate('/login');
    };
    
    const handleToggleDarkMode = () => {
      const currentDarkMode = document.documentElement.classList.contains('dark');
      const newDarkMode = !currentDarkMode;
      document.documentElement.classList.toggle('dark', newDarkMode);
      localStorage.setItem('darkMode', newDarkMode.toString());
    };
    
    window.addEventListener('logout', handleLogout);
    window.addEventListener('toggleDarkMode', handleToggleDarkMode);
    
    return () => {
      window.removeEventListener('logout', handleLogout);
      window.removeEventListener('toggleDarkMode', handleToggleDarkMode);
    };
  }, [logout, navigate]);
  
  // Show loading state while verifying authentication
  if (isVerifying) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
      </div>
    );
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <div className="hidden md:block">
        <Sidebar />
      </div>
      <div className="flex-1 flex flex-col overflow-hidden">
        <div className="hidden md:block">
          <Navbar />
        </div>
        <main className="flex-1 overflow-y-auto p-4 md:p-6 pb-16 md:pb-0">
          {children}
        </main>
        <div className="md:hidden">
          <MobileNav />
        </div>
      </div>
    </div>
  );
};

// Public Route Component (redirects authenticated users)
const PublicRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, isVerifying } = useUser();
  
  // Show loading state while verifying authentication
  if (isVerifying) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
      </div>
    );
  }
  
  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }
  
  return <>{children}</>;
};

// Admin Route Component
const AdminRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user } = useUser();

  if (user && !user.is_admin) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
};

const App = () => {
  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<PublicRoute><Login /></PublicRoute>} />
        <Route path="/register" element={<PublicRoute><Register /></PublicRoute>} />
        <Route path="/verify-otp" element={<PublicRoute><VerifyOTPPage /></PublicRoute>} />

        {/* Protected Routes */}
        <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="/todos" element={<ProtectedRoute><Todos /></ProtectedRoute>} />
        <Route path="/habits" element={<ProtectedRoute><Habits /></ProtectedRoute>} />
        <Route path="/habits/:id" element={<ProtectedRoute><HabitDetail /></ProtectedRoute>} />
        <Route path="/pomodoro" element={<ProtectedRoute><Pomodoro /></ProtectedRoute>} />
        <Route path="/profile" element={<ProtectedRoute><Profile /></ProtectedRoute>} />

        {/* Admin Route */}
        <Route path="/admin" element={<ProtectedRoute><AdminRoute><AdminDashboard /></AdminRoute></ProtectedRoute>} />

        {/* Not Found Route */}
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Router>
  );
};

export default App;
