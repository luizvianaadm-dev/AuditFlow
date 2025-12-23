import React, { useState, useEffect } from 'react';
import { Calculator, Save, AlertCircle, Lightbulb } from 'lucide-react';
import { getFinancialSummary, saveMateriality, calculateMaterialitySuggestion } from '../services/clientService';

const MaterialityWizard = ({ engagement, onComplete }) => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [benchmark, setBenchmark] = useState('revenue'); // revenue, assets, equity
    const [percentage, setPercentage] = useState(5); // Default 5%
    const [performancePct, setPerformancePct] = useState(75); // Default 75% of Global
    const [suggestion, setSuggestion] = useState(null);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, [engagement]);

    const loadData = async () => {
        try {
            setLoading(true);
            // 1. Load Financials
            const finData = await getFinancialSummary(engagement.id);
            setSummary(finData);

            // 2. Load AI Suggestion
            const aiData = await calculateMaterialitySuggestion(engagement.id);
            if (aiData && aiData.suggestion) {
                setSuggestion(aiData); // Store full response including entity_type
                if (aiData.suggestion.benchmark !== 'manual') {
                    setBenchmark(aiData.suggestion.benchmark);
                    setPercentage(aiData.suggestion.recommended_pct * 100);
                }
            }

        } catch (err) {
            console.error(err);
            setError("Erro ao carregar dados. Verifique se a importação financeira foi realizada.");
        } finally {
            setLoading(false);
        }
    };

    const calculateGlobal = () => {
        if (!summary) return 0;
        // Handle Condominio 'total_expenses' if present in summary, otherwise 0
        // The current summary might not have 'total_expenses' if planning.py didn't return it in 'getFinancialSummary'
        // But 'calculateMaterialitySuggestion' returns 'financial_data' too!
        // We should use that preferably? 
        // For now, let's use summary object which we updated in planning.py? 
        // Wait, planning.py 'get_financial_summary' returns { revenue, assets... expenses: 0.0 }.
        // So it supports expenses.

        const map = {
            'revenue': summary.revenue || 0,
            'assets': summary.assets || 0,
            'equity': summary.equity || 0,
            'net_profit': (summary.revenue - summary.expenses) || 0, // Approx
            'total_expenses': summary.expenses || 0,
            'gross_revenue': summary.revenue || 0
        };

        const base = map[benchmark] || 0;
        return base * (percentage / 100);
    };

    const calculatePerformance = () => {
        return calculateGlobal() * (performancePct / 100);
    };

    const handleSave = async () => {
        try {
            await saveMateriality(engagement.id, {
                benchmark,
                benchmark_value: calculateGlobal() / (percentage / 100), // Reverse calc base
                percentage_global: percentage,
                percentage_performance: performancePct,
                global_materiality: calculateGlobal(),
                performance_materiality: calculatePerformance()
            });
            alert("Materialidade salva com sucesso!");
            if (onComplete) onComplete();
        } catch (err) {
            setError(err.message);
        }
    };

    if (loading) return <div className="text-center p-6 text-slate-500">Calculando sugestão da IA...</div>;

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="flex items-center mb-6">
                <div className="p-2 bg-blue-50 rounded-lg mr-3">
                    <Calculator className="w-6 h-6 text-primary" />
                </div>
                <h2 className="text-xl font-bold text-slate-800">Cálculo de Materialidade (NBC TA 320)</h2>
            </div>

            {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 flex items-center">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    {error}
                </div>
            )}

            {suggestion && (
                <div className="mb-6 p-4 bg-indigo-50 border border-indigo-100 rounded-lg flex items-start">
                    <Lightbulb className="w-5 h-5 text-indigo-600 mr-2 mt-0.5" />
                    <div>
                        <h4 className="font-semibold text-indigo-900 text-sm">IA Suggestion ({suggestion.entity_type})</h4>
                        <p className="text-sm text-indigo-700 mt-1">
                            Recomendamos usar <strong>{suggestion.suggestion.label}</strong> com base nos dados.
                            Calculado automaticamente: {suggestion.suggestion.recommended_pct * 100}%
                        </p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Left: Financial Base */}
                <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">Base Financeira</h3>
                    <div className="space-y-3">
                        <div
                            onClick={() => setBenchmark('revenue')}
                            className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === 'revenue' || benchmark === 'gross_revenue' ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                        >
                            <div className="flex justify-between">
                                <span className="font-medium text-slate-700">Receita Total</span>
                                <span className="font-bold text-slate-900">R$ {summary?.revenue?.toLocaleString()}</span>
                            </div>
                        </div>
                        <div
                            onClick={() => setBenchmark('assets')}
                            className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === 'assets' || benchmark === 'total_assets' ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                        >
                            <div className="flex justify-between">
                                <span className="font-medium text-slate-700">Ativo Total</span>
                                <span className="font-bold text-slate-900">R$ {summary?.assets?.toLocaleString()}</span>
                            </div>
                        </div>
                        {/* Condominio Special */}
                        <div
                            onClick={() => setBenchmark('total_expenses')}
                            className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === 'total_expenses' ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                        >
                            <div className="flex justify-between">
                                <span className="font-medium text-slate-700">Despesas (Condomínio)</span>
                                <span className="font-bold text-slate-900">R$ {summary?.expenses?.toLocaleString()}</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right: Parameters */}
                <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">Parâmetros de Auditoria</h3>

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            % para Materialidade Global
                        </label>
                        <div className="flex items-center">
                            <input
                                type="number"
                                value={percentage}
                                onChange={(e) => setPercentage(parseFloat(e.target.value))}
                                className="w-20 p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary outline-none text-right"
                            />
                            <span className="ml-2 text-slate-500">%</span>
                        </div>
                    </div>

                    <div className="mb-6">
                        <label className="block text-sm font-medium text-slate-700 mb-1">
                            % para Performance (Execução)
                        </label>
                        <div className="flex items-center">
                            <input
                                type="number"
                                value={performancePct}
                                onChange={(e) => setPerformancePct(parseFloat(e.target.value))}
                                className="w-20 p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary outline-none text-right"
                            />
                            <span className="ml-2 text-slate-500">% da Global</span>
                        </div>
                    </div>

                    <div className="bg-slate-100 p-4 rounded-lg space-y-2">
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-600">Materialidade Global (PM):</span>
                            <span className="font-bold text-slate-800">R$ {calculateGlobal().toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                        </div>
                        <div className="flex justify-between text-sm">
                            <span className="text-slate-600">Materialidade de Performance (TE):</span>
                            <span className="font-bold text-slate-800">R$ {calculatePerformance().toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                        </div>
                        <div className="flex justify-between text-sm border-t border-slate-200 pt-2 mt-2">
                            <span className="text-slate-500 text-xs">Limite de Trivialidade (CTT):</span>
                            <span className="font-bold text-slate-600 text-xs">R$ {(calculateGlobal() * 0.05).toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
                        </div>
                    </div>

                    <button
                        onClick={handleSave}
                        className="w-full mt-4 flex items-center justify-center px-4 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-lg transition-colors font-medium"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        Salvar Planejamento
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MaterialityWizard;
