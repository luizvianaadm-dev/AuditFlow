import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileSpreadsheet, CheckCircle, AlertTriangle, ArrowRight } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../context/AuthContext';

const FinancialImport = ({ engagementId }) => {
    const { user } = useAuth();
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Dropzone config
    const onDrop = (acceptedFiles) => {
        setFile(acceptedFiles[0]);
        setError('');
        setPreview(null);
    };

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
            'application/vnd.ms-excel': ['.xls'],
            'text/csv': ['.csv']
        },
        multiple: false
    });

    const handleUpload = async () => {
        if (!file) return;
        setLoading(true);
        setError('');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('engagement_id', engagementId);

        try {
            // Using generic api wrapper or axios directly if wrapper doesn't support form yet
            // Assuming api.post supports FormData logic or we use fetch
            const token = localStorage.getItem('token');
            const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'} /financials/import`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token} `
                },
                body: formData
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Upload failed');
            }

            const data = await response.json();
            setPreview(data);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="p-6 max-w-7xl mx-auto space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold text-slate-800">Importação de Dados Financeiros</h1>
                    <p className="text-slate-500">Fase 2: Alimente o sistema com o Balancete (XLSX, CSV) para iniciar o Planejamento.</p>
                </div>
            </div>

            {/* Upload Area */}
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8">
                <div
                    {...getRootProps()}
                    className={`border - 2 border - dashed rounded - lg p - 12 text - center cursor - pointer transition - colors
            ${isDragActive ? 'border-primary bg-blue-50' : 'border-slate-300 hover:border-primary'}
`}
                >
                    <input {...getInputProps()} />
                    <div className="flex flex-col items-center gap-4">
                        <div className="p-4 bg-blue-100 rounded-full text-primary">
                            <Upload className="w-8 h-8" />
                        </div>
                        <div>
                            <p className="text-lg font-medium text-slate-700">
                                {file ? file.name : "Arraste o Balancete aqui ou clique para selecionar"}
                            </p>
                            <p className="text-sm text-slate-500 mt-1">Suporta .xlsx, .xls e .csv</p>
                        </div>
                    </div>
                </div>

                {file && !preview && (
                    <div className="mt-6 flex justify-end">
                        <button
                            onClick={handleUpload}
                            disabled={loading}
                            className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary-dark disabled:opacity-50 flex items-center gap-2"
                        >
                            {loading ? 'Processando...' : 'Analisar Arquivo'}
                            {!loading && <ArrowRight className="w-4 h-4" />}
                        </button>
                    </div>
                )}

                {error && (
                    <div className="mt-4 p-4 bg-red-50 text-red-700 rounded-lg flex items-center gap-2">
                        <AlertTriangle className="w-5 h-5" />
                        {error}
                    </div>
                )}
            </div>

            {/* Preview Section */}
            {preview && (
                <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden animate-fade-in">
                    <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
                        <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                            <FileSpreadsheet className="w-5 h-5 text-green-600" />
                            Pré-visualização ({preview.total_rows} linhas)
                        </h3>
                        <div className="flex gap-2">
                            <button className="text-sm text-primary hover:underline">Mapear Colunas</button>
                        </div>
                    </div>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left">
                            <thead className="text-xs text-slate-500 uppercase bg-slate-50 border-b">
                                <tr>
                                    {preview.columns.map((col, idx) => (
                                        <th key={idx} className="px-6 py-3 font-semibold">{col}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {preview.preview.map((row, rIdx) => (
                                    <tr key={rIdx} className="border-b hover:bg-slate-50">
                                        {preview.columns.map((col, cIdx) => (
                                            <td key={cIdx} className="px-6 py-3 truncate max-w-xs" title={row[col]}>
                                                {row[col] !== null ? String(row[col]) : ''}
                                            </td>
                                        ))}
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                    <div className="p-4 bg-green-50 border-t border-green-100 text-green-800 flex items-center justify-between">
                        <div className="flex items-center gap-2">
                            <CheckCircle className="w-5 h-5" />
                            <span>Arquivo lido com sucesso! O sistema identificou colunas potenciais para Conta, Descrição e Saldo.</span>
                        </div>
                        <button className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 shadow-sm font-medium">
                            Confirmar Importação & Calcular Materialidade
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default FinancialImport;
