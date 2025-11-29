import React, { useState } from 'react';
import { Lock, Mail, User, Building2, FileText } from 'lucide-react';
import { register } from '../services/authService';

const Register = ({ onNavigate }) => {
  const [formData, setFormData] = useState({
    companyName: '',
    cnpj: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (formData.password !== formData.confirmPassword) {
        setError("As senhas não coincidem.");
        setLoading(false);
        return;
    }

    try {
      await register({
          companyName: formData.companyName,
          cnpj: formData.cnpj,
          email: formData.email,
          password: formData.password
      });
      // On success, redirect to login
      alert("Cadastro realizado com sucesso! Faça login para continuar.");
      onNavigate('login');
    } catch (err) {
      setError(err.message);
    } finally {
        setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-xl shadow-lg border border-slate-100 overflow-hidden transform transition-all hover:shadow-xl">
        <div className="bg-primary p-8 text-center">
          <h1 className="text-2xl font-bold text-white tracking-tight">Nova Conta</h1>
          <p className="text-blue-100 mt-2 text-sm font-medium">Junte-se ao AuditFlow</p>
        </div>

        <div className="p-8">
            {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">

            {/* Company Name */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Razão Social / Nome
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Building2 className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type="text"
                  name="companyName"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="Nome da Empresa"
                  value={formData.companyName}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* CNPJ */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                CNPJ
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <FileText className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type="text"
                  name="cnpj"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="00.000.000/0000-00"
                  value={formData.cnpj}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Email */}
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
                  name="email"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="admin@empresa.com"
                  value={formData.email}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Senha
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type="password"
                  name="password"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* Confirm Password */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Confirmar Senha
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type="password"
                  name="confirmPassword"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white transition-all transform active:scale-[0.98] mt-6 ${
                  loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-secondary hover:bg-secondary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary'
              }`}
            >
              {loading ? 'Criando Conta...' : 'Criar Conta'}
            </button>
          </form>
        </div>

        <div className="bg-slate-50 px-8 py-5 border-t border-slate-100 text-center">
          <p className="text-sm text-slate-600">
            Já possui cadastro?{' '}
            <button
              onClick={() => onNavigate('login')}
              className="font-medium text-primary hover:text-primary-light transition-colors focus:outline-none"
            >
              Fazer Login
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
