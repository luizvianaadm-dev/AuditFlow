import React, { useState, useEffect } from 'react';
import { Calculator, Save, AlertCircle } from 'lucide-react';
import { getFinancialSummary, saveMateriality } from '../services/clientService';

const MaterialityWizard = ({ engagement, onComplete }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [benchmark, setBenchmark] = useState('revenue'); // revenue, assets, equity
  const [percentage, setPercentage] = useState(5); // Default 5%
  const [performancePct, setPerformancePct] = useState(75); // Default 75% of Global
  const [error, setError] = useState('');

  useEffect(() => {
    loadSummary();
  }, [engagement]);

  const loadSummary = async () => {
    try {
      const data = await getFinancialSummary(engagement.id);
      setSummary(data);
    } catch (err) {
      setError("Erro ao carregar dados financeiros. Verifique se o mapeamento foi realizado.");
    } finally {
      setLoading(false);
    }
  };

  const calculateGlobal = () => {
      if (!summary) return 0;
      const base = summary[benchmark] || 0;
      return base * (percentage / 100);
  };

  const calculatePerformance = () => {
      return calculateGlobal() * (performancePct / 100);
  };

  const handleSave = async () => {
      try {
          await saveMateriality(engagement.id, {
              benchmark,
              benchmark_value: summary[benchmark],
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

  if (loading) return <div className="text-center p-6">Calculando saldos...</div>;

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

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Left: Financial Base */}
          <div>
              <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wide mb-4">Base Financeira (Mapeada)</h3>
              <div className="space-y-3">
                  <div
                    onClick={() => setBenchmark('revenue')}
                    className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === 'revenue' ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                  >
                      <div className="flex justify-between">
                          <span className="font-medium text-slate-700">Receita Total</span>
                          <span className="font-bold text-slate-900">R$ {summary?.revenue.toLocaleString()}</span>
                      </div>
                  </div>
                  <div
                    onClick={() => setBenchmark('assets')}
                    className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === 'assets' ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                  >
                      <div className="flex justify-between">
                          <span className="font-medium text-slate-700">Ativo Total</span>
                          <span className="font-bold text-slate-900">R$ {summary?.assets.toLocaleString()}</span>
                      </div>
                  </div>
                  <div
                    onClick={() => setBenchmark('equity')}
                    className={`p-3 border rounded-lg cursor-pointer transition-all ${benchmark === 'equity' ? 'border-secondary ring-1 ring-secondary bg-blue-50' : 'border-slate-200 hover:bg-slate-50'}`}
                  >
                      <div className="flex justify-between">
                          <span className="font-medium text-slate-700">Patrimônio Líquido</span>
                          <span className="font-bold text-slate-900">R$ {summary?.equity.toLocaleString()}</span>
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
                  <p className="text-xs text-slate-400 mt-1">Usual: 0.5% a 1% da Receita ou 1% a 2% do Ativo.</p>
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
                  <p className="text-xs text-slate-400 mt-1">Usual: 60% a 85%.</p>
              </div>

              <div className="bg-slate-100 p-4 rounded-lg space-y-2">
                  <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Materialidade Global:</span>
                      <span className="font-bold text-slate-800">R$ {calculateGlobal().toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                      <span className="text-slate-600">Materialidade de Performance:</span>
                      <span className="font-bold text-slate-800">R$ {calculatePerformance().toLocaleString(undefined, {minimumFractionDigits: 2})}</span>
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
