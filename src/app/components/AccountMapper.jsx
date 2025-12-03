import React, { useState, useEffect } from 'react';
import { UploadCloud, Check, AlertTriangle, ArrowRight } from 'lucide-react';
import { getStandardAccounts, uploadTrialBalanceForMapping, saveMappings } from '../services/mappingService';

const AccountMapper = ({ onComplete, onGoToCleaning }) => {
  const [standardAccounts, setStandardAccounts] = useState([]);
  const [unmappedAccounts, setUnmappedAccounts] = useState([]);
  const [mappings, setMappings] = useState({}); // { "Client Account Name": standard_account_id }
  const [step, setStep] = useState(1); // 1: Upload, 2: Map
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadStandardAccounts();
  }, []);

  const loadStandardAccounts = async () => {
    try {
      const data = await getStandardAccounts();
      // Sort accounts by code for better hierarchy display
      const sorted = data.sort((a, b) => {
          const aParts = a.code.split('.').map(Number);
          const bParts = b.code.split('.').map(Number);
          for (let i = 0; i < Math.max(aParts.length, bParts.length); i++) {
              if ((aParts[i] || 0) < (bParts[i] || 0)) return -1;
              if ((aParts[i] || 0) > (bParts[i] || 0)) return 1;
          }
          return 0;
      });
      setStandardAccounts(sorted);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    try {
      const unmapped = await uploadTrialBalanceForMapping(file);
      if (unmapped.length === 0) {
          alert("Todas as contas deste arquivo já estão mapeadas!");
          if (onComplete) onComplete();
          return;
      }
      setUnmappedAccounts(unmapped);
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMappingChange = (clientAccount, standardId) => {
    setMappings(prev => ({
        ...prev,
        [clientAccount]: parseInt(standardId)
    }));
  };

  const handleSave = async () => {
      setLoading(true);
      const payload = Object.entries(mappings).map(([desc, id]) => ({
          client_description: desc,
          standard_account_id: id
      }));

      try {
          await saveMappings(payload);
          alert("Mapeamento salvo com sucesso!");
          if (onComplete) onComplete();
          setStep(1);
          setUnmappedAccounts([]);
          setMappings({});
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Processando...</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <h2 className="text-xl font-bold text-slate-800 mb-4">Mapeamento Inteligente de Contas</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {step === 1 && (
        <div className="border-2 border-dashed border-slate-300 rounded-lg p-10 text-center hover:bg-slate-50 transition-colors relative">
            <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <p className="text-slate-600 mb-4">Faça upload do Balancete (CSV ou Excel) para identificar novas contas.</p>
            <label className="cursor-pointer bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-light transition-colors font-medium inline-block">
                Carregar Balancete
                <input type="file" className="hidden" accept=".csv, .xlsx, .xls" onChange={handleFileUpload} />
            </label>
            <p className="text-xs text-slate-400 mt-2">Coluna obrigatória: 'description' ou 'conta'</p>

            <div className="mt-6 pt-6 border-t border-slate-200">
                <p className="text-sm text-slate-500 mb-2">O arquivo está muito bagunçado?</p>
                <button
                    onClick={onGoToCleaning}
                    className="text-secondary hover:text-secondary-dark text-sm font-medium flex items-center justify-center mx-auto"
                >
                    Ir para Limpeza de Dados
                    <ArrowRight className="w-3 h-3 ml-1" />
                </button>
            </div>
        </div>
      )}

      {step === 2 && (
        <div>
            <div className="flex items-center mb-4 text-sm text-amber-700 bg-amber-50 p-3 rounded-md border border-amber-200">
                <AlertTriangle className="w-4 h-4 mr-2" />
                Foram encontradas {unmappedAccounts.length} contas desconhecidas. Vincule-as ao padrão.
            </div>

            <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Conta do Cliente</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Conta Padrão (AuditFlow)</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {unmappedAccounts.map((account, idx) => (
                            <tr key={idx}>
                                <td className="px-6 py-4 text-sm text-slate-800 font-medium">
                                    {account}
                                </td>
                                <td className="px-6 py-4">
                                    <select
                                        className="block w-full pl-3 pr-10 py-2 text-base border-slate-300 focus:outline-none focus:ring-secondary focus:border-secondary sm:text-sm rounded-md"
                                        onChange={(e) => handleMappingChange(account, e.target.value)}
                                        value={mappings[account] || ""}
                                    >
                                        <option value="">Selecione...</option>
                                        {standardAccounts.map(sa => {
                                            // Determine formatting based on level (approximated by code length)
                                            const level = sa.code.split('.').length;
                                            const indent = "\u00A0\u00A0".repeat(level - 1);
                                            const isBold = level === 1;

                                            return (
                                                <option key={sa.id} value={sa.id} style={{ fontWeight: isBold ? 'bold' : 'normal' }}>
                                                    {indent}{sa.code} - {sa.name}
                                                </option>
                                            );
                                        })}
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="mt-6 flex justify-end">
                <button
                    onClick={handleSave}
                    disabled={Object.keys(mappings).length === 0}
                    className={`flex items-center px-6 py-2 rounded-lg text-white font-medium transition-colors ${
                        Object.keys(mappings).length > 0 ? 'bg-green-600 hover:bg-green-700' : 'bg-slate-400 cursor-not-allowed'
                    }`}
                >
                    <Check className="w-4 h-4 mr-2" />
                    Salvar Mapeamentos
                </button>
            </div>
        </div>
      )}
    </div>
  );
};

export default AccountMapper;
