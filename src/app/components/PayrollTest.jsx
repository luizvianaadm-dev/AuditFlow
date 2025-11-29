import React, { useState } from 'react';
import { UploadCloud, CheckCircle, AlertTriangle, Play, FileText } from 'lucide-react';
import { uploadPayroll, runPayrollReconciliation } from '../services/clientService';

const PayrollTest = ({ engagement }) => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [fileUploaded, setFileUploaded] = useState(false);

  const handleFileUpload = async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      setLoading(true);
      setError('');
      try {
          await uploadPayroll(engagement.id, file);
          setFileUploaded(true);
          alert("Resumo da folha carregado com sucesso!");
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  const handleRun = async () => {
      setLoading(true);
      setError('');
      try {
          const data = await runPayrollReconciliation(engagement.id);
          setResult(data.result);
      } catch (err) {
          setError(err.message);
      } finally {
          setLoading(false);
      }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <div className="flex items-center mb-6">
          <div className="p-2 bg-pink-50 rounded-lg mr-3">
              <FileText className="w-6 h-6 text-pink-600" />
          </div>
          <h2 className="text-xl font-bold text-slate-800">Recálculo Global da Folha</h2>
      </div>

      {!fileUploaded && !result && (
        <div className="border-2 border-dashed border-slate-300 rounded-lg p-10 text-center hover:bg-slate-50 transition-colors mb-6">
            <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
            <p className="text-slate-600 mb-4">Carregue o Resumo da Folha (CSV) do sistema de RH.</p>
            <label className="cursor-pointer bg-pink-600 text-white px-4 py-2 rounded-lg hover:bg-pink-700 transition-colors font-medium inline-block">
                Selecionar Arquivo
                <input type="file" className="hidden" accept=".csv" onChange={handleFileUpload} />
            </label>
            <p className="text-xs text-slate-400 mt-2">Colunas: gross_salary, inss, fgts</p>
        </div>
      )}

      {fileUploaded && !result && (
          <div className="text-center mb-6">
              <div className="flex items-center justify-center text-green-600 mb-4">
                  <CheckCircle className="w-6 h-6 mr-2" />
                  <span className="font-medium">Arquivo de Folha pronto para análise.</span>
              </div>
              <button
                onClick={handleRun}
                disabled={loading}
                className="px-6 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-lg font-bold transition-colors"
              >
                  {loading ? 'Processando...' : 'Conciliar com Contabilidade'}
              </button>
          </div>
      )}

      {error && (
        <div className="mb-4 p-3 bg-red-50 text-red-700 rounded-md border border-red-200">
          {error}
        </div>
      )}

      {result && (
          <div className="animate-fade-in space-y-4">
              <div className={`p-4 rounded-lg border ${result.status === 'reconciled' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
                  <h3 className={`text-lg font-bold ${result.status === 'reconciled' ? 'text-green-800' : 'text-red-800'} mb-2`}>
                      {result.status === 'reconciled' ? 'Conciliação Concluída' : 'Divergência Encontrada'}
                  </h3>
                  <p className="text-sm text-slate-600">
                      Diferença apurada: <b>R$ {result.difference?.toLocaleString()}</b>
                  </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 rounded-lg">
                      <h4 className="text-sm font-semibold text-slate-500 uppercase mb-2">Sistema de RH (Folha)</h4>
                      <div className="text-xl font-bold text-slate-800">
                          R$ {(result.payroll_system_gross || 0).toLocaleString()}
                      </div>
                      <p className="text-xs text-slate-500">Salário Bruto Total</p>
                  </div>
                  <div className="p-4 bg-slate-50 rounded-lg">
                      <h4 className="text-sm font-semibold text-slate-500 uppercase mb-2">Contabilidade (Razão)</h4>
                      <div className="text-xl font-bold text-slate-800">
                          R$ {(result.accounting_total || 0).toLocaleString()}
                      </div>
                      <p className="text-xs text-slate-500">Despesas com Pessoal Mapeadas</p>
                  </div>
              </div>
          </div>
      )}
    </div>
  );
};

export default PayrollTest;
