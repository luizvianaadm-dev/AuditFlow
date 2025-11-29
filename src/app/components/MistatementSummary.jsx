import React, { useState, useEffect } from 'react';
import { AlertOctagon, CheckCircle, XCircle } from 'lucide-react';
import { getMistatementSummary } from '../services/clientService';

const MistatementSummary = ({ engagement }) => {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [engagement]);

  const loadData = async () => {
      try {
          const data = await getMistatementSummary(engagement.id);
          setSummary(data);
      } catch (err) {
          console.error(err);
      } finally {
          setLoading(false);
      }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Carregando sumário...</div>;
  if (!summary) return <div>Erro ao carregar dados.</div>;

  const materiality = summary.materiality || {};
  const globalMat = materiality.global_materiality || 0;
  const perfMat = materiality.performance_materiality || 0;
  const totalUnadjusted = Math.abs(summary.total_unadjusted); // Use absolute for comparison

  const isMaterial = totalUnadjusted > globalMat;
  const isPervasive = totalUnadjusted > (globalMat * 1.5); // Arbitrary rule for MVP

  return (
    <div className="space-y-6">
        {/* Scorecard */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Total de Erros Não Ajustados</h3>
                <div className={`text-2xl font-bold ${isMaterial ? 'text-red-600' : 'text-slate-800'}`}>
                    R$ {summary.total_unadjusted.toLocaleString()}
                </div>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
                <h3 className="text-sm font-semibold text-slate-500 uppercase mb-2">Materialidade Global</h3>
                <div className="text-2xl font-bold text-slate-800">
                    R$ {globalMat.toLocaleString()}
                </div>
            </div>
            <div className={`p-6 rounded-lg border ${isMaterial ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
                <h3 className={`text-sm font-semibold uppercase mb-2 ${isMaterial ? 'text-red-700' : 'text-green-700'}`}>Conclusão Preliminar</h3>
                <div className={`text-lg font-bold flex items-center ${isMaterial ? 'text-red-800' : 'text-green-800'}`}>
                    {isMaterial ? <XCircle className="w-6 h-6 mr-2" /> : <CheckCircle className="w-6 h-6 mr-2" />}
                    {isMaterial ? (isPervasive ? "Opinião Adversa / Abstenção" : "Opinião com Ressalva") : "Opinião Sem Ressalva"}
                </div>
            </div>
        </div>

        {/* List */}
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50">
                <h3 className="text-lg font-bold text-slate-800 flex items-center">
                    <AlertOctagon className="w-5 h-5 mr-2 text-slate-500" />
                    Detalhamento das Divergências (Mistatements)
                </h3>
            </div>
            <table className="min-w-full divide-y divide-slate-200">
                <thead className="bg-slate-50">
                    <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Descrição</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase">Tipo</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">Valor (R$)</th>
                        <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase">Status</th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-slate-200">
                    {summary.items.length === 0 ? (
                        <tr><td colSpan="4" className="px-6 py-4 text-center text-slate-500">Nenhuma divergência registrada.</td></tr>
                    ) : (
                        summary.items.map(item => (
                            <tr key={item.id}>
                                <td className="px-6 py-4 text-sm text-slate-800">{item.description}</td>
                                <td className="px-6 py-4 text-sm text-slate-600 capitalize">{item.type}</td>
                                <td className="px-6 py-4 text-sm font-medium text-right text-slate-900">{item.amount_divergence.toLocaleString()}</td>
                                <td className="px-6 py-4 text-right">
                                    <span className={`px-2 py-1 rounded-full text-xs font-bold uppercase ${item.status === 'adjusted' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                                        {item.status}
                                    </span>
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    </div>
  );
};

export default MistatementSummary;
