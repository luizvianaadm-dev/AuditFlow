import React, { useState } from 'react';
import Login from './login';
import Register from './components/Register';
import ClientList from './components/ClientList';
import ClientDetails from './components/ClientDetails';
import BenfordDashboard from './components/BenfordDashboard';
import Header from './components/Header';
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
    return (
      <div className="min-h-screen bg-background">
        <Header />
        <main>
          {selectedEngagement ? (
            <div>
               <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                 <button
                  onClick={handleBackToClientDetails}
                  className="text-sm text-slate-500 hover:text-slate-800 underline"
                >
                  &larr; Voltar para {selectedClient.name}
                </button>
               </div>
              <BenfordDashboard engagement={selectedEngagement} />
            </div>
          ) : selectedClient ? (
            <ClientDetails
              client={selectedClient}
              onBack={handleBackToClients}
              onSelectEngagement={handleEngagementSelect}
            />
          ) : (
            <ClientList onSelectClient={handleClientSelect} />
          )}
        </main>
      </div>
    );
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
