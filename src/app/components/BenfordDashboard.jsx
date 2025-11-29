import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, UploadCloud, FileText, Play, History, RotateCcw, Download } from 'lucide-react';
import { getTransactions, uploadTransactionFile, runBenfordAnalysis, getAnalysisResults, downloadReport } from '../services/clientService';

const BenfordDashboard = ({ engagement }) => {
  const [transactions, setTransactions] = useState([]);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('analysis'); // 'analysis', 'history'

  useEffect(() => {
    if (engagement) {
        loadTransactions();
        loadHistory();
    }
  }, [engagement]);

  const loadTransactions = async () => {
      setLoading(true);
      try {
          const data = await getTransactions(engagement.id);
          setTransactions(data);
      } catch (err) {
          console.error(err);
          setError("Falha ao carregar transações.");
      } finally {
          setLoading(false);
      }
  };

  const loadHistory = async () => {
      try {
          const data = await getAnalysisResults(engagement.id);
          setHistory(data);
      } catch (err) {
          console.error("Failed to load history", err);
      }
  };

  const handleRunAnalysis = async () => {
      setAnalyzing(true);
      setError('');
      try {
        const data = await runBenfordAnalysis(engagement.id);
        setResult(data.result);
        loadHistory(); // Refresh history list
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
          await loadTransactions();
      } catch (err) {
          setError("Erro no upload: " + err.message);
      } finally {
          setLoading(false);
      }
  };

  const handleViewResult = (item) => {
      setResult(item.result);
      setActiveTab('analysis');
  };

  const handleDownloadReport = async () => {
      setDownloading(true);
      try {
          await downloadReport(engagement.id, engagement.name);
      } catch (err) {
          alert("Erro ao baixar relatório: " + err.message);
      } finally {
          setDownloading(false);
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
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row gap-6">

        {/* Main Content */}
        <div className="flex-1">
            <header className="mb-8 flex justify-between items-center">
            <div>
                <h1 className="text-3xl font-bold text-slate-800">Análise de Benford</h1>
                <p className="text-slate-600 mt-2">Auditoria: <span className="font-semibold">{engagement.name}</span> ({engagement.year})</p>
            </div>
            <div className="flex space-x-2">
                <button
                    onClick={handleDownloadReport}
                    disabled={downloading}
                    className="flex items-center px-4 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg transition-colors font-medium shadow-sm"
                >
                    {downloading ? <RotateCcw className="w-4 h-4 mr-2 animate-spin"/> : <Download className="w-4 h-4 mr-2"/>}
                    Exportar PDF
                </button>
                <div className="h-10 w-px bg-slate-300 mx-2"></div>
                <button
                    onClick={() => setActiveTab('analysis')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'analysis' ? 'bg-primary text-white' : 'bg-white text-slate-600 border border-slate-200'}`}
                >
                    Análise Atual
                </button>
                <button
                    onClick={() => setActiveTab('history')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${activeTab === 'history' ? 'bg-primary text-white' : 'bg-white text-slate-600 border border-slate-200'}`}
                >
                    Histórico
                </button>
            </div>
            </header>

            {/* Upload Section (Always visible if needed) */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 mb-8">
            <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold text-slate-700">Dados da Auditoria</h2>
                <div className="flex items-center space-x-4">
                    <span className="text-sm text-slate-500">{transactions.length} transações</span>
                    {transactions.length > 0 && (
                        <button
                            onClick={handleRunAnalysis}
                            disabled={analyzing}
                            className={`flex items-center px-4 py-2 bg-secondary text-white rounded-lg hover:bg-secondary-dark transition-colors font-medium ${analyzing ? 'opacity-70 cursor-wait' : ''}`}
                        >
                            {analyzing ? <RotateCcw className="w-4 h-4 mr-2 animate-spin"/> : <Play className="w-4 h-4 mr-2"/>}
                            Executar Análise
                        </button>
                    )}
                </div>
            </div>

            {transactions.length === 0 ? (
                <div className="border-2 border-dashed border-slate-300 rounded-lg p-10 text-center hover:bg-slate-50 transition-colors">
                    <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
                    <p className="text-slate-600 mb-4">Faça upload do razão contábil (CSV) para começar.</p>
                    <label className="cursor-pointer bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-light transition-colors font-medium inline-block">
                        Selecionar Arquivo
                        <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
                    </label>
                </div>
            ) : (
                <div className="flex items-center space-x-4">
                    <div className="bg-green-50 text-green-700 px-4 py-2 rounded-lg flex items-center border border-green-200">
                        <FileText className="w-5 h-5 mr-2" />
                        Dados carregados
                    </div>
                    <label className="cursor-pointer text-primary hover:underline text-sm">
                        Atualizar arquivo
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

            {/* Analysis View */}
            {activeTab === 'analysis' && result && (
            <div className="space-y-8 animate-fade-in">
                <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                <h2 className="text-xl font-semibold mb-6 text-slate-700">Resultado Gráfico</h2>
                <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={chartData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                        <XAxis dataKey="digit" label={{ value: 'Dígito', position: 'insideBottom', offset: -5 }} stroke="#64748b" />
                        <YAxis label={{ value: '%', angle: -90, position: 'insideLeft' }} stroke="#64748b" />
                        <Tooltip contentStyle={{ backgroundColor: '#fff', border: '1px solid #e2e8f0', borderRadius: '0.375rem' }} />
                        <Legend verticalAlign="top" height={36}/>
                        <Line type="monotone" dataKey="Esperado" stroke="#3b82f6" strokeWidth={2} dot={{ r: 4 }} />
                        <Line type="monotone" dataKey="Observado" stroke="#ef4444" strokeWidth={2} dot={{ r: 4 }} />
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
                    <h3 className="text-lg font-semibold">Sem Anomalias</h3>
                    <p>A distribuição segue a Lei de Benford.</p>
                    </div>
                </div>
                )}
            </div>
            )}

            {activeTab === 'history' && (
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                    <table className="min-w-full divide-y divide-slate-200">
                        <thead className="bg-slate-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Data</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Tipo</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Resultado</th>
                                <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">Ação</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-200">
                            {history.length === 0 ? (
                                <tr>
                                    <td colSpan="4" className="px-6 py-4 text-center text-sm text-slate-500">Nenhum histórico disponível.</td>
                                </tr>
                            ) : (
                                history.map((item) => (
                                    <tr key={item.id} className="hover:bg-slate-50">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                            {new Date(item.executed_at).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-800 capitalize">
                                            {item.test_type}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                                            {item.test_type === 'benford' && (
                                                <span>{item.result.anomalies.length} anomalias</span>
                                            )}
                                            {item.test_type === 'duplicates' && (
                                                <span>{item.result.duplicates.length} grupos suspeitos</span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                                            <button
                                                onClick={() => handleViewResult(item)}
                                                className="text-secondary hover:text-secondary-dark"
                                            >
                                                Visualizar
                                            </button>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
      </div>
    </div>
  );
};

export default BenfordDashboard;
