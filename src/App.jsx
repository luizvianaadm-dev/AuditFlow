import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './app/context/AuthContext';
import Login from './app/login';
import BenfordDashboard from './app/components/BenfordDashboard';
import './app/index.css';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
};

// Main App Component
function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Login Route */}
          <Route path="/login" element={<Login />} />
          
          {/* Protected App Routes */}
          <Route 
            path="/app" 
            element={
              <ProtectedRoute>
                <BenfordDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Redirect root to /app */}
          <Route path="/" element={<Navigate to="/app" replace />} />
          
          {/* Catch-all redirect to /app */}
          <Route path="*" element={<Navigate to="/app" replace />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
