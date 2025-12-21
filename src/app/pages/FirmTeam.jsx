import React, { useState, useEffect } from 'react';
import { UserPlus, Save, Users, Shield, Calendar, Phone, FileText, Briefcase } from 'lucide-react';
import { getDepartments, getJobRoles } from '../services/firmService';
import { inviteUser } from '../services/teamService';

const FirmTeam = () => {
    const [users, setUsers] = useState([]);
    const [departments, setDepartments] = useState([]);
    const [jobRoles, setJobRoles] = useState([]);
    const [showInviteModal, setShowInviteModal] = useState(false);
    const [loading, setLoading] = useState(false);

    // Fetch Structure on Mount
    useEffect(() => {
        const fetchStructure = async () => {
            try {
                const [depts, roles] = await Promise.all([getDepartments(), getJobRoles()]);
                setDepartments(depts);
                setJobRoles(roles);
            } catch (err) {
                console.error("Failed to load firm structure", err);
            }
        };
        fetchStructure();
    }, []);

    // Form State
    const [formData, setFormData] = useState({
        email: '',
        cpf: '',
        phone: '',
        birthday: '',
        admission_date: '',
        department_id: '',
        job_role_id: ''
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleInvite = async (e) => {
        e.preventDefault();
        try {
            // Generate temp int password or expected by backend?
            // Backend schema expects password.
            const tempPassword = Math.random().toString(36).slice(-8) + "Aa1@";

            await inviteUser({
                ...formData,
                password: tempPassword,
                role: 'auditor', // Fixed for now
                position: 'N/A' // Legacy
            });

            alert(`Convite enviado para ${formData.email}. Senha provisória: ${tempPassword}`);
            setShowInviteModal(false);
        } catch (err) {
            alert("Erro ao convidar: " + err.message);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <div className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Gestão de Time</h1>
                    <p className="text-slate-500">Cadastre e gerencie os colaboradores da firma.</p>
                </div>
                <button
                    onClick={() => setShowInviteModal(true)}
                    className="bg-primary hover:bg-primary-light text-white px-4 py-2 rounded-lg flex items-center shadow-sm transition-colors"
                >
                    <UserPlus className="w-4 h-4 mr-2" />
                    Novo Colaborador
                </button>
            </div>

            {/* List of Users - Placeholder for now until getFirmUsers is real */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
                <table className="min-w-full divide-y divide-slate-200">
                    <thead className="bg-slate-50">
                        <tr>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Colaborador</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Cargo / Departamento</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Nível</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Contato</th>
                            <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Status</th>
                        </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-slate-200">
                        {/* Mock Rows to preserve UI until real data */}
                        <tr>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center">
                                    <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-bold">
                                        LV
                                    </div>
                                    <div className="ml-4">
                                        <div className="text-sm font-medium text-slate-900">Luiz Viana</div>
                                        <div className="text-sm text-slate-500">CPF: 123.456.789-00</div>
                                    </div>
                                </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-slate-900">Sócio Fundador</div>
                                <div className="text-xs text-slate-500">Administrativo</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                                    Sócio (Nível 1)
                                </span>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-slate-900">luiz@vorcon.com.br</div>
                                <div className="text-sm text-slate-500">(71) 99999-9999</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                                    Ativo
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            {/* Invite Modal */}
            {showInviteModal && (
                <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                        <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                            <h2 className="text-xl font-bold text-slate-800">Cadastrar Novo Colaborador</h2>
                            <button onClick={() => setShowInviteModal(false)} className="text-slate-400 hover:text-slate-600">
                                ✕
                            </button>
                        </div>

                        <form onSubmit={handleInvite} className="p-6 space-y-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

                                {/* Identity */}
                                <div className="col-span-2">
                                    <h3 className="text-sm font-semibold text-slate-900 mb-3 flex items-center">
                                        <Users className="w-4 h-4 mr-2 text-primary" /> Identificação
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">E-mail Corporativo</label>
                                            <input name="email" type="email" required onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" placeholder="email@firma.com.br" />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">CPF</label>
                                            <input name="cpf" type="text" required onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" placeholder="000.000.000-00" />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Telefone / WhatsApp</label>
                                            <input name="phone" type="text" onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" placeholder="(00) 00000-0000" />
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Data de Nascimento</label>
                                            <input name="birthday" type="date" onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                                        </div>
                                    </div>
                                </div>

                                {/* Role & Dept */}
                                <div className="col-span-2">
                                    <h3 className="text-sm font-semibold text-slate-900 mb-3 flex items-center">
                                        <Briefcase className="w-4 h-4 mr-2 text-primary" /> Cargo e Departamento
                                    </h3>
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Cargo (Função)</label>
                                            <select name="job_role_id" required onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary">
                                                <option value="">Selecione um Cargo</option>
                                                {jobRoles.map(role => (
                                                    <option key={role.id} value={role.id}>{role.name} (Nível {role.level})</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Departamento</label>
                                            <select name="department_id" required onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary">
                                                <option value="">Selecione um Departamento</option>
                                                {departments.map(dept => (
                                                    <option key={dept.id} value={dept.id}>{dept.name}</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-sm font-medium text-slate-700 mb-1">Data de Admissão</label>
                                            <input name="admission_date" type="date" required onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                                        </div>
                                    </div>
                                </div>

                            </div>

                            <div className="pt-4 border-t border-slate-100 flex justify-end space-x-3">
                                <button
                                    type="button"
                                    onClick={() => setShowInviteModal(false)}
                                    className="px-4 py-2 text-slate-700 hover:bg-slate-50 rounded-lg border border-slate-300"
                                >
                                    Cancelar
                                </button>
                                <button
                                    type="submit"
                                    className="px-4 py-2 bg-secondary hover:bg-secondary-dark text-white rounded-lg font-medium shadow-sm"
                                >
                                    Cadastrar e Enviar Acesso
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FirmTeam;
