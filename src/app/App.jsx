import React, { useState } from 'react';
import Login from './login';
import Register from './components/Register';
import BenfordDashboard from './components/BenfordDashboard';

const App = () => {
  const [currentScreen, setCurrentScreen] = useState('login'); // 'login', 'register', 'dashboard'

  const handleNavigate = (screen) => {
    setCurrentScreen(screen);
  };

  return (
    <div className="bg-background min-h-screen text-slate-800 font-sans">
      {currentScreen === 'login' && (
        <Login onNavigate={handleNavigate} />
      )}

      {currentScreen === 'register' && (
        <Register onNavigate={handleNavigate} />
      )}

      {currentScreen === 'dashboard' && (
        <BenfordDashboard />
      )}
    </div>
  );
};

export default App;
