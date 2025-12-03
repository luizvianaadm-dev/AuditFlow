import React, { useState } from 'react';
import { Filter, Play, CheckCircle, AlertTriangle, Download } from 'lucide-react';
import { runRandomSampling, runStratifiedSampling } from '../services/clientService';

const SamplingManager = ({ engagement, onComplete }) => {
  const [method, setMethod] = useState('random'); // random, stratified
  const [params, setParams] = useState({
      sampleSize: 20,
      threshold: 1000,
      sampleSizeBelow: 10
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handleRun = async () => {
      setLoading(true);
      setError('');
      try {
          let data;
          if (method === 'random') {
              data = await runRandomSampling(engagement.id, params.sampleSize);
          } else {
              data = await runStratifiedSampling(engagement.id, params.threshold, params.sampleSizeBelow);
          }
          setResult(data.result);
          if (onComplete) onComplete();
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  const exportSample = () => {
      if (!result) return;
      // Simple CSV export logic for frontend
      const items = result.items;
      const csvContent = "data:text/csv;charset=utf-8,"
          + "ID,Vendor,Amount,Date,Reason\n"
          + items.map(e => `${e.id},${e.vendor},${e.amount},${e.date || ''},${e.reason || 'Random'}`).join("\n");

      const encodedUri = encodeURI(csvContent);
      const link = document.createElement("a");
      link.setAttribute("href", encodedUri);
      link.setAttribute("download", `Amostra_${method}_${engagement.id}.csv`);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <div className="flex items-center mb-6">
          <div className="p-2 bg-purple-50 rounded-lg mr-3">
              <Filter className="w-6 h-6 text-purple-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-800">Amostragem Estatística (NBC TA 530)</h2>
      </div>

      <div className="flex space-x-4 mb-6">
          <button
            onClick={() => setMethod('random')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${method === 'random' ? 'bg-purple-600 text-white' : 'bg-slate-100 text-slate-600'}`}
          >
              Aleatória Simples
          </button>
          <button
            onClick={() => setMethod('stratified')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${method === 'stratified' ? 'bg-purple-600 text-white' : 'bg-slate-100 text-slate-600'}`}
          >
              Estratificada (Valor)
          </button>
      </div>

      <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-6">
          {method === 'random' ? (
              <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Tamanho da Amostra</label>
                  <input
                    type="number"
                    value={params.sampleSize}
                    onChange={(e) => setParams({...params, sampleSize: parseInt(e.target.value)})}
                    className="w-full p-2 border border-slate-300 rounded-md"
                  />
                  <p className="text-xs text-slate-500 mt-1">O sistema selecionará {params.sampleSize} itens aleatoriamente.</p>
              </div>
          ) : (
              <div className="grid grid-cols-2 gap-4">
                  <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Limiar de Valor Significativo (R$)</label>
                      <input
                        type="number"
                        value={params.threshold}
                        onChange={(e) => setParams({...params, threshold: parseFloat(e.target.value)})}
                        className="w-full p-2 border border-slate-300 rounded-md"
                      />
                      <p className="text-xs text-slate-500 mt-1">Todos os itens acima deste valor serão selecionados.</p>
                  </div>
                  <div>
                      <label className="block text-sm font-medium text-slate-700 mb-1">Amostra do Remanescente</label>
                      <input
                        type="number"
                        value={params.sampleSizeBelow}
                        onChange={(e) => setParams({...params, sampleSizeBelow: parseInt(e.target.value)})}
                        className="w-full p-2 border border-slate-300 rounded-md"
                      />
                      <p className="text-xs text-slate-500 mt-1">Itens aleatórios abaixo do limiar.</p>
                  </div>
              </div>
          )}
      </div>

      <div className="flex justify-end mb-6">
          <button
            onClick={handleRun}
            disabled={loading}
            className="flex items-center px-6 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-lg font-bold transition-colors"
          >
              {loading ? 'Processando...' : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Gerar Amostra
                  </>
              )}
          </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {result && (
          <div className="animate-fade-in">
              <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-semibold text-slate-700">Resultado da Seleção</h3>
                  <button onClick={exportSample} className="flex items-center text-sm text-primary hover:underline">
                      <Download className="w-4 h-4 mr-1" /> Exportar CSV
                  </button>
              </div>

              <div className="bg-slate-100 p-3 rounded-md mb-4 flex space-x-4 text-sm">
                  <span>População: <b>{result.population_size}</b></span>
                  <span>Selecionados: <b>{result.items.length}</b></span>
                  {method === 'stratified' && (
                      <span>(Acima do Limiar: {result.high_value_count})</span>
                  )}
              </div>

              <div className="overflow-x-auto border border-slate-200 rounded-lg">
                  <table className="min-w-full divide-y divide-slate-200">
                      <thead className="bg-slate-50">
                          <tr>
                              <th className="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Vendor</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Valor</th>
                              <th className="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Data</th>
                              {method === 'stratified' && <th className="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Motivo</th>}
                          </tr>
                      </thead>
                      <tbody className="bg-white divide-y divide-slate-200">
                          {result.items.slice(0, 10).map((item, idx) => (
                              <tr key={idx}>
                                  <td className="px-4 py-2 text-sm text-slate-700">{item.vendor}</td>
                                  <td className="px-4 py-2 text-sm font-medium text-slate-900">R$ {item.amount?.toLocaleString()}</td>
                                  <td className="px-4 py-2 text-sm text-slate-500">{item.date ? new Date(item.date).toLocaleDateString() : '-'}</td>
                                  {method === 'stratified' && (
                                      <td className="px-4 py-2 text-xs">
                                          <span className={`px-2 py-1 rounded-full ${item.reason === 'High Value' ? 'bg-amber-100 text-amber-800' : 'bg-slate-100 text-slate-600'}`}>
                                              {item.reason}
                                          </span>
                                      </td>
                                  )}
                              </tr>
                          ))}
                      </tbody>
                  </table>
                  {result.items.length > 10 && (
                      <div className="p-2 text-center text-xs text-slate-500 bg-slate-50">
                          ...e mais {result.items.length - 10} itens.
                      </div>
                  )}
              </div>
          </div>
      )}
    </div>
  );
};

export default SamplingManager;
