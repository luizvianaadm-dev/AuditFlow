import React, { useState, useEffect } from 'react';
import { Calculator, Save, AlertCircle, Lightbulb, CheckSquare, ShieldAlert } from 'lucide-react';
import { getFinancialSummary, saveMateriality, calculateMaterialitySuggestion, getRiskFactors } from '../services/clientService';

const MaterialityWizard = ({ engagement, onComplete }) => {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [benchmark, setBenchmark] = useState('revenue');
    const [percentage, setPercentage] = useState(5);
    const [performancePct, setPerformancePct] = useState(75);
    const [suggestion, setSuggestion] = useState(null);
    const [risks, setRisks] = useState([]);
    const [selectedRisks, setSelectedRisks] = useState([]);
    const [calculatedValues, setCalculatedValues] = useState(null); // { pm, te, ctt }
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, [engagement]);

    const loadData = async () => {
        try {
            setLoading(true);

            // 0. Load Risk Factors
            try {
                const r = await getRiskFactors();
                setRisks(r);
            } catch (ignored) {
                console.warn("Could not load risks", ignored);
            }

            // 1. Load Financials
            const finData = await getFinancialSummary(engagement.id);
            setSummary(finData);

            // 2. Load AI Suggestion (Initial)
            await recalculateSuggestion(finData, []);

        } catch (err) {
            console.error(err);
            setError("Erro ao carregar dados. Verifique se a importação financeira foi realizada.");
        } finally {
            setLoading(false);
        }
    };

    const recalculateSuggestion = async (currentSummary, currentRisks) => {
        try {
            const aiData = await calculateMaterialitySuggestion(engagement.id, currentRisks);
            if (aiData && aiData.suggestion) {
                setSuggestion(aiData);
                if (aiData.suggestion.benchmark !== 'manual') {
                    // Update Benchmark if Manual Override not active (Simplification: Always update for now)
                    setBenchmark(aiData.suggestion.benchmark);
                    setPercentage(aiData.suggestion.recommended_pct * 100);
                }
                if (aiData.calculated_values) {
                    setCalculatedValues(aiData.calculated_values);
                }
            }
        } catch (e) {
            console.error(e);
        }
    };

    const handleRiskToggle = async (riskId) => {
        const newSelection = selectedRisks.includes(riskId)
            ? selectedRisks.filter(id => id !== riskId)
            : [...selectedRisks, riskId];

        setSelectedRisks(newSelection);
        await recalculateSuggestion(summary, newSelection);
    };

    // Fallback Calculation (Manual override in frontend visually if API fails, but we prefer API values)
    const calculateGlobal = () => {
        if (calculatedValues) return calculatedValues.pm; // Use API Adjusted Value
        if (!summary) return 0;
        // ... (Fallback manual logic omitted for brevity, logic moved to backend)
        const map = {
            'revenue': summary.revenue || 0,
            'assets': summary.assets || 0,
            'equity': summary.equity || 0,
            'net_profit': (summary.revenue - summary.expenses) || 0,
            'total_expenses': summary.expenses || 0,
            'gross_revenue': summary.revenue || 0
        };
        const base = map[benchmark] || 0;
        return base * (percentage / 100);
    };

    const calculatePerformance = () => {
        if (calculatedValues) return calculatedValues.te;
        return calculateGlobal() * (performancePct / 100);
    };

    const calculateCTT = () => {
        if (calculatedValues) return calculatedValues.ctt;
        return calculateGlobal() * 0.05;
    }

    const handleSave = async () => {
        try {
            await saveMateriality(engagement.id, {
                benchmark,
                benchmark_value: 0, // Should calculate base
                percentage_global: percentage,
                percentage_performance: performancePct,
                global_materiality: calculateGlobal(),
                performance_materiality: calculatePerformance(),
                risks_identified: selectedRisks
            });
            alert("Planejamento salvo com sucesso!");
            if (onComplete) onComplete();
        } catch (err) {
            setError(err.message);
        }
    };

    if (loading) return <div className="text-center p-6 text-slate-500">Iniciando Motor de Auditoria...</div>;

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
                            Base: <strong>{suggestion.suggestion.label}</strong>. Risco Calculado: <strong>{suggestion.suggestion.risk_score}</strong> pontos.
                            <br />
                            Recomendação: {percentage.toFixed(2)}% (Ajustado pelo risco).
                        </p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* 1. Base Financeira */}
                <div className="space-y-6">
                    <div>
                        <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">1. Base (Quantitativo)</h3>
                        <div className="space-y-3">
                            {['revenue', 'assets', 'equity', 'total_expenses'].map(key => {
                                // Filter irrelevant keys if needed
                                if (key === 'total_expenses' && !summary?.expenses) return null;
                                const labelMap = {
                                    'revenue': 'Receita Total', 'assets': 'Ativo Total',
                                    'equity': 'Patrimônio Líquido', 'total_expenses': 'Despesas Totais'
                                };
                                const valMap = {
                                    'revenue': summary?.revenue, 'assets': summary?.assets,
                                    'equity': summary?.equity, 'total_expenses': summary?.expenses
                                };

                                return (
                                    <div
                                        key={key}
                                        onClick={() => setBenchmark(key)}
                                        className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === key ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                                    >
                                        <div className="flex justify-between">
                                            <span className="font-medium text-slate-700">{labelMap[key]}</span>
                                            <span className="font-bold text-slate-900">R$ {valMap[key]?.toLocaleString()}</span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>

                {/* 2. Riscos (Qualitativo) */}
                <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4 flex items-center">
                        2. Avaliação de Riscos
                        <ShieldAlert className="w-4 h-4 ml-2 text-amber-500" />
                    </h3>
                    <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 space-y-3">
                        <p className="text-xs text-slate-500 mb-2">Selecione os fatores presentes para ajustar a %:</p>
                        {risks.map(r => (
                            <label key={r.id} className="flex items-start space-x-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={selectedRisks.includes(r.id)}
                                    onChange={() => handleRiskToggle(r.id)}
                                    className="mt-1 w-4 h-4 text-secondary rounded border-slate-300 focus:ring-secondary"
                                />
                                <span className="text-sm text-slate-700 leading-snug">{r.label} <span className="text-xs text-slate-400">({r.weight} pts)</span></span>
                            </label>
                        ))}
                        {risks.length === 0 && <p className="text-sm text-slate-400">Carregando fatores de risco...</p>}
                    </div>
                </div>

                {/* 3. Resultados */}
                <div>
                    <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">3. Definição (NBC TA 320)</h3>

                    <div className="mb-4">
                        <label className="block text-sm font-medium text-slate-700 mb-1">% Global Aplicada</label>
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

                    <div className="bg-slate-100 p-4 rounded-lg space-y-3">
                        <div className="flex justify-between text-sm items-center">
                            <span className="text-slate-600">Materialidade Global (PM):</span>
                            <span className="font-bold text-lg text-slate-800">R$ {calculateGlobal().toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm items-center">
                            <span className="text-slate-600">Performance (TE) (75%):</span>
                            <span className="font-bold text-slate-800">R$ {calculatePerformance().toLocaleString()}</span>
                        </div>
                        <div className="flex justify-between text-sm items-center border-t border-slate-200 pt-2">
                            <span className="text-slate-500 text-xs">Limite (AMPT/CTT) (5%):</span>
                            <span className="font-bold text-slate-600 text-xs">R$ {calculateCTT().toLocaleString()}</span>
                        </div>
                    </div>

                    <button
                        onClick={handleSave}
                        className="w-full mt-6 flex items-center justify-center px-4 py-3 bg-secondary hover:bg-secondary-dark text-white rounded-lg transition-colors font-medium shadow-md"
                    >
                        <Save className="w-4 h-4 mr-2" />
                        Confirmar e Salvar
                    </button>
                </div>
            </div>
        </div>
    );
};

export default MaterialityWizard;
