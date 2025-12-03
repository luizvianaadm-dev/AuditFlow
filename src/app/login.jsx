import React, { useState } from 'react';
import { Lock, Mail, Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';

const Login = () => {
  const navigate = useNavigate();
  const { login, loading, error } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(email, password);
    if (success) {
      navigate('/app');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-slate-100 overflow-hidden transform transition-all hover:shadow-xl">
        <div className="bg-primary p-8 text-center">
          <h1 className="text-3xl font-bold text-white tracking-tight">AuditFlow</h1>
          <p className="text-blue-100 mt-2 text-sm font-medium">Plataforma de Auditoria Inteligente</p>
        </div>

        <div className="p-8">
          <h2 className="text-xl font-semibold text-slate-700 mb-6 text-center">Acesse sua conta</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                E-mail Corporativo
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Mail className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type="email"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="seu@empresa.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Senha
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  required
                  className="block w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center cursor-pointer" onClick={() => setShowPassword(!showPassword)}>
                    {showPassword ? <EyeOff className="h-4 w-4 text-slate-400 hover:text-slate-600" /> : <Eye className="h-4 w-4 text-slate-400 hover:text-slate-600" />}
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between pt-2">
              <div className="flex items-center">
                <input
                  id="remember-me"
                  name="remember-me"
                  type="checkbox"
                  className="h-4 w-4 text-secondary focus:ring-secondary border-slate-300 rounded cursor-pointer"
                />
                <label htmlFor="remember-me" className="ml-2 block text-sm text-slate-600 cursor-pointer">
                  Lembrar-me
                </label>
              </div>

              <div className="text-sm">
                <a href="#" className="font-medium text-secondary hover:text-secondary-dark transition-colors">
                  Esqueceu a senha?
                </a>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white transition-all transform active:scale-[0.98] mt-4 ${
                loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-primary hover:bg-primary-light focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary'
              }`}
            >
              {loading ? 'Entrando...' : 'Entrar na Plataforma'}
            </button>
          </form>
        </div>

        <div className="bg-slate-50 px-8 py-5 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-600">
            Não tem uma conta?{' '}
            <button
              onClick={() => navigate('/register')}
              className="font-medium text-secondary hover:text-secondary-dark transition-colors focus:outline-none"
            >
              Cadastre sua empresa
            </button>
          </p>
        </div>
      </div>

      <div className="fixed bottom-4 text-center w-full">
        <p className="text-xs text-slate-400">© 2024 Vorcon Auditores. Todos os direitos reservados.</p>
      </div>
    </div>
  );
};

export default Login;
