import React from 'react';
import { LogOut, User as UserIcon, CreditCard, LayoutGrid } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

const Header = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center cursor-pointer" onClick={() => navigate('/app')}>
            <div className="bg-gradient-to-tr from-blue-700 to-cyan-500 w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold mr-2">
              {user?.name ? user.name[0].toUpperCase() : 'A'}
            </div>
            <h1 className="text-xl font-bold text-slate-800 tracking-tight">AuditFlow</h1>
          </div>

          <div className="flex items-center space-x-6">
            <nav className="flex items-center space-x-4">
              <button onClick={() => navigate('/app')} className="text-slate-600 hover:text-blue-600 text-sm font-medium flex items-center">
                <LayoutGrid className="w-4 h-4 mr-1.5" /> Dashboard
              </button>
              <button onClick={() => navigate('/billing')} className="text-slate-600 hover:text-blue-600 text-sm font-medium flex items-center">
                <CreditCard className="w-4 h-4 mr-1.5" /> Assinatura
              </button>
            </nav>

            <div className="h-6 w-px bg-slate-200"></div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-slate-600">
                <div className="p-1 bg-slate-100 rounded-full">
                  <UserIcon className="w-4 h-4 text-slate-500" />
                </div>
                <span className="hidden md:block">{user?.name || user?.email}</span>
              </div>

              <button
                onClick={handleLogout}
                className="flex items-center text-sm font-medium text-red-600 hover:text-red-700 transition-colors"
              >
                <LogOut className="w-4 h-4 mr-1.5" />
                Sair
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
