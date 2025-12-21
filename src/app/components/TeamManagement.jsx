import React, { useState, useEffect } from 'react';
import { Users, Save, CheckCircle, AlertCircle, Search } from 'lucide-react';

const TeamManagement = ({ engagement, onSave }) => {
    const [team, setTeam] = useState([]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [selectedMembers, setSelectedMembers] = useState(new Set());
    const [error, setError] = useState(null);

    // Hardcoded for now if API not ready, but we should try to fetch
    useEffect(() => {
        // In a real scenario, we fetch the Firm's full team and the Engagement's current team
        // For MVP, we'll mock the fetch or use a service if available.
        // Assuming we have a service `getTeam` and `getEngagementTeam` (not yet impl on frontend)
        // We will simulate fetching for now to show the UI.

        // Simulate Fetch
        setTimeout(() => {
            setTeam([
                { id: 1, name: 'Luiz Viana', email: 'luiz@vorcon.com.br', role: 'Partner' },
                { id: 2, name: 'Auditor Senior', email: 'senior@vorcon.com.br', role: 'Senior' },
                { id: 3, name: 'Trainee 01', email: 'trainee@vorcon.com.br', role: 'Trainee' },
            ]);
            // Assume all are selected for demo or none
            setLoading(false);
        }, 500);
    }, [engagement.id]);

    const toggleMember = (id) => {
        const newSelected = new Set(selectedMembers);
        if (newSelected.has(id)) {
            newSelected.delete(id);
        } else {
            newSelected.add(id);
        }
        setSelectedMembers(newSelected);
    };

    const handleSave = async () => {
        setSaving(true);
        try {
            // Call API to save (mocked)
            await new Promise(resolve => setTimeout(resolve, 1000));
            // Call onSave callback
            if (onSave) onSave();
            alert('Equipe atualizada com sucesso!');
        } catch (err) {
            setError('Erro ao salvar equipe.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) return <div className="p-8 text-center text-slate-500">Carregando equipe...</div>;

    return (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200">
            <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                <div>
                    <h2 className="text-xl font-semibold text-slate-800 flex items-center">
                        <Users className="w-5 h-5 mr-2 text-blue-600" />
                        Equipe do Projeto
                    </h2>
                    <p className="text-slate-500 text-sm mt-1">Selecione os auditores alocados para este trabalho.</p>
                </div>
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="flex items-center px-4 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors disabled:opacity-70"
                >
                    {saving ? <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full mr-2"></div> : <Save className="w-4 h-4 mr-2" />}
                    Salvar Equipe
                </button>
            </div>

            <div className="p-6">
                {error && (
                    <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-center">
                        <AlertCircle className="w-5 h-5 mr-2" />
                        {error}
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {team.map(member => (
                        <div
                            key={member.id}
                            onClick={() => toggleMember(member.id)}
                            className={`cursor-pointer p-4 rounded-lg border-2 transition-all flex items-start space-x-3 ${selectedMembers.has(member.id) ? 'border-primary bg-blue-50' : 'border-slate-100 hover:border-blue-200'}`}
                        >
                            <div className={`mt-1 w-5 h-5 rounded border flex items-center justify-center ${selectedMembers.has(member.id) ? 'bg-primary border-primary text-white' : 'border-slate-300 bg-white'}`}>
                                {selectedMembers.has(member.id) && <CheckCircle className="w-3.5 h-3.5" />}
                            </div>
                            <div>
                                <h3 className="font-semibold text-slate-800">{member.name}</h3>
                                <p className="text-sm text-slate-500">{member.role}</p>
                                <p className="text-xs text-slate-400 mt-1">{member.email}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default TeamManagement;
