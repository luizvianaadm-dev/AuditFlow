import React, { useState, useEffect } from 'react';
import { CheckCircle, Circle, MessageSquare, AlertOctagon, ChevronDown, ChevronRight, Save } from 'lucide-react';
import { getWorkPapers, generateWorkPapers, updateWorkPaper, addMistatement } from '../services/clientService';

const WorkProgram = ({ engagement }) => {
  const [workpapers, setWorkpapers] = useState({}); // { "Area": [wp, wp] }
  const [loading, setLoading] = useState(true);
  const [expandedAreas, setExpandedAreas] = useState({});
  const [activeWp, setActiveWp] = useState(null); // ID of WP being edited (comment/mistatement)
  const [commentText, setCommentText] = useState('');
  const [mistatement, setMistatement] = useState({ description: '', amount: 0 });

  useEffect(() => {
    if (engagement) {
        loadData();
    }
  }, [engagement]);

  const loadData = async () => {
      setLoading(true);
      try {
          let data = await getWorkPapers(engagement.id);
          // If empty, try generating
          if (Object.keys(data).length === 0) {
              await generateWorkPapers(engagement.id);
              data = await getWorkPapers(engagement.id);
          }
          setWorkpapers(data);
          // Expand all by default
          const allAreas = {};
          Object.keys(data).forEach(area => allAreas[area] = true);
          setExpandedAreas(allAreas);
      } catch (err) {
          console.error("Failed to load workpapers", err);
      } finally {
          setLoading(false);
      }
  };

  const toggleArea = (area) => {
      setExpandedAreas(prev => ({ ...prev, [area]: !prev[area] }));
  };

  const handleStatusChange = async (wpId, currentStatus) => {
      const newStatus = currentStatus === 'completed' ? 'open' : 'completed';
      try {
          await updateWorkPaper(wpId, { status: newStatus });
          // Optimistic update or reload
          loadData();
      } catch (err) {
          alert("Erro ao atualizar status");
      }
  };

  const openEdit = (wp) => {
      setActiveWp(wp);
      setCommentText(wp.comments || '');
      setMistatement({ description: '', amount: 0 });
  };

  const handleSaveComment = async () => {
      if (!activeWp) return;
      try {
          await updateWorkPaper(activeWp.id, { comments: commentText });
          setActiveWp(null);
          loadData();
      } catch (err) {
          alert("Erro ao salvar comentário");
      }
  };

  const handleAddMistatement = async () => {
      if (!activeWp || !mistatement.description) return;
      try {
          await addMistatement(engagement.id, {
              workpaper_id: activeWp.id,
              description: mistatement.description,
              amount: parseFloat(mistatement.amount),
              type: 'factual'
          });
          alert("Divergência registrada!");
          setActiveWp(null);
          // Ideally reload mistatements too
      } catch (err) {
          alert("Erro ao registrar divergência");
      }
  };

  if (loading) return <div className="p-8 text-center text-slate-500">Carregando Programa de Trabalho...</div>;

  return (
    <div className="space-y-6">
      {Object.entries(workpapers).map(([area, wps]) => (
        <div key={area} className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
          <button
            onClick={() => toggleArea(area)}
            className="w-full flex justify-between items-center p-4 bg-slate-50 hover:bg-slate-100 transition-colors"
          >
            <div className="flex items-center font-bold text-slate-700">
                {expandedAreas[area] ? <ChevronDown className="w-5 h-5 mr-2"/> : <ChevronRight className="w-5 h-5 mr-2"/>}
                {area}
            </div>
            <div className="text-sm text-slate-500">
                {wps.filter(w => w.status === 'completed').length} / {wps.length} Concluídos
            </div>
          </button>

          {expandedAreas[area] && (
              <div className="divide-y divide-slate-100">
                  {wps.map(wp => (
                      <div key={wp.id} className="p-4 hover:bg-slate-50 transition-colors">
                          <div className="flex items-start justify-between">
                              <div className="flex items-start space-x-3 flex-1">
                                  <button
                                    onClick={() => handleStatusChange(wp.id, wp.status)}
                                    className={`mt-1 flex-shrink-0 transition-colors ${wp.status === 'completed' ? 'text-green-600' : 'text-slate-300 hover:text-slate-400'}`}
                                  >
                                      {wp.status === 'completed' ? <CheckCircle className="w-6 h-6" /> : <Circle className="w-6 h-6" />}
                                  </button>
                                  <div>
                                      <p className={`text-sm ${wp.status === 'completed' ? 'text-slate-500 line-through' : 'text-slate-800'}`}>
                                          {wp.description}
                                      </p>
                                      {wp.comments && (
                                          <p className="text-xs text-slate-500 mt-1 italic">
                                              Obs: {wp.comments}
                                          </p>
                                      )}
                                  </div>
                              </div>
                              <div className="flex space-x-2 ml-4">
                                  <button
                                    onClick={() => openEdit(wp)}
                                    className="p-1 text-slate-400 hover:text-secondary rounded"
                                    title="Adicionar Nota"
                                  >
                                      <MessageSquare className="w-4 h-4" />
                                  </button>
                                  <button
                                    onClick={() => openEdit(wp)} // Same modal for now
                                    className="p-1 text-slate-400 hover:text-red-500 rounded"
                                    title="Registrar Divergência"
                                  >
                                      <AlertOctagon className="w-4 h-4" />
                                  </button>
                              </div>
                          </div>
                      </div>
                  ))}
              </div>
          )}
        </div>
      ))}

      {/* Edit Modal */}
      {activeWp && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
              <div className="bg-white rounded-xl shadow-2xl p-6 w-full max-w-lg">
                  <h3 className="text-lg font-bold text-slate-800 mb-4">Detalhes do Procedimento</h3>
                  <p className="text-sm text-slate-600 mb-4 bg-slate-50 p-3 rounded">{activeWp.description}</p>

                  <div className="mb-6">
                      <label className="block text-xs font-bold text-slate-500 uppercase mb-2">Comentários / Papel de Trabalho</label>
                      <textarea
                        className="w-full p-2 border border-slate-300 rounded-md text-sm"
                        rows="3"
                        value={commentText}
                        onChange={(e) => setCommentText(e.target.value)}
                        placeholder="Descreva o teste realizado ou cole referências..."
                      />
                      <button
                        onClick={handleSaveComment}
                        className="mt-2 text-sm text-secondary hover:underline font-medium"
                      >
                          Salvar Comentário
                      </button>
                  </div>

                  <div className="border-t border-slate-200 pt-4">
                      <label className="block text-xs font-bold text-red-500 uppercase mb-2">Registrar Divergência (Mistatement)</label>
                      <div className="grid grid-cols-3 gap-3 mb-2">
                          <div className="col-span-2">
                              <input
                                type="text"
                                className="w-full p-2 border border-slate-300 rounded-md text-sm"
                                placeholder="Descrição do erro encontrado"
                                value={mistatement.description}
                                onChange={(e) => setMistatement({...mistatement, description: e.target.value})}
                              />
                          </div>
                          <div>
                              <input
                                type="number"
                                className="w-full p-2 border border-slate-300 rounded-md text-sm"
                                placeholder="Valor (R$)"
                                value={mistatement.amount}
                                onChange={(e) => setMistatement({...mistatement, amount: e.target.value})}
                              />
                          </div>
                      </div>
                      <button
                        onClick={handleAddMistatement}
                        className="w-full py-2 bg-red-50 text-red-700 hover:bg-red-100 rounded-md text-sm font-medium transition-colors border border-red-200"
                      >
                          Registrar Ponto de Auditoria
                      </button>
                  </div>

                  <button
                    onClick={() => setActiveWp(null)}
                    className="absolute top-4 right-4 text-slate-400 hover:text-slate-600"
                  >
                      ✕
                  </button>
              </div>
          </div>
      )}
    </div>
  );
};

export default WorkProgram;
