import React, { useState, useEffect } from 'react';
import { Target, Save, AlertTriangle, FileText, ArrowDown, ArrowUp } from 'lucide-react';
import { API_URL } from '../services/authService';
import { getHeaders } from '../services/clientService';

const RiskMatrix = ({ engagement, onComplete }) => {
    const [scoping, setScoping] = useState([]);
    const [materiality, setMateriality] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all'); // all, significant

    useEffect(() => {
        loadMatrix();
    }, [engagement]);

    const loadMatrix = async () => {
        try {
            setLoading(true);
            const response = await fetch(`${API_URL}/engagements/${engagement.id}/risk-matrix`, {
                headers: getHeaders()
            });
            if (!response.ok) throw new Error("Failed to load Risk Matrix");

            const data = await response.json();
            if (data.error) {
                setError(data.error); // E.g., Materiality not defined
            } else {
                setScoping(data.scoping);
                setMateriality(data.materiality);
            }
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleUpdate = (code, field, value) => {
        const updated = scoping.map(item => {
            if (item.account_code === code) {
                return { ...item, [field]: value };
            }
            return item;
        });
        setScoping(updated);
    };

    const handleSave = async () => {
        try {
            const response = await fetch(`${API_URL}/engagements/${engagement.id}/risk-matrix`, {
                method: 'POST',
                headers: getHeaders(),
                body: JSON.stringify({ scoping })
            });
            if (!response.ok) throw new Error("Failed to save Scoping");
            alert("Matriz de Riscos salva com sucesso!");
            if (onComplete) onComplete();
        } catch (err) {
            alert(err.message);
        }
    };

    if (loading) return <div className="p-6 text-center text-slate-500">Calculando Matriz de Riscos...</div>;

    if (error) return (
        <div className="p-6 bg-red-50 text-red-700 rounded-lg border border-red-200">
            <h3 className="font-bold flex items-center"><AlertTriangle className="w-5 h-5 mr-2" /> Atenção</h3>
            <p>{error}</p>
            <p className="text-sm mt-2">Certifique-se de que a Materialidade foi calculada e salva primeiro.</p>
        </div>
    );

    const filteredScoping = filter === 'all' ? scoping : scoping.filter(s => s.classification === 'Significant' || s.classification === 'Key Item');

    return (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center">
                    <div className="p-2 bg-purple-50 rounded-lg mr-3">
                        <Target className="w-6 h-6 text-purple-600" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-slate-800">Matriz de Riscos (Scoping)</h2>
                        <p className="text-sm text-slate-500">Classificação de Contas Baseada na Materialidade</p>
                    </div>
                </div>
                <div className="flex space-x-2">
                    <select
                        className="border border-slate-300 rounded-lg text-sm p-2"
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                    >
                        <option value="all">Todas as Contas</option>
                        <option value="significant">Somente Significativas</option>
                    </select>
                    <button onClick={handleSave} className="bg-secondary text-white px-4 py-2 rounded-lg text-sm flex items-center hover:bg-secondary-dark">
                        <Save className="w-4 h-4 mr-2" />
                        Salvar Definições
                    </button>
                </div>
            </div>

            {/* Thresholds Header */}
            <div className="grid grid-cols-3 gap-4 mb-6 text-sm">
                <div className="bg-slate-50 p-3 rounded border border-slate-200 text-center">
                    <span className="text-slate-500 block text-xs uppercase">Materialidade Global (PM)</span>
                    <span className="font-bold text-slate-800">R$ {materiality?.pm?.toLocaleString()}</span>
                </div>
                <div className="bg-slate-50 p-3 rounded border border-slate-200 text-center">
                    <span className="text-slate-500 block text-xs uppercase">Performance (TE)</span>
                    <span className="font-bold text-slate-800">R$ {materiality?.te?.toLocaleString()}</span>
                    <span className="text-xs text-orange-600 font-medium block mt-1">Acima disto = Significativo</span>
                </div>
                <div className="bg-slate-50 p-3 rounded border border-slate-200 text-center">
                    <span className="text-slate-500 block text-xs uppercase">Trivial (CTT)</span>
                    <span className="font-bold text-slate-800">R$ {materiality?.ctt?.toLocaleString()}</span>
                    <span className="text-xs text-green-600 font-medium block mt-1">Abaixo disto = Trivial</span>
                </div>
            </div>

            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="bg-slate-50 text-slate-600 font-semibold border-b">
                        <tr>
                            <th className="p-3">Conta</th>
                            <th className="p-3 text-right">Saldo</th>
                            <th className="p-3 text-center">% PM</th>
                            <th className="p-3">Classificação (Auto)</th>
                            <th className="p-3">Risco Inerente</th>
                            <th className="p-3">Estratégia de Teste</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {filteredScoping.map(item => (
                            <tr key={item.account_code} className={item.classification === 'Significant' || item.classification === 'Key Item' ? 'bg-purple-50/30' : ''}>
                                <td className="p-3">
                                    <div className="font-medium text-slate-800">{item.account_name}</div>
                                    <div className="text-xs text-slate-400">{item.account_code} ({item.account_type})</div>
                                </td>
                                <td className="p-3 text-right font-mono text-slate-700">
                                    {item.balance.toLocaleString()}
                                </td>
                                <td className="p-3">
                                    <div className="flex items-center justify-center">
                                        <div className="w-16 bg-slate-200 rounded-full h-1.5 mr-2">
                                            <div
                                                className={`h-1.5 rounded-full ${item.pct_materiality > 1 ? 'bg-red-500' : item.pct_materiality > 0.75 ? 'bg-orange-500' : 'bg-green-500'}`}
                                                style={{ width: `${Math.min(item.pct_materiality * 100, 100)}%` }}
                                            />
                                        </div>
                                        <span className="text-xs text-slate-500">{(item.pct_materiality * 100).toFixed(0)}%</span>
                                    </div>
                                </td>
                                <td className="p-3">
                                    <span className={`px-2 py-1 rounded-full text-xs font-medium 
                                        ${item.classification === 'Key Item' ? 'bg-red-100 text-red-700' :
                                            item.classification === 'Significant' ? 'bg-orange-100 text-orange-700' :
                                                item.classification === 'Relevant' ? 'bg-blue-50 text-blue-700' : 'bg-slate-100 text-slate-500'
                                        }`}>
                                        {item.classification}
                                    </span>
                                </td>
                                <td className="p-3">
                                    <select
                                        className="border border-slate-300 rounded text-xs p-1 bg-white focus:ring-2 focus:ring-purple-500 outline-none"
                                        value={item.risk}
                                        onChange={(e) => handleUpdate(item.account_code, 'risk', e.target.value)}
                                    >
                                        <option value="High">Alto</option>
                                        <option value="Medium">Médio</option>
                                        <option value="Low">Baixo</option>
                                    </select>
                                </td>
                                <td className="p-3">
                                    <select
                                        className="border border-slate-300 rounded text-xs p-1 bg-white focus:ring-2 focus:ring-purple-500 outline-none w-32"
                                        value={item.strategy}
                                        onChange={(e) => handleUpdate(item.account_code, 'strategy', e.target.value)}
                                    >
                                        <option value="Substantive">Substantivo</option>
                                        <option value="Analytical">Analítico (Control)</option>
                                        <option value="None">Nenhum</option>
                                    </select>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
            <div className="mt-4 text-xs text-slate-400 text-center">
                * Classificação baseada em comparação direta com TE (Performance) e CTT (Trivial). Ajuste manual disponível.
            </div>
        </div>
    );
};

export default RiskMatrix;
