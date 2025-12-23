import React, { useState, useEffect } from 'react';
import { CheckSquare, AlertCircle, FileText, Save, ArrowLeft } from 'lucide-react';
import { getOrCreateWorkpaper, updateGenericWorkpaper, getRiskFactors } from '../services/clientService';

const WorkpaperContainer = ({ engagement, account, onBack }) => {
    const [wp, setWp] = useState(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('procedures'); // procedures, findings
    const [unsavedChanges, setUnsavedChanges] = useState(false);

    useEffect(() => {
        loadWP();
    }, [account]);

    const loadWP = async () => {
        try {
            setLoading(true);
            const data = await getOrCreateWorkpaper(engagement.id, account.account_code, account.account_name);
            setWp(data.result); // AnalysisResult.result holds the JSON
        } catch (err) {
            console.error(err);
            alert("Erro ao carregar Papel de Trabalho");
        } finally {
            setLoading(false);
        }
    };

    const handleCheck = (id) => {
        if (!wp) return;
        const newProcedures = wp.procedures.map(p =>
            p.id === id ? { ...p, checked: !p.checked } : p
        );
        const newWp = { ...wp, procedures: newProcedures };
        setWp(newWp);
        setUnsavedChanges(true);
    };

    const handleSave = async () => {
        try {
            await updateGenericWorkpaper(engagement.id, account.account_code, wp);
            setUnsavedChanges(false);
            alert("Salvo com sucesso!");
        } catch (err) {
            alert("Erro ao salvar: " + err.message);
        }
    };

    if (loading) return <div className="p-10 text-center text-slate-500">Carregando Papel de Trabalho...</div>;
    if (!wp) return <div className="p-10 text-center text-red-500">Erro ao carregar dados.</div>;

    const progress = Math.round((wp.procedures.filter(p => p.checked).length / wp.procedures.length) * 100) || 0;

    return (
        <div className="bg-white min-h-[600px] flex flex-col">
            {/* Header */}
            <div className="border-b border-slate-200 p-4 flex justify-between items-center bg-slate-50">
                <div className="flex items-center">
                    <button onClick={onBack} className="mr-3 p-2 hover:bg-slate-200 rounded-full text-slate-500">
                        <ArrowLeft className="w-5 h-5" />
                    </button>
                    <div>
                        <h2 className="text-lg font-bold text-slate-800">{account.account_name}</h2>
                        <div className="flex items-center text-xs text-slate-500 space-x-3">
                            <span>{account.account_code}</span>
                            <span>|</span>
                            <span>Risco: {account.risk || 'N/A'}</span>
                            <span>|</span>
                            <span>Estratégia: {account.strategy || 'N/A'}</span>
                        </div>
                    </div>
                </div>
                <div className="flex items-center space-x-4">
                    <div className="text-right">
                        <div className="text-xs text-slate-500">Progresso</div>
                        <div className="font-bold text-primary">{progress}%</div>
                    </div>
                    {unsavedChanges && <span className="text-xs text-amber-600 font-medium">Não salvo*</span>}
                    <button
                        onClick={handleSave}
                        className="bg-primary text-white px-4 py-2 rounded-lg flex items-center hover:bg-primary-dark"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        Salvar
                    </button>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-slate-200 px-4">
                <button
                    onClick={() => setActiveTab('procedures')}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'procedures' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-800'}`}
                >
                    Execução (Procedimentos)
                </button>
                <button
                    onClick={() => setActiveTab('findings')}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === 'findings' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-800'}`}
                >
                    Divergências (Achados)
                </button>
            </div>

            {/* Content */}
            <div className="p-6 flex-1 overflow-y-auto">
                {activeTab === 'procedures' && (
                    <div className="max-w-3xl mx-auto space-y-6 animate-fade-in">
                        <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 mb-6">
                            <h4 className="text-sm font-bold text-blue-800 mb-2">Objetivo de Auditoria</h4>
                            <p className="text-sm text-blue-700">
                                Assegurar a existência, integridade, e avaliação correta dos saldos de {account.account_name},
                                conforme risco {account.risk} e estratégia {account.strategy}.
                            </p>
                        </div>

                        <div className="space-y-2">
                            {wp.procedures.map(p => (
                                <label key={p.id} className="flex items-start p-3 border rounded-lg hover:bg-slate-50 cursor-pointer transition-colors border-slate-200">
                                    <input
                                        type="checkbox"
                                        checked={p.checked}
                                        onChange={() => handleCheck(p.id)}
                                        className="mt-1 w-5 h-5 text-primary rounded focus:ring-primary border-slate-300"
                                    />
                                    <div className="ml-3">
                                        <span className={`text-sm font-medium ${p.checked ? 'text-slate-900' : 'text-slate-700'}`}>{p.label}</span>
                                        {p.checked && <div className="text-xs text-green-600 mt-1">Concluído</div>}
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'findings' && (
                    <div className="max-w-3xl mx-auto text-center py-10">
                        <div className="inline-block p-4 bg-slate-100 rounded-full mb-4">
                            <AlertCircle className="w-8 h-8 text-slate-400" />
                        </div>
                        <h3 className="text-lg font-medium text-slate-700">Registro de Divergências</h3>
                        <p className="text-slate-500 mb-6">Integração com Sumário de Erros em construção.</p>
                        <button className="text-primary hover:underline text-sm font-medium">
                            + Adicionar Nova Divergência
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default WorkpaperContainer;
