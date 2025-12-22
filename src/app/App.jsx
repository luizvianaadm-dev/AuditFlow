import React from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Login from './login';
import Register from './components/Register';
import LandingPage from './pages/LandingPage';
import BillingPage from './pages/BillingPage';
import ClientList from './components/ClientList';
import ClientDetails from './components/ClientDetails';
import BenfordDashboard from './components/BenfordDashboard';
import Header from './components/Header';
import { AuthProvider, useAuth } from './context/AuthContext';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
    const { user, loading } = useAuth();
    if (loading) return <div className="min-h-screen flex items-center justify-center">Carregando...</div>;
    if (!user) return <Navigate to="/login" replace />;
    return (
        <div className="min-h-screen bg-background">
            <Header />
            <main>{children}</main>
        </div>
    );
};

const AppRoutes = () => {
    return (
        <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Routes */}
            <Route path="/billing" element={
                <ProtectedRoute>
                    <BillingPage />
                </ProtectedRoute>
            } />

            <Route path="/app/*" element={
                <ProtectedRoute>
                    <DashboardWrapper />
                </ProtectedRoute>
            } />

            {/* Redirect legacy or unknown routes */}
            <Route path="/dashboard" element={<Navigate to="/app" replace />} />
        </Routes>
    );
};

// Wrapper to preserve existing state-based navigation for Clients/Engagements
const DashboardWrapper = () => {
    const [selectedClient, setSelectedClient] = React.useState(null);
    const [selectedEngagement, setSelectedEngagement] = React.useState(null);

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

    if (selectedEngagement) {
        return (
            <div>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <button onClick={handleBackToClientDetails} className="text-sm text-slate-500 hover:text-slate-800 underline">
                        &larr; Voltar para {selectedClient.name}
                    </button>
                </div>
                <BenfordDashboard engagement={selectedEngagement} client={selectedClient} />
            </div>
        );
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
};

const App = () => {
    return (
        <BrowserRouter>
            <AuthProvider>
                <AppRoutes />
            </AuthProvider>
        </BrowserRouter>
    );
};

export default App;
