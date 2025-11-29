import React, { useState } from 'react';
import Login from './login';
import Register from './components/Register';
import ClientList from './components/ClientList';
import BenfordDashboard from './components/BenfordDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';

const AppContent = () => {
  const { user } = useAuth();
  const [currentScreen, setCurrentScreen] = useState('login'); // 'login', 'register'
  const [selectedClient, setSelectedClient] = useState(null);

  const handleNavigate = (screen) => {
    setCurrentScreen(screen);
  };

  // Authenticated Flow
  if (user) {
    if (selectedClient) {
      return (
        <div>
          <button
            onClick={() => setSelectedClient(null)}
            className="m-4 text-sm text-slate-500 hover:text-slate-800 underline"
          >
            &larr; Voltar para Clientes
          </button>
          <BenfordDashboard client={selectedClient} />
        </div>
      );
    }
    return <ClientList onSelectClient={setSelectedClient} />;
  }

  // Public Flow
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
