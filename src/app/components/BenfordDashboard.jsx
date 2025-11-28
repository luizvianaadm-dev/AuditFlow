import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertTriangle, CheckCircle, Calculator } from 'lucide-react';
import { analyzeBenford } from '../services/auditService';

export default function BenfordDashboard() {
  const [inputData, setInputData] = useState('');
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    setLoading(true);
    setError(null);
    setAnalysisResult(null);

    try {
      // Parse input: allow JSON or comma-separated values
      let transactions = [];
      const cleanedInput = inputData.trim();

      if (cleanedInput.startsWith('[')) {
        transactions = JSON.parse(cleanedInput);
      } else {
        transactions = cleanedInput
          .split(',')
          .map(s => parseFloat(s.trim()))
          .filter(n => !isNaN(n));
      }

      if (transactions.length === 0) {
        throw new Error("Insira uma lista válida de números.");
      }

      const result = await analyzeBenford(transactions);
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message || "Erro ao processar dados.");
    } finally {
      setLoading(false);
    }
  };

  // Prepare chart data
  const chartData = analysisResult
    ? Object.keys(analysisResult.expected).map(digit => ({
        digit: parseInt(digit),
        Esperado: (analysisResult.expected[digit] * 100).toFixed(2),
        Observado: (analysisResult.observed[digit] * 100).toFixed(2),
      }))
    : [];

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
        <h2 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
          <Calculator className="w-5 h-5 text-blue-600" />
          Dados da Amostra
        </h2>
        <textarea
          className="w-full h-32 p-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none font-mono text-sm"
          placeholder="Cole aqui os valores (ex: 100.50, 230.00...) ou JSON."
          value={inputData}
          onChange={(e) => setInputData(e.target.value)}
        />
        <div className="mt-4 flex justify-end">
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Analisando...' : 'Executar Análise de Benford'}
          </button>
        </div>
        {error && (
          <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" />
            {error}
          </div>
        )}
      </div>

      {/* Results Section */}
      {analysisResult && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Chart */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold text-slate-800 mb-6">Distribuição de Dígitos</h3>
            <div className="h-80 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="digit" />
                  <YAxis unit="%" />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="Esperado"
                    stroke="#94a3b8"
                    strokeDasharray="5 5"
                    strokeWidth={2}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="Observado"
                    stroke="#2563eb"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Anomalies Panel */}
          <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center gap-2">
              <AlertTriangle className={`w-5 h-5 ${analysisResult.anomalies.length > 0 ? 'text-red-500' : 'text-green-500'}`} />
              Análise de Risco
            </h3>

            {analysisResult.anomalies.length > 0 ? (
              <div className="space-y-4">
                <div className="p-4 bg-red-50 border border-red-100 rounded-lg">
                  <p className="text-sm text-red-800 font-medium mb-2">
                    Divergências Significativas Detectadas (>5%)
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {analysisResult.anomalies.map(digit => (
                      <span key={digit} className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-bold">
                        Dígito {digit}
                      </span>
                    ))}
                  </div>
                </div>
                <p className="text-sm text-slate-600 leading-relaxed">
                  Os dígitos acima apresentam frequência observada com desvio superior ao limite tolerável da Lei de Benford.
                  Recomenda-se aprofundar a auditoria nas transações iniciadas com estes números.
                </p>
              </div>
            ) : (
              <div className="p-4 bg-green-50 border border-green-100 rounded-lg flex items-start gap-3">
                <CheckCircle className="w-5 h-5 text-green-600 mt-0.5" />
                <div>
                  <p className="text-sm text-green-800 font-medium">Nenhuma Anomalia Detectada</p>
                  <p className="text-xs text-green-700 mt-1">
                    A distribuição dos dados está em conformidade com a Lei de Benford.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
