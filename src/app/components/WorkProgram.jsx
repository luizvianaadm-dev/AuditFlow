import WorkpaperContainer from './WorkpaperContainer';
import { getWorkPapers, generateWorkPapers, updateWorkPaper, addMistatement, getEngagementWorkpapers } from '../services/clientService';

const WorkProgram = ({ engagement }) => {
  const [workpapers, setWorkpapers] = useState({});
  const [loading, setLoading] = useState(true);
  const [expandedAreas, setExpandedAreas] = useState({});
  const [activeWp, setActiveWp] = useState(null); 
  const [commentText, setCommentText] = useState('');
  const [mistatement, setMistatement] = useState({ description: '', amount: 0 });
  const [scopedAccounts, setScopedAccounts] = useState([]);
  const [selectedAccountForWp, setSelectedAccountForWp] = useState(null); // Account Object

  useEffect(() => {
    if (engagement) {
        loadData();
    }
  }, [engagement]);

  const loadData = async () => {
      setLoading(true);
      try {
          // 1. Load Risk Matrix Scoping (Using the GET /risk-matrix endpoint directly or via helper?)
          // We can use the endpoint mapping from RiskMatrix.jsx
          const riskResponse = await fetch(`${import.meta.env.VITE_API_URL || 'https://auditflow-api.railway.app'}/engagements/${engagement.id}/risk-matrix`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('auditflow_token')}` }
          });
          if (riskResponse.ok) {
              const riskData = await riskResponse.json();
              if (riskData.scoping) {
                  // Filter for execution? Or show all? Show Significant/Key.
                  const executionScope = riskData.scoping.filter(s => 
                      s.classification === 'Significant' || s.classification === 'Key Item' || s.strategy === 'Substantive'
                  );
                  setScopedAccounts(executionScope);
              }
          }

          // 2. Load General Workpapers
          let data = await getWorkPapers(engagement.id);
          if (Object.keys(data).length === 0) {
              await generateWorkPapers(engagement.id);
              data = await getWorkPapers(engagement.id);
          }
          setWorkpapers(data);
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
      } catch (err) {
          alert("Erro ao registrar divergência");
      }
  };

  if (selectedAccountForWp) {
      return (
          <WorkpaperContainer 
             engagement={engagement} 
             account={selectedAccountForWp} 
             onBack={() => setSelectedAccountForWp(null)} 
          />
      );
  }

  if (loading) return <div className="p-8 text-center text-slate-500">Carregando Programa de Trabalho...</div>;

  return (
    <div className="space-y-8">
      
      {/* SECTION 1: ACCOUNT TESTING (New) */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
          <div className="p-4 bg-indigo-50 border-b border-indigo-100">
              <h3 className="font-bold text-indigo-900 flex items-center">
                  <CheckCircle className="w-5 h-5 mr-2 text-indigo-600" />
                  Auditoria de Saldos (Contas Significativas)
              </h3>
              <p className="text-xs text-indigo-700 mt-1">
                  Definido na Matriz de Riscos. Clique para abrir os procedimentos.
              </p>
          </div>
          <div className="divide-y divide-slate-100">
              {scopedAccounts.length === 0 ? (
                  <div className="p-6 text-center text-slate-500 text-sm">
                      Nenhuma conta significativa identificada na Matriz de Riscos.
                  </div>
              ) : (
                  scopedAccounts.map(acc => (
                      <div 
                        key={acc.account_code} 
                        onClick={() => setSelectedAccountForWp(acc)}
                        className="p-4 hover:bg-slate-50 transition-colors cursor-pointer flex justify-between items-center group"
                      >
                          <div>
                              <div className="font-medium text-slate-800 group-hover:text-primary transition-colors">
                                  {acc.account_code} - {acc.account_name}
                              </div>
                              <div className="text-xs text-slate-500 mt-1 flex space-x-3">
                                  <span>Saldo: R$ {acc.balance.toLocaleString()}</span>
                                  <span className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600">{acc.strategy}</span>
                              </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-slate-300 group-hover:text-primary" />
                      </div>
                  ))
              )}
          </div>
      </div>

      {/* SECTION 2: GENERAL PROCEDURES (Existing) */}
      <div>
        <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wide mb-4 ml-1">Procedimentos Gerais & Controles</h3>
        <div className="space-y-4">
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
        </div>
      </div>

      {/* Edit Modal (Existing) */}
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
