import React, { useState } from 'react';
import Login from './login';
import Register from './components/Register';
import ClientList from './components/ClientList';
import ClientDetails from './components/ClientDetails';
import BenfordDashboard from './components/BenfordDashboard';
import { AuthProvider, useAuth } from './context/AuthContext';

const AppContent = () => {
  const { user } = useAuth();
  const [currentScreen, setCurrentScreen] = useState('login'); // 'login', 'register'
  const [selectedClient, setSelectedClient] = useState(null);
  const [selectedEngagement, setSelectedEngagement] = useState(null);

  const handleNavigate = (screen) => {
    setCurrentScreen(screen);
  };

  const handleClientSelect = (client) => {
    setSelectedClient(client);
    setSelectedEngagement(null);
  };

  const handleEngagementSelect = (engagement) => {
    setSelectedEngagement(engagement);
  };

  const handleBackToClients = () => {
    setSelectedClient(null);
    setSelectedEngagement(null);
  };

  const handleBackToClientDetails = () => {
    setSelectedEngagement(null);
  };

  // Authenticated Flow
  if (user) {
    if (selectedEngagement) {
      return (
        <div>
           <button
            onClick={handleBackToClientDetails}
            className="m-4 text-sm text-slate-500 hover:text-slate-800 underline"
          >
            &larr; Voltar para {selectedClient.name}
          </button>
          <BenfordDashboard engagement={selectedEngagement} />
        </div>
      )
    }

    if (selectedClient) {
      return (
        <ClientDetails
          client={selectedClient}
          onBack={handleBackToClients}
          onSelectEngagement={handleEngagementSelect}
        />
      );
    }
    return <ClientList onSelectClient={handleClientSelect} />;
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
