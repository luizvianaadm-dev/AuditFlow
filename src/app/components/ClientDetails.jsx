import React, { useEffect, useState } from 'react';
import { Plus, FolderOpen, Calendar, ArrowLeft, Settings, Lock } from 'lucide-react';
import { getEngagements, createEngagement, getClientAcceptance } from '../services/clientService';
import AccountMapper from './AccountMapper';
import AcceptanceChecklist from './AcceptanceChecklist';

const ClientDetails = ({ client, onBack, onSelectEngagement }) => {
  const [engagements, setEngagements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showMapper, setShowMapper] = useState(false);
  const [newEngagement, setNewEngagement] = useState({ name: '', year: new Date().getFullYear() });

  // Acceptance State
  const [acceptanceStatus, setAcceptanceStatus] = useState('pending');

  useEffect(() => {
    loadData();
  }, [client]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [engData, accData] = await Promise.all([
          getEngagements(client.id),
          getClientAcceptance(client.id)
      ]);
      setEngagements(engData);
      if (accData) setAcceptanceStatus(accData.status);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newEngagement.name.trim()) return;
    try {
      await createEngagement(client.id, newEngagement.name, parseInt(newEngagement.year));
      setNewEngagement({ name: '', year: new Date().getFullYear() });
      setShowModal(false);
      // Reload only engagements
      const data = await getEngagements(client.id);
      setEngagements(data);
    } catch (error) {
      alert("Erro ao criar auditoria");
    }
  };

  const isAccepted = acceptanceStatus === 'approved';

  if (loading) return <div className="p-8 text-center text-slate-500">Carregando detalhes...</div>;

  if (showMapper) {
      return (
          <div className="p-6 max-w-5xl mx-auto">
              <button
                onClick={() => setShowMapper(false)}
                className="flex items-center text-slate-500 hover:text-primary mb-6 transition-colors"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Voltar para Detalhes do Cliente
              </button>
              <AccountMapper onComplete={() => setShowMapper(false)} />
          </div>
      )
  }

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <button
        onClick={onBack}
        className="flex items-center text-slate-500 hover:text-primary mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Voltar para Clientes
      </button>

      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">{client.name}</h1>
          <p className="text-slate-500">Gerencie as auditorias deste cliente</p>
        </div>
        <div className="flex space-x-3">
            <button
                onClick={() => setShowMapper(true)}
                className="flex items-center px-4 py-2 bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 rounded-lg transition-colors font-medium"
            >
                <Settings className="w-4 h-4 mr-2" />
                Mapear Contas
            </button>

            {/* New Engagement Button - Disabled if not accepted */}
            <div className="relative group">
                <button
                    onClick={() => isAccepted && setShowModal(true)}
                    disabled={!isAccepted}
                    className={`flex items-center px-4 py-2 text-white rounded-lg transition-colors font-medium ${
                        isAccepted ? 'bg-secondary hover:bg-secondary-dark' : 'bg-slate-300 cursor-not-allowed'
                    }`}
                >
                    {isAccepted ? <Plus className="w-4 h-4 mr-2" /> : <Lock className="w-4 h-4 mr-2" />}
                    Nova Auditoria
                </button>
                {!isAccepted && (
                    <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-48 p-2 bg-slate-800 text-white text-xs rounded shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none text-center">
                        Aprovação do cliente necessária.
                    </div>
                )}
            </div>
        </div>
      </div>

      {/* Acceptance Checklist Section */}
      <AcceptanceChecklist client={client} onStatusChange={setAcceptanceStatus} />

      <h3 className="text-lg font-semibold text-slate-700 mb-4 mt-8">Auditorias Realizadas</h3>

      {engagements.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-dashed border-slate-300">
          <FolderOpen className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-slate-700">Nenhuma auditoria encontrada</h3>
          <p className="text-slate-500 mb-4">
              {isAccepted ? "Crie um novo trabalho para começar." : "Complete a aceitação do cliente para iniciar."}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {engagements.map(eng => (
            <div
              key={eng.id}
              onClick={() => onSelectEngagement(eng)}
              className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 hover:shadow-md hover:border-secondary transition-all cursor-pointer group"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                  <FolderOpen className="w-6 h-6 text-primary" />
                </div>
                <span className="text-xs font-semibold bg-slate-100 text-slate-600 px-2 py-1 rounded-full flex items-center">
                  <Calendar className="w-3 h-3 mr-1" />
                  {eng.year}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-slate-800">{eng.name}</h3>
              <p className="text-sm text-slate-500 mt-2">{eng.transactions?.length || 0} Transações importadas</p>
            </div>
          ))}
        </div>
      )}

      {/* Modal de Criação */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Nova Auditoria</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Nome do Trabalho</label>
                <input
                  type="text"
                  value={newEngagement.name}
                  onChange={(e) => setNewEngagement({...newEngagement, name: e.target.value})}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary outline-none"
                  placeholder="Ex: Auditoria Fiscal 2024"
                  autoFocus
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Ano de Referência</label>
                <input
                  type="number"
                  value={newEngagement.year}
                  onChange={(e) => setNewEngagement({...newEngagement, year: e.target.value})}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary outline-none"
                />
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-secondary text-white rounded-lg hover:bg-secondary-dark transition-colors font-medium"
                >
                  Criar
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientDetails;
