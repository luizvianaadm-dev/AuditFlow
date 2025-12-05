import React, { useState, useEffect } from 'react';
import { UploadCloud, Check, AlertTriangle, ArrowRight, Settings } from 'lucide-react';
import { getMappingContext, uploadTrialBalanceForMapping, saveMappings, setChartMode, saveAsStandard } from '../services/mappingService';

const AccountMapper = ({ engagementId, onComplete, onGoToCleaning }) => {
  const [standardAccounts, setStandardAccounts] = useState([]);
  const [clientAccounts, setClientAccounts] = useState([]); // List of {code, name}
  const [mappings, setMappings] = useState({}); // { "code": standard_account_id }
  const [chartMode, setChartModeState] = useState('standard_auditflow');
  const [step, setStep] = useState(1); // 1: Upload, 2: Map
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (engagementId) {
        loadContext();
    }
  }, [engagementId]);

  const loadContext = async () => {
    try {
      const data = await getMappingContext(engagementId);
      setStandardAccounts(data.standard_accounts);
      setClientAccounts(data.client_accounts);
      setChartModeState(data.chart_mode);

      // Pre-fill mappings
      const initialMappings = {};
      data.mappings.forEach(m => {
          if (m.client_account_code) {
              initialMappings[m.client_account_code] = m.standard_account_id;
          } else if (m.client_description) {
               // Fallback for old mappings or description-only match
               // We need to find the code for this description if possible
               const match = data.client_accounts.find(ca => ca.name === m.client_description);
               if (match) initialMappings[match.code] = m.standard_account_id;
          }
      });
      setMappings(initialMappings);

      if (data.client_accounts.length > 0) {
          setStep(2);
      }
    } catch (err) {
      console.error(err);
      setError("Erro ao carregar contexto de mapeamento.");
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setLoading(true);
    setError('');
    try {
      // Logic change: upload triggers backend parsing, but usually we just want to refresh context
      // The current backend upload returns "unmapped descriptions".
      // We might need to refresh the context after upload to get the full objects.
      await uploadTrialBalanceForMapping(file);
      // After upload, reload context to get new transactions/accounts
      await loadContext();
      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMappingChange = (code, standardId) => {
    setMappings(prev => ({
        ...prev,
        [code]: parseInt(standardId)
    }));
  };

  const handleModeChange = async (mode) => {
      try {
          setLoading(true);
          await setChartMode(engagementId, mode);
          await loadContext(); // Refresh standard accounts list
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  const handleSaveAsStandard = async () => {
      try {
          setLoading(true);
          await saveAsStandard(engagementId);
          await loadContext(); // Should switch to custom mode and reload accounts
          alert("Plano de contas atual definido como Padrão do Cliente!");
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  const handleSave = async () => {
      setLoading(true);

      // Payload: map entries to object
      // We need to send description for backward compat, but code is key
      const payload = Object.entries(mappings).map(([code, id]) => {
          const account = clientAccounts.find(ca => ca.code === code);
          return {
              client_account_code: code,
              client_description: account ? account.name : "Unknown",
              standard_account_id: id
          };
      });

      try {
          await saveMappings(payload);
          alert("Mapeamento salvo com sucesso!");
          if (onComplete) onComplete();
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Processando...</div>;

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-slate-800">Mapeamento Inteligente</h2>

        {step === 2 && (
            <div className="flex items-center space-x-4">
                <div className="flex bg-slate-100 p-1 rounded-lg">
                    <button
                        onClick={() => handleModeChange('standard_auditflow')}
                        className={`px-3 py-1 text-sm rounded-md transition-all ${chartMode === 'standard_auditflow' ? 'bg-white shadow text-primary font-medium' : 'text-slate-500'}`}
                    >
                        Padrão AuditFlow
                    </button>
                    <button
                        onClick={() => handleModeChange('client_custom')}
                        className={`px-3 py-1 text-sm rounded-md transition-all ${chartMode === 'client_custom' ? 'bg-white shadow text-primary font-medium' : 'text-slate-500'}`}
                    >
                        Personalizado (Cliente)
                    </button>
                </div>
                {chartMode === 'standard_auditflow' && (
                     <button onClick={handleSaveAsStandard} className="text-xs text-secondary hover:underline flex items-center">
                         <Settings className="w-3 h-3 mr-1"/>
                         Usar este plano como Padrão
                     </button>
                )}
            </div>
        )}
      </div>

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {step === 1 && (
        <div className="border-2 border-dashed border-slate-300 rounded-lg p-10 text-center hover:bg-slate-50 transition-colors">
            <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <p className="text-slate-600 mb-4">Faça upload do Balancete (CSV/Excel) para iniciar.</p>
            <label className="cursor-pointer bg-primary text-white px-4 py-2 rounded-lg hover:bg-primary-light transition-colors font-medium inline-block">
                Carregar Balancete
                <input type="file" className="hidden" accept=".csv, .xlsx, .xls" onChange={handleFileUpload} />
            </label>
            {onGoToCleaning && (
                <button onClick={onGoToCleaning} className="block mx-auto mt-4 text-sm text-slate-500 underline">
                    Precisa limpar os dados antes?
                </button>
            )}
        </div>
      )}

      {step === 2 && (
        <div>
            <div className="flex items-center mb-4 text-sm text-blue-700 bg-blue-50 p-3 rounded-md border border-blue-200">
                <Check className="w-4 h-4 mr-2" />
                {clientAccounts.length} contas identificadas. {Object.keys(mappings).length} mapeadas.
            </div>

            <div className="overflow-x-auto max-h-[500px] overflow-y-auto border rounded-lg">
                <table className="min-w-full divide-y divide-slate-200 header-fixed">
                    <thead className="bg-slate-50 sticky top-0 z-10">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-1/2">Conta do Cliente</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider w-1/2">
                                Conta Padrão ({chartMode === 'client_custom' ? 'Cliente' : 'AuditFlow'})
                            </th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {clientAccounts.map((account) => (
                            <tr key={account.code} className="hover:bg-slate-50">
                                <td className="px-6 py-3 text-sm text-slate-800">
                                    <div className="font-medium">{account.code}</div>
                                    <div className="text-slate-500 text-xs">{account.name}</div>
                                </td>
                                <td className="px-6 py-3">
                                    <select
                                        className={`block w-full pl-3 pr-10 py-2 text-sm border focus:outline-none focus:ring-1 sm:text-sm rounded-md ${
                                            mappings[account.code]
                                            ? 'border-green-300 bg-green-50 text-green-800'
                                            : 'border-slate-300 text-slate-700'
                                        }`}
                                        onChange={(e) => handleMappingChange(account.code, e.target.value)}
                                        value={mappings[account.code] || ""}
                                    >
                                        <option value="">Selecione...</option>
                                        {standardAccounts.map(sa => (
                                            <option key={sa.id} value={sa.id} style={{ paddingLeft: `${(sa.level || 1) * 10}px` }}>
                                                {sa.code} - {sa.name}
                                            </option>
                                        ))}
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <div className="mt-6 flex justify-end space-x-3">
                <button
                    onClick={() => setStep(1)}
                    className="px-4 py-2 text-slate-600 hover:text-slate-800"
                >
                    Voltar
                </button>
                <button
                    onClick={handleSave}
                    disabled={clientAccounts.length === 0}
                    className="flex items-center px-6 py-2 rounded-lg text-white font-medium bg-green-600 hover:bg-green-700 disabled:opacity-50"
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
