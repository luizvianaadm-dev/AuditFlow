import React, { useState, useEffect } from 'react';
import { Save, Building, Users, Upload, CreditCard } from 'lucide-react';
import { getDepartments, getJobRoles, getFirmDetails, updateFirmDetails, uploadLetterhead } from '../services/firmService';

const FirmSettings = () => {
    const [activeTab, setActiveTab] = useState('details');
    const [firmData, setFirmData] = useState({
        name: '',
        cnpj: '',
        crc_registration: '',
        cvm_registration: '',
        email_contact: '' // If backend maps it
    });

    const [departments, setDepartments] = useState([]);
    const [jobRoles, setJobRoles] = useState([]);
    const [loading, setLoading] = useState(false);
    const [letterheadUrl, setLetterheadUrl] = useState(null);

    useEffect(() => {
        const fetchDetails = async () => {
            try {
                const firm = await getFirmDetails();
                setFirmData({
                    name: firm.name || '',
                    cnpj: firm.cnpj || '',
                    crc_registration: firm.crc_registration || '',
                    cvm_registration: firm.cvm_registration || '',
                    email_contact: firm.email_contact || ''
                });
                if (firm.firm_letterhead_url) setLetterheadUrl(firm.firm_letterhead_url);
            } catch (err) {
                console.error("Failed to load firm details", err);
            }
        };

        const fetchStructure = async () => {
            try {
                const [depts, roles] = await Promise.all([getDepartments(), getJobRoles()]);
                setDepartments(depts);
                setJobRoles(roles);
            } catch (err) {
                console.error("Failed to load firm structure", err);
            }
        };

        if (activeTab === 'details') fetchDetails();
        if (activeTab === 'structure') fetchStructure();
        if (activeTab === 'branding') fetchDetails(); // Need letterhead url
    }, [activeTab]);

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFirmData(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = async (e) => {
        e.preventDefault();
        try {
            await updateFirmDetails(firmData);
            alert("Dados salvos com sucesso!");
        } catch (err) {
            alert("Erro ao salvar: " + err.message);
        }
    };

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
            const result = await uploadLetterhead(file);
            setLetterheadUrl(result.url);
            alert("Upload realizado com sucesso!");
        } catch (err) {
            alert("Erro no upload: " + err.message);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto">
            <h1 className="text-2xl font-bold text-slate-800 mb-6">Configurações da Firma</h1>

            {/* Tabs */}
            <div className="flex space-x-4 border-b border-slate-200 mb-6">
                <button
                    onClick={() => setActiveTab('details')}
                    className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'details' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'
                        }`}
                >
                    <div className="flex items-center">
                        <Building className="w-4 h-4 mr-2" /> Dados Cadastrais
                    </div>
                </button>
                <button
                    onClick={() => setActiveTab('structure')}
                    className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'structure' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'
                        }`}
                >
                    <div className="flex items-center">
                        <Users className="w-4 h-4 mr-2" /> Departamentos e Cargos
                    </div>
                </button>
                <button
                    onClick={() => setActiveTab('branding')}
                    className={`pb-3 px-4 text-sm font-medium border-b-2 transition-colors ${activeTab === 'branding' ? 'border-primary text-primary' : 'border-transparent text-slate-500 hover:text-slate-700'
                        }`}
                >
                    <div className="flex items-center">
                        <Upload className="w-4 h-4 mr-2" /> Marca e Timbrado
                    </div>
                </button>
            </div>

            {/* Content */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
                {activeTab === 'details' && (
                    <form onSubmit={handleSave} className="space-y-6 max-w-3xl">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div className="col-span-2">
                                <label className="block text-sm font-medium text-slate-700 mb-1">Razão Social</label>
                                <input name="name" value={firmData.name} onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">CNPJ</label>
                                <input name="cnpj" value={firmData.cnpj} onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">CRC da Firma</label>
                                <input name="crc_registration" value={firmData.crc_registration} onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">Registro CVM</label>
                                <input name="cvm_registration" value={firmData.cvm_registration} onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-slate-700 mb-1">E-mail de Contato</label>
                                <input name="email_contact" value={firmData.email_contact} onChange={handleInputChange} className="w-full border-slate-300 rounded-lg focus:ring-primary" />
                            </div>
                        </div>

                        <div className="flex justify-between items-center pt-4 border-t border-slate-200">
                            <button
                                type="button"
                                onClick={async () => {
                                    if (!confirm("Isso tentará corrigir tabelas ausentes no banco de dados. Continuar?")) return;
                                    try {
                                        await import('../services/firmService').then(m => m.fixFirmStructure());
                                        alert("Banco de dados reparado! Tente salvar agora.");
                                    } catch (e) {
                                        alert("Erro ao reparar: " + e.message);
                                    }
                                }}
                                className="text-xs text-red-500 hover:text-red-700 underline flex items-center"
                            >
                                <span className="mr-1">⚠️</span> Problemas ao Salvar? Reparar Banco de Dados
                            </button>

                            <button type="submit" className="bg-primary hover:bg-primary-light text-white px-4 py-2 rounded-lg flex items-center shadow-sm">
                                <Save className="w-4 h-4 mr-2" /> Salvar Alterações
                            </button>
                        </div>
                    </form>
                )
                }

                {
                    activeTab === 'structure' && (
                        <div>
            </div>                    )
                }

            </div
            )    </div>
            )                    activeTab === 'structure' && (
                        <div>
                            <h3 className="text-lg font-semibold text-slate-800 mb-4">Estrutura Organizacional</h3>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                                {/* Departments */}
                                <div>
                                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">Departamentos</h4>
                                    <ul className="divide-y divide-slate-100 border border-slate-200 rounded-lg">
                                        {departments.map(dept => (
                                            <li key={dept.id} className="p-3 flex justify-between items-center text-sm">
                                                <span>{dept.name}</span>
                                                <span className={`px-2 py-0.5 rounded-full text-xs ${dept.is_overhead ? 'bg-orange-100 text-orange-700' : 'bg-green-100 text-green-700'}`}>
                                                    {dept.is_overhead ? 'Overhead' : 'Produtivo'}
                                                </span>
                                            </li>
                                        ))}
                                        {departments.length === 0 && <li className="p-3 text-slate-400 italic">Nenhum departamento carregado.</li>}
                                    </ul>
                                </div>

                                {/* Roles */}
                                <div>
                                    <h4 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">Cargos e Taxas</h4>
                                    <ul className="divide-y divide-slate-100 border border-slate-200 rounded-lg">
                                        {jobRoles.map(role => (
                                            <li key={role.id} className="p-3 flex justify-between items-center text-sm">
                                                <div>
                                                    <div className="font-medium text-slate-900">{role.name}</div>
                                                    <div className="text-xs text-slate-500">Nível {role.level}</div>
                                                </div>
                                                <div className="font-semibold text-slate-700">
                                                    R$ {role.hourly_rate?.toFixed(2)}/h
                                                </div>
                                            </li>
                                        ))}
                                        {jobRoles.length === 0 && <li className="p-3 text-slate-400 italic">Nenhum cargo carregado.</li>}
                                    </ul>
                                </div>
                            </div>
                            <p className="mt-4 text-xs text-slate-500 text-center">
                                * A edição de cargos e departamentos será habilitada em breve.
                            </p>
                        </div>
                    )
                }

                {
                    activeTab === 'branding' && (
                        <div className="text-center py-12">
                            {letterheadUrl ? (
                                <div className="mb-6">
                                    <img src={`${import.meta.env.VITE_API_URL}${letterheadUrl}`} alt="Papel Timbrado" className="max-w-md mx-auto shadow-md border border-slate-200" />
                                    <p className="text-sm text-green-600 font-medium mt-2">Timbrado Atual Ativo</p>
                                </div>
                            ) : (
                                <Upload className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                            )}

                            <h3 className="text-lg font-medium text-slate-900">Papel Timbrado (Letterhead)</h3>
                            <p className="text-slate-500 mb-6">Faça upload do cabeçalho oficial para os relatórios de auditoria.</p>

                            <label className="bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 px-4 py-2 rounded-lg font-medium shadow-sm cursor-pointer inline-block">
                                Selecionar Arquivo (PNG/JPG)
                                <input type="file" accept="image/*" className="hidden" onChange={handleFileUpload} />
                            </label>
                        </div>
                    )
                }
            </div >
        </div >
    );
};

export default FirmSettings;
