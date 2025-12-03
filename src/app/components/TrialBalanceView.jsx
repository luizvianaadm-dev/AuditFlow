import React, { useState, useEffect } from 'react';
import { UploadCloud, Check, AlertTriangle, ArrowRight, Eye, EyeOff, Table } from 'lucide-react';

const TrialBalanceView = ({ engagementId }) => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('original'); // 'original', 'mapped' (future)
  const [uploading, setUploading] = useState(false);

  // Future: Fetch mapped data if needed. For now, only Original Plan is requested.

  const fetchData = async () => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/engagements/${engagementId}/trial-balance`, {
          headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
      });
      if (response.ok) {
          const result = await response.json();
          setData(result);
      }
    } catch (error) {
      console.error(error);
    } finally {
        setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [engagementId]);

  const handleUpload = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      try {
          const res = await fetch(`${import.meta.env.VITE_API_URL}/engagements/${engagementId}/upload-trial-balance-full`, {
              method: 'POST',
              headers: {
                  'Authorization': `Bearer ${localStorage.getItem('token')}`
              },
              body: formData
          });

          if (!res.ok) throw new Error("Falha no upload");

          await fetchData();
          alert("Balancete importado com sucesso!");
      } catch (err) {
          alert(err.message);
      } finally {
          setUploading(false);
      }
  };

  const formatMoney = (val) => {
      return new Intl.NumberFormat('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val || 0);
  };

  if (loading) return <div className="p-4 text-center">Carregando balancete...</div>;

  return (
    <div className="bg-white rounded-lg shadow-sm border border-slate-200 mt-6">
        <div className="p-4 border-b border-slate-200 flex justify-between items-center">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                <Table className="w-5 h-5 text-primary" />
                Balancete de Verificação
            </h3>
            <div className="flex gap-2">
                 <label className="cursor-pointer px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-sm font-medium flex items-center transition-colors">
                    <UploadCloud className="w-4 h-4 mr-2" />
                    {uploading ? 'Enviando...' : 'Importar Balancete Completo'}
                    <input type="file" className="hidden" accept=".csv, .xlsx, .xls" onChange={handleUpload} disabled={uploading} />
                 </label>

                 {/* Toggle View Mode (Placeholder for now as only original is implemented) */}
                 <button
                    className="px-4 py-2 bg-white border border-slate-300 text-slate-600 rounded text-sm font-medium hover:bg-slate-50 transition-colors"
                    onClick={() => setViewMode(viewMode === 'original' ? 'mapped' : 'original')}
                    title="Alternar entre Plano Original e Padronizado (De-Para)"
                 >
                    {viewMode === 'original' ? 'Ver Plano Padronizado' : 'Ver Plano Original'}
                 </button>
            </div>
        </div>

        {data.length === 0 ? (
            <div className="p-12 text-center text-slate-500">
                <p>Nenhum balancete importado para este trabalho.</p>
                <p className="text-sm mt-2">Utilize o botão "Importar Balancete Completo" para começar.</p>
            </div>
        ) : (
            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200 text-sm">
                    <thead className="bg-slate-50">
                        <tr>
                            <th className="px-4 py-3 text-left font-medium text-slate-500 uppercase">Conta</th>
                            <th className="px-4 py-3 text-left font-medium text-slate-500 uppercase">Descrição</th>
                            <th className="px-4 py-3 text-right font-medium text-slate-500 uppercase">Saldo Anterior</th>
                            <th className="px-4 py-3 text-right font-medium text-slate-500 uppercase text-blue-600">Débitos</th>
                            <th className="px-4 py-3 text-right font-medium text-slate-500 uppercase text-red-600">Créditos</th>
                            <th className="px-4 py-3 text-right font-bold text-slate-700 uppercase">Saldo Atual</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-200 bg-white">
                        {data.map((row) => (
                            <tr key={row.id} className="hover:bg-slate-50">
                                <td className="px-4 py-2 text-slate-600 font-mono text-xs">{row.account_code}</td>
                                <td className="px-4 py-2 text-slate-800 font-medium">{row.account_description}</td>
                                <td className="px-4 py-2 text-right text-slate-600">{formatMoney(row.initial_balance)}</td>
                                <td className="px-4 py-2 text-right text-blue-600">{formatMoney(row.debits)}</td>
                                <td className="px-4 py-2 text-right text-red-600">{formatMoney(row.credits)}</td>
                                <td className={`px-4 py-2 text-right font-bold ${row.final_balance < 0 ? 'text-red-700' : 'text-slate-800'}`}>
                                    {formatMoney(row.final_balance)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                    <tfoot className="bg-slate-50 font-bold text-slate-700">
                         <tr>
                             <td colSpan={2} className="px-4 py-3 text-right">TOTAIS</td>
                             <td className="px-4 py-3 text-right">
                                 {formatMoney(data.reduce((acc, r) => acc + (r.initial_balance || 0), 0))}
                             </td>
                             <td className="px-4 py-3 text-right text-blue-600">
                                 {formatMoney(data.reduce((acc, r) => acc + (r.debits || 0), 0))}
                             </td>
                             <td className="px-4 py-3 text-right text-red-600">
                                 {formatMoney(data.reduce((acc, r) => acc + (r.credits || 0), 0))}
                             </td>
                             <td className="px-4 py-3 text-right">
                                 {formatMoney(data.reduce((acc, r) => acc + (r.final_balance || 0), 0))}
                             </td>
                         </tr>
                    </tfoot>
                </table>
            </div>
        )}
    </div>
  );
};

export default TrialBalanceView;
