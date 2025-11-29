import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, UploadCloud, FileText } from 'lucide-react';
import { analyzeBenford } from '../services/auditService';
import { getTransactions, uploadTransactionFile } from '../services/clientService';

const BenfordDashboard = ({ engagement }) => {
  const [transactions, setTransactions] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState('');

  // Load existing transactions on mount
  useEffect(() => {
    if (engagement) {
        loadTransactions();
    }
  }, [engagement]);

  const loadTransactions = async () => {
      setLoading(true);
      try {
          const data = await getTransactions(engagement.id);
          setTransactions(data);
          // If we have data, we can auto-analyze or let user click analyze
          // Let's auto-analyze if data exists
          if (data.length > 0) {
              performAnalysis(data.map(t => t.amount));
          }
      } catch (err) {
          console.error(err);
          setError("Falha ao carregar transações.");
      } finally {
          setLoading(false);
      }
  };

  const performAnalysis = async (values) => {
      setAnalyzing(true);
      try {
        const data = await analyzeBenford(values);
        setResult(data);
      } catch (err) {
          setError(err.message);
      } finally {
          setAnalyzing(false);
      }
  };

  const handleFileUpload = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setLoading(true);
      setError('');
      try {
          await uploadTransactionFile(engagement.id, file);
          await loadTransactions(); // Reload and analyze
      } catch (err) {
          setError("Erro no upload: " + err.message);
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

  if (!engagement) return <div>Selecione uma auditoria.</div>;

  return (
    <div className="p-6 bg-gray-50 min-h-screen font-sans text-gray-800">
      <div className="max-w-6xl mx-auto">
        <header className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">Análise de Benford</h1>
          <p className="text-slate-600 mt-2">Auditoria: <span className="font-semibold">{engagement.name}</span> ({engagement.year})</p>
        </header>

        {/* Upload Section */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 mb-8">
          <div className="flex justify-between items-center mb-4">
             <h2 className="text-xl font-semibold text-slate-700">Dados da Auditoria</h2>
             <span className="text-sm text-slate-500">{transactions.length} transações carregadas</span>
          </div>

          {transactions.length === 0 ? (
              <div className="border-2 border-dashed border-slate-300 rounded-lg p-10 text-center hover:bg-slate-50 transition-colors">
                  <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                  <p className="text-slate-600 mb-4">Nenhum dado encontrado. Faça upload do razão contábil (CSV).</p>
                  <label className="cursor-pointer bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-light transition-colors font-medium inline-block">
                      Selecionar Arquivo
                      <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
                  </label>
                  <p className="text-xs text-slate-400 mt-2">Colunas requeridas: vendor, amount</p>
              </div>
          ) : (
              <div className="flex items-center space-x-4">
                  <div className="bg-green-50 text-green-700 px-4 py-2 rounded-lg flex items-center border border-green-200">
                      <FileText className="w-5 h-5 mr-2" />
                      Dados carregados com sucesso
                  </div>
                  <label className="cursor-pointer text-primary hover:underline text-sm">
                      Adicionar mais dados (Upload)
                      <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
                  </label>
              </div>
          )}

          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200 flex items-center">
              <AlertCircle className="w-5 h-5 mr-2" />
              {error}
            </div>
          )}
        </div>

        {/* Loading State */}
        {(loading || analyzing) && (
            <div className="text-center py-10">
                <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary mx-auto mb-4"></div>
                <p className="text-slate-500">Processando dados...</p>
            </div>
        )}

        {/* Analysis Results */}
        {result && !loading && !analyzing && (
          <div className="space-y-8 animate-fade-in">
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
