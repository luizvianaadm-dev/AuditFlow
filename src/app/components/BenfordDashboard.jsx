import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle } from 'lucide-react';
import { analyzeBenford } from '../services/auditService';

const BenfordDashboard = () => {
  const [inputValue, setInputValue] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setResult(null);

    try {
      // Parse input: allow comma, newline, or space separated values
      const cleanedInput = inputValue.replace(/[\n,]/g, ' ');
      const values = cleanedInput
        .split(' ')
        .map(v => parseFloat(v))
        .filter(v => !isNaN(v));

      if (values.length === 0) {
        throw new Error('Por favor, insira valores numéricos válidos.');
      }

      const data = await analyzeBenford(values);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const chartData = result
    ? Object.keys(result.expected_frequencies).map((digit) => ({
        digit: digit,
        Esperado: (result.expected_frequencies[digit] * 100).toFixed(1),
        Observado: (result.observed_frequencies[digit] * 100).toFixed(1),
      }))
    : [];

  return (
    <div className="p-6 bg-gray-50 min-h-screen font-sans text-gray-800">
      <div className="max-w-4xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">Auditoria Digital - Lei de Benford</h1>
          <p className="text-slate-600 mt-2">Análise forense de conformidade de dados financeiros (NBC TA 520).</p>
        </header>

        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 mb-8">
          <h2 className="text-xl font-semibold mb-4 text-slate-700">Entrada de Dados</h2>
          <textarea
            className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition"
            rows="5"
            placeholder="Cole aqui a lista de valores (separados por vírgula, espaço ou nova linha)..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading}
            className={`mt-4 px-6 py-2 rounded-md text-white font-medium transition ${
              loading ? 'bg-slate-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? 'Analisando...' : 'Analisar Risco'}
          </button>
          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              {error}
            </div>
          )}
        </div>

        {result && (
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
              <h2 className="text-xl font-semibold mb-6 text-slate-700">Análise Gráfica</h2>
              <div className="h-80 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis dataKey="digit" label={{ value: 'Dígito Significativo', position: 'insideBottom', offset: -5 }} stroke="#64748b" />
                    <YAxis label={{ value: 'Frequência (%)', angle: -90, position: 'insideLeft' }} stroke="#64748b" />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '0.375rem' }}
                    />
                    <Legend verticalAlign="top" height={36}/>
                    <Line type="monotone" dataKey="Esperado" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                    <Line type="monotone" dataKey="Observado" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {result.anomalies.length > 0 ? (
              <div className="bg-white p-6 rounded-lg shadow-sm border border-red-100">
                <div className="flex items-center mb-4 text-red-700">
                  <AlertCircle className="w-6 h-6 mr-2" />
                  <h2 className="text-xl font-semibold">Anomalias Detectadas</h2>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {result.anomalies.map((digit) => {
                    const detail = result.details.find(d => d.digit === digit);
                    return (
                      <div key={digit} className="bg-red-50 p-4 rounded-md border border-red-200">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-lg font-bold text-red-800">Dígito {digit}</span>
                          <span className="text-xs font-semibold bg-red-200 text-red-800 px-2 py-1 rounded-full">Desvio &gt; 5%</span>
                        </div>
                        <div className="text-sm text-red-700 space-y-1">
                          <p>Esperado: <span className="font-medium">{(detail.expected * 100).toFixed(1)}%</span></p>
                          <p>Observado: <span className="font-medium">{(detail.observed * 100).toFixed(1)}%</span></p>
                          <p className="mt-2 text-xs">Desvio Absoluto: {(detail.deviation * 100).toFixed(1)}%</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="bg-green-50 p-6 rounded-lg border border-green-200 text-green-800 flex items-center">
                <div className="mr-4 text-2xl">✓</div>
                <div>
                  <h3 className="text-lg font-semibold">Conformidade Verificada</h3>
                  <p>Nenhuma anomalia significativa detectada nos dados fornecidos segundo a Lei de Benford.</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default BenfordDashboard;
