import React, { useEffect, useState } from 'react';
import { Plus, Building, ChevronRight } from 'lucide-react';
import { getClients, createClient } from '../services/clientService';

const ClientList = ({ onSelectClient }) => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newClientName, setNewClientName] = useState('');

  useEffect(() => {
    loadClients();
  }, []);

  const loadClients = async () => {
    try {
      const data = await getClients();
      setClients(data);
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (e) => {
    e.preventDefault();
    if (!newClientName.trim()) return;
    try {
      await createClient(newClientName);
      setNewClientName('');
      setShowModal(false);
      loadClients();
    } catch (error) {
      alert("Erro ao criar cliente");
    }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Carregando clientes...</div>;

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-800">Meus Clientes</h1>
          <p className="text-slate-500">Gerencie seus trabalhos de auditoria</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center px-4 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-lg transition-colors font-medium"
        >
          <Plus className="w-4 h-4 mr-2" />
          Novo Cliente
        </button>
      </div>

      {clients.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-xl border border-dashed border-slate-300">
          <Building className="w-12 h-12 text-slate-300 mx-auto mb-3" />
          <h3 className="text-lg font-medium text-slate-700">Nenhum cliente encontrado</h3>
          <p className="text-slate-500 mb-4">Comece cadastrando seu primeiro cliente.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {clients.map(client => (
            <div
              key={client.id}
              onClick={() => onSelectClient(client)}
              className="bg-white p-6 rounded-xl shadow-sm border border-slate-200 hover:shadow-md hover:border-secondary transition-all cursor-pointer group"
            >
              <div className="flex justify-between items-start">
                <div className="p-2 bg-blue-50 rounded-lg group-hover:bg-blue-100 transition-colors">
                  <Building className="w-6 h-6 text-primary" />
                </div>
                <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-secondary" />
              </div>
              <h3 className="text-lg font-semibold text-slate-800 mt-4">{client.name}</h3>
              <p className="text-sm text-slate-500 mt-1">{client.engagements?.length || 0} Auditorias</p>
            </div>
          ))}
        </div>
      )}

      {/* Modal de Criação */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-md">
            <h2 className="text-xl font-bold text-slate-800 mb-4">Novo Cliente</h2>
            <form onSubmit={handleCreate}>
              <div className="mb-4">
                <label className="block text-sm font-medium text-slate-700 mb-1">Nome da Empresa</label>
                <input
                  type="text"
                  value={newClientName}
                  onChange={(e) => setNewClientName(e.target.value)}
                  className="w-full p-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-secondary outline-none"
                  placeholder="Ex: Indústrias ACME Ltda"
                  autoFocus
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

export default ClientList;
