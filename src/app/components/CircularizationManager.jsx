import React, { useState } from 'react';
import { Mail, Briefcase, Building, UploadCloud, Download, Plus, Trash } from 'lucide-react';
import { uploadClientLogo, generateCircularization, downloadCircularizationZip } from '../services/clientService';

const CircularizationManager = ({ engagement, client }) => {
  const [requests, setRequests] = useState([]);
  const [newRequest, setNewRequest] = useState({ type: 'bank', recipient_name: '', recipient_email: '' });
  const [loading, setLoading] = useState(false);

  const handleLogoUpload = async (e) => {
      const file = e.target.files[0];
      if (!file) return;
      try {
          setLoading(true);
          await uploadClientLogo(client.id, file);
          alert("Logotipo enviado com sucesso!");
      } catch (err) {
          alert("Erro no upload do logo: " + err.message);
      } finally {
          setLoading(false);
      }
  };

  const addRequest = () => {
      if (!newRequest.recipient_name) return;
      setRequests([...requests, newRequest]);
      setNewRequest({ type: 'bank', recipient_name: '', recipient_email: '' });
  };

  const removeRequest = (index) => {
      const newReqs = [...requests];
      newReqs.splice(index, 1);
      setRequests(newReqs);
  };

  const handleGenerate = async () => {
      if (requests.length === 0) return;
      setLoading(true);
      try {
          await generateCircularization(engagement.id, requests);
          await downloadCircularizationZip(engagement.id);
          alert("Cartas geradas e baixadas com sucesso!");
      } catch (err) {
          alert("Erro ao gerar cartas: " + err.message);
      } finally {
          setLoading(false);
      }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
      <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-slate-800">Circularização (NBC TA 505)</h2>
          <label className="cursor-pointer flex items-center text-sm text-primary hover:underline">
              <UploadCloud className="w-4 h-4 mr-2" />
              Upload Logo do Cliente
              <input type="file" className="hidden" accept="image/*" onChange={handleLogoUpload} />
          </label>
      </div>

      <div className="bg-slate-50 p-4 rounded-lg border border-slate-200 mb-6">
          <h3 className="text-sm font-semibold text-slate-700 mb-3">Adicionar Destinatário</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
              <div>
                  <label className="block text-xs font-medium text-slate-500 mb-1">Tipo</label>
                  <select
                    value={newRequest.type}
                    onChange={(e) => setNewRequest({...newRequest, type: e.target.value})}
                    className="w-full p-2 border border-slate-300 rounded-md text-sm"
                  >
                      <option value="bank">Banco</option>
                      <option value="legal">Advogado</option>
                      <option value="supplier">Fornecedor</option>
                      <option value="customer">Cliente</option>
                      <option value="representation">Carta de Representação</option>
                  </select>
              </div>
              <div className="md:col-span-1">
                  <label className="block text-xs font-medium text-slate-500 mb-1">Nome / Razão Social</label>
                  <input
                    type="text"
                    value={newRequest.recipient_name}
                    onChange={(e) => setNewRequest({...newRequest, recipient_name: e.target.value})}
                    className="w-full p-2 border border-slate-300 rounded-md text-sm"
                    placeholder="Ex: Banco Itaú S.A."
                  />
              </div>
              <div className="md:col-span-1">
                  <label className="block text-xs font-medium text-slate-500 mb-1">E-mail (Opcional)</label>
                  <input
                    type="email"
                    value={newRequest.recipient_email}
                    onChange={(e) => setNewRequest({...newRequest, recipient_email: e.target.value})}
                    className="w-full p-2 border border-slate-300 rounded-md text-sm"
                    placeholder="contato@banco.com"
                  />
              </div>
              <button
                onClick={addRequest}
                className="px-4 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-md text-sm font-medium flex items-center justify-center"
              >
                  <Plus className="w-4 h-4 mr-1" /> Adicionar
              </button>
          </div>
      </div>

      {requests.length > 0 && (
          <div className="mb-6">
              <table className="min-w-full divide-y divide-slate-200">
                  <thead className="bg-slate-50">
                      <tr>
                          <th className="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Tipo</th>
                          <th className="px-4 py-2 text-left text-xs font-medium text-slate-500 uppercase">Destinatário</th>
                          <th className="px-4 py-2 text-right text-xs font-medium text-slate-500 uppercase">Ação</th>
                      </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-slate-200">
                      {requests.map((req, idx) => (
                          <tr key={idx}>
                              <td className="px-4 py-2 text-sm text-slate-700 capitalize">
                                  {req.type === 'bank' && <span className="flex items-center"><Building className="w-3 h-3 mr-1"/> Banco</span>}
                                  {req.type === 'legal' && <span className="flex items-center"><Briefcase className="w-3 h-3 mr-1"/> Advogado</span>}
                                  {req.type === 'representation' && <span className="flex items-center"><FileText className="w-3 h-3 mr-1"/> Admin</span>}
                                  {!['bank','legal','representation'].includes(req.type) && req.type}
                              </td>
                              <td className="px-4 py-2 text-sm text-slate-800">{req.recipient_name}</td>
                              <td className="px-4 py-2 text-right">
                                  <button onClick={() => removeRequest(idx)} className="text-red-500 hover:text-red-700">
                                      <Trash className="w-4 h-4" />
                                  </button>
                              </td>
                          </tr>
                      ))}
                  </tbody>
              </table>
          </div>
      )}

      <div className="flex justify-end">
          <button
            onClick={handleGenerate}
            disabled={requests.length === 0 || loading}
            className={`flex items-center px-6 py-2 rounded-lg text-white font-bold transition-all ${
                requests.length > 0 ? 'bg-primary hover:bg-primary-light' : 'bg-slate-400 cursor-not-allowed'
            }`}
          >
              {loading ? 'Gerando...' : (
                  <>
                    <Download className="w-5 h-5 mr-2" />
                    Gerar Cartas (PDF)
                  </>
              )}
          </button>
      </div>
    </div>
  );
};

export default CircularizationManager;
