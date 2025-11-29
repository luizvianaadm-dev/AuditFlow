import React, { useState } from 'react';
import Login from './login';
import Register from './components/Register';
import BenfordDashboard from './components/BenfordDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';

const AppContent = () => {
  const { user } = useAuth();
  const [currentScreen, setCurrentScreen] = useState('login'); // 'login', 'register', 'dashboard'

  const handleNavigate = (screen) => {
    setCurrentScreen(screen);
  };

  // If user is authenticated, show dashboard
  if (user) {
      return <BenfordDashboard />;
  }

  return (
    <div className="bg-background min-h-screen text-slate-800 font-sans">
      {currentScreen === 'login' && (
        <Login onNavigate={handleNavigate} />
      )}

      {currentScreen === 'register' && (
        <Register onNavigate={handleNavigate} />
      )}
    </div>
  );
};

const App = () => {
    return (
        <AuthProvider>
            <AppContent />
        </AuthProvider>
    );
};

export default App;
