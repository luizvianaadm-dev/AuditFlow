import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, BarChart2, FileText, Zap } from 'lucide-react';

const LandingPage = () => {
    const navigate = useNavigate();

    return (
        <div className="font-sans text-slate-900 bg-white">
            {/* Header */}
            <header className="border-b border-slate-100 sticky top-0 bg-white/80 backdrop-blur-md z-50">
                <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                         <div className="bg-gradient-to-tr from-blue-700 to-cyan-500 w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold">A</div>
                         <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-cyan-600">AuditFlow</span>
                    </div>
                    <div className="flex space-x-4">
                        <button onClick={() => navigate('/login')} className="text-slate-600 hover:text-slate-900 font-medium">Entrar</button>
                        <button onClick={() => navigate('/register')} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">Começar Agora</button>
                    </div>
                </div>
            </header>

            {/* Hero */}
            <section className="pt-20 pb-32 px-6 text-center max-w-5xl mx-auto">
                <h1 className="text-5xl md:text-6xl font-bold tracking-tight text-slate-900 mb-6">
                    Auditoria Contábil <span className="text-blue-600">Inteligente</span> e <span className="text-cyan-600">Automatizada</span>
                </h1>
                <p className="text-xl text-slate-600 mb-10 max-w-2xl mx-auto">
                    A primeira plataforma SaaS que democratiza ferramentas de nível "Big 4" para firmas de auditoria de pequeno e médio porte.
                </p>
                <div className="flex justify-center gap-4">
                    <button onClick={() => navigate('/register')} className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold text-lg shadow-lg hover:shadow-blue-500/25 transition-all">Criar Conta Grátis</button>
                    <button className="bg-white border border-slate-200 hover:border-slate-300 text-slate-700 px-8 py-3 rounded-xl font-semibold text-lg transition-all">Agendar Demo</button>
                </div>
            </section>

            {/* Features */}
            <section className="py-20 bg-slate-50 px-6">
                <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
                    <FeatureCard icon={<BarChart2 />} title="Lei de Benford" desc="Detecte anomalias estatísticas em grandes volumes de transações automaticamente." />
                    <FeatureCard icon={<ShieldCheck />} title="Normas NBC TAs" desc="Workflows guiados que garantem conformidade total com as normas brasileiras." />
                    <FeatureCard icon={<FileText />} title="Relatórios Prontos" desc="Gere pareceres e relatórios de auditoria em PDF e Word com um clique." />
                </div>
            </section>

            {/* Pricing Preview */}
             <section className="py-20 px-6">
                <div className="text-center mb-12">
                    <h2 className="text-3xl font-bold text-slate-900">Planos flexíveis para sua firma</h2>
                </div>
                <div className="max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-8">
                    <PricingCard title="Basic" price="R$ 99" desc="Para auditores individuais" />
                    <PricingCard title="Pro" price="R$ 299" desc="Para pequenas firmas" highlight={true} />
                    <PricingCard title="Enterprise" price="R$ 999" desc="Para grandes redes" />
                </div>
             </section>

            {/* Footer */}
            <footer className="bg-slate-900 text-slate-400 py-12 px-6 text-center">
                <p>© 2024 AuditFlow Tecnologia. Todos os direitos reservados.</p>
            </footer>
        </div>
    );
};

const FeatureCard = ({ icon, title, desc }) => (
    <div className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
        <div className="w-12 h-12 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center mb-4">{icon}</div>
        <h3 className="text-xl font-bold text-slate-900 mb-2">{title}</h3>
        <p className="text-slate-600">{desc}</p>
    </div>
);

const PricingCard = ({ title, price, desc, highlight }) => (
    <div className={`p-8 rounded-2xl border ${highlight ? 'border-blue-600 ring-2 ring-blue-600 ring-opacity-20 bg-blue-50' : 'border-slate-200 bg-white'}`}>
        <h3 className="text-lg font-semibold text-slate-900 mb-2">{title}</h3>
        <div className="text-4xl font-bold text-slate-900 mb-2">{price}<span className="text-sm text-slate-500 font-normal">/mês</span></div>
        <p className="text-slate-600 mb-6">{desc}</p>
    </div>
);

export default LandingPage;
