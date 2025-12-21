import React, { useState } from 'react';
import { Lock, Mail, User, Building2, FileText, ShieldCheck, CheckCircle, Eye, EyeOff } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { register } from '../services/authService';
import { LegalModal } from './LegalModals';

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    companyName: '',
    cnpj: '',
    email: '',
    password: '',
    confirmPassword: '',
    cnai: '',
    cnai_expiration_date: '',
    crc_registration: '',
    cvm_registration: '',
    cpf: '',
    phone: '',
    termsAccepted: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Legal State
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [showTerms, setShowTerms] = useState(false);
  const [showPrivacy, setShowPrivacy] = useState(false);
  const [legalState, setLegalState] = useState({ terms: false, privacy: false });

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
        password: formData.password,
        cnai: formData.cnai,
        cnai_expiration_date: formData.cnai_expiration_date,
        crc_registration: formData.crc_registration,
        cvm_registration: formData.cvm_registration,
        cpf: formData.cpf,
        phone: formData.phone,
        termsAccepted: true // Validated by disable button logic
      });
      // On success, redirect to login
      alert("Cadastro realizado com sucesso! Faça login para continuar.");
      navigate('/login');
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

            {/* CRC Registration */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Registro CRC (Escritório)
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Building2 className="h-5 w-5 text-slate-400 group-focus-within:text-green-500 transition-colors" />
                </div>
                <input
                  type="text"
                  name="crc_registration"
                  required
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-200 focus:border-green-500 sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="Ex: RJ-000000/O-0"
                  value={formData.crc_registration}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* CNAI & Expiration */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Registro CNAI
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <ShieldCheck className={`h-5 w-5 transition-colors ${formData.cnai.length > 3 ? 'text-green-500' : 'text-slate-400'}`} />
                  </div>
                  <input
                    type="text"
                    name="cnai"
                    required
                    className={`block w-full pl-10 pr-3 py-2.5 border rounded-lg focus:ring-2 sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white ${formData.cnai.length > 3
                      ? 'border-green-300 focus:border-green-500 focus:ring-green-200'
                      : 'border-slate-300 focus:border-secondary focus:border-secondary'
                      }`}
                    placeholder="Ex: RJ-000000/O-0"
                    value={formData.cnai}
                    onChange={handleChange}
                  />
                  {formData.cnai.length > 3 && (
                    <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                      <span className="text-xs text-green-600 font-medium bg-green-50 px-2 py-0.5 rounded-full">Válido</span>
                    </div>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Validade CNAI/CRC
                </label>
                <input
                  type="date"
                  name="cnai_expiration_date"
                  required
                  className="block w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  value={formData.cnai_expiration_date}
                  onChange={handleChange}
                />
              </div>
            </div>

            {/* CVM */}
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">
                Registro CVM (Opcional)
              </label>
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Building2 className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                </div>
                <input
                  type="text"
                  name="cvm_registration"
                  className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="Se houver"
                  value={formData.cvm_registration}
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

            {/* CPF & Phone */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  CPF
                </label>
                <div className="relative group">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <User className="h-5 w-5 text-slate-400 group-focus-within:text-secondary transition-colors" />
                  </div>
                  <input
                    type="text"
                    name="cpf"
                    required
                    className="block w-full pl-10 pr-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                    placeholder="000.000.000-00"
                    value={formData.cpf}
                    onChange={handleChange}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Telefone
                </label>
                <input
                  type="text"
                  name="phone"
                  required
                  className="block w-full px-3 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="(00) 00000-0000"
                  value={formData.phone}
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
                  type={showPassword ? "text" : "password"}
                  name="password"
                  required
                  className="block w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="••••••••"
                  value={formData.password}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-secondary focus:outline-none"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
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
                  type={showConfirmPassword ? "text" : "password"}
                  name="confirmPassword"
                  required
                  className="block w-full pl-10 pr-10 py-2.5 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary focus:border-secondary sm:text-sm outline-none transition-all bg-slate-50 focus:bg-white"
                  placeholder="••••••••"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-secondary focus:outline-none"
                >
                  {showConfirmPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Legal Consent Section */}
            <div className="space-y-3 mt-6">

              {/* Terms Trigger */}
              <div
                onClick={() => setShowTerms(true)}
                className={`flex items-center p-3 border rounded-lg cursor-pointer transition-all hover:bg-slate-50 ${legalState.terms ? 'border-green-200 bg-green-50' : 'border-slate-200'}`}
              >
                <div className={`w-5 h-5 rounded border flex items-center justify-center mr-3 ${legalState.terms ? 'bg-green-500 border-green-500 text-white' : 'border-slate-300 bg-white'}`}>
                  {legalState.terms && <CheckCircle className="w-3 h-3" />}
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-700">Termos de Uso</span>
                  <p className="text-xs text-slate-500">Clique para ler e aceitar os termos da Vorcon Tech.</p>
                </div>
              </div>

              {/* Privacy Trigger */}
              <div
                onClick={() => setShowPrivacy(true)}
                className={`flex items-center p-3 border rounded-lg cursor-pointer transition-all hover:bg-slate-50 ${legalState.privacy ? 'border-green-200 bg-green-50' : 'border-slate-200'}`}
              >
                <div className={`w-5 h-5 rounded border flex items-center justify-center mr-3 ${legalState.privacy ? 'bg-green-500 border-green-500 text-white' : 'border-slate-300 bg-white'}`}>
                  {legalState.privacy && <CheckCircle className="w-3 h-3" />}
                </div>
                <div>
                  <span className="text-sm font-medium text-slate-700">Política de Privacidade</span>
                  <p className="text-xs text-slate-500">Clique para ler e aceitar a política LGPD.</p>
                </div>
              </div>

            </div>

            <button
              type="submit"
              disabled={loading || !legalState.terms || !legalState.privacy}
              className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-bold text-white transition-all transform active:scale-[0.98] mt-6 ${loading || !legalState.terms || !legalState.privacy ? 'bg-slate-400 cursor-not-allowed' : 'bg-secondary hover:bg-secondary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary'
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
              onClick={() => navigate('/login')}
              className="font-medium text-primary hover:text-primary-light transition-colors focus:outline-none"
            >
              Fazer Login
            </button>
          </p>
        </div>
      </div>

      {/* Modals */}
      <LegalModal
        title="Termos de Uso - Vorcon Tech"
        type="terms"
        isOpen={showTerms}
        onClose={() => setShowTerms(false)}
        onAccept={() => { setLegalState(prev => ({ ...prev, terms: true })); setShowTerms(false); }}
      />
      <LegalModal
        title="Política de Privacidade - LGPD"
        type="privacy"
        isOpen={showPrivacy}
        onClose={() => setShowPrivacy(false)}
        onAccept={() => { setLegalState(prev => ({ ...prev, privacy: true })); setShowPrivacy(false); }}
      />
    </div>
  );
};

export default Register;
