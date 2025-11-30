import React, { useState, useEffect } from 'react';
import { ShieldCheck, AlertTriangle, Save, Check } from 'lucide-react';
import { getClientAcceptance, saveClientAcceptance } from '../services/clientService';

const AcceptanceChecklist = ({ client, onStatusChange }) => {
  const [form, setForm] = useState({
    independence_check: false,
    integrity_check: false,
    competence_check: false,
    conflict_check: false, // Should be false
    comments: ''
  });
  const [status, setStatus] = useState('pending');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAcceptance();
  }, [client]);

  const loadAcceptance = async () => {
    try {
      const data = await getClientAcceptance(client.id);
      if (data) {
        setForm({
            independence_check: data.independence_check,
            integrity_check: data.integrity_check,
            competence_check: data.competence_check,
            conflict_check: data.conflict_check,
            comments: data.comments || ''
        });
        setStatus(data.status);
        if (onStatusChange) onStatusChange(data.status);
      }
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
      const { name, checked, value, type } = e.target;
      setForm(prev => ({
          ...prev,
          [name]: type === 'checkbox' ? checked : value
      }));
  };

  const handleSave = async () => {
      setLoading(true);
      try {
          const result = await saveClientAcceptance(client.id, form);
          setStatus(result.status);
          if (onStatusChange) onStatusChange(result.status);
          alert(`Formulário salvo. Status: ${result.status.toUpperCase()}`);
      } catch (err) {
          alert("Erro ao salvar: " + err.message);
      } finally {
          setLoading(false);
      }
  };

  if (loading) return <div className="p-4 text-center">Carregando checklist...</div>;

  const isApproved = status === 'approved';

  return (
    <div className={`p-6 rounded-lg border ${isApproved ? 'bg-green-50 border-green-200' : 'bg-amber-50 border-amber-200'} mb-6`}>
      <div className="flex items-center mb-4">
          <ShieldCheck className={`w-6 h-6 mr-2 ${isApproved ? 'text-green-600' : 'text-amber-600'}`} />
          <h2 className={`text-lg font-bold ${isApproved ? 'text-green-800' : 'text-amber-800'}`}>
              Aceitação do Cliente (NBC TA 220)
          </h2>
          <span className={`ml-auto px-3 py-1 rounded-full text-xs font-bold uppercase ${isApproved ? 'bg-green-200 text-green-800' : 'bg-amber-200 text-amber-800'}`}>
              {status === 'approved' ? 'Aprovado' : 'Pendente / Rejeitado'}
          </span>
      </div>

      <div className="space-y-3 mb-6">
          <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                name="independence_check"
                checked={form.independence_check}
                onChange={handleChange}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
              <span className="text-sm text-slate-700">A equipe de auditoria é independente em relação ao cliente?</span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                name="integrity_check"
                checked={form.integrity_check}
                onChange={handleChange}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
              <span className="text-sm text-slate-700">A integridade da administração foi avaliada e considerada satisfatória?</span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                name="competence_check"
                checked={form.competence_check}
                onChange={handleChange}
                className="w-5 h-5 text-primary rounded focus:ring-primary"
              />
              <span className="text-sm text-slate-700">A firma possui recursos e competência para realizar o trabalho?</span>
          </label>

          <label className="flex items-center space-x-3 cursor-pointer">
              <input
                type="checkbox"
                name="conflict_check"
                checked={form.conflict_check}
                onChange={handleChange}
                className="w-5 h-5 text-red-500 rounded focus:ring-red-500"
              />
              <span className="text-sm text-slate-700 font-medium text-red-700">Existe algum conflito de interesses impeditivo? (Deve ser NÃO)</span>
          </label>
      </div>

      <div className="mb-4">
          <label className="block text-xs font-medium text-slate-500 mb-1">Comentários / Justificativas</label>
          <textarea
            name="comments"
            value={form.comments}
            onChange={handleChange}
            className="w-full p-2 border border-slate-300 rounded-md text-sm"
            rows="2"
            placeholder="Observações sobre riscos identificados..."
          />
      </div>

      <button
        onClick={handleSave}
        className="flex items-center px-4 py-2 bg-white border border-slate-300 rounded-lg hover:bg-slate-50 text-slate-700 font-medium text-sm shadow-sm"
      >
        <Save className="w-4 h-4 mr-2" />
        Salvar Avaliação
      </button>
    </div>
  );
};

export default AcceptanceChecklist;
