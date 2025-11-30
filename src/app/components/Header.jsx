import React from 'react';
import { LogOut, User as UserIcon } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Header = () => {
  const { user, logout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-primary tracking-tight">AuditFlow</h1>
          </div>

          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-sm text-slate-600">
                <div className="p-1 bg-slate-100 rounded-full">
                    <UserIcon className="w-4 h-4 text-slate-500" />
                </div>
                <span className="hidden md:block">{user?.email}</span>
            </div>

            <div className="h-6 w-px bg-slate-200"></div>

            <button
              onClick={logout}
              className="flex items-center text-sm font-medium text-red-600 hover:text-red-700 transition-colors"
            >
              <LogOut className="w-4 h-4 mr-1.5" />
              Sair
            </button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
