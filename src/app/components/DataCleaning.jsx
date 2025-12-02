import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { Upload, FileDown, ArrowRight, Table } from 'lucide-react';

const DataCleaning = () => {
  const { token } = useAuth();
  const [file, setFile] = useState(null);
  const [previewData, setPreviewData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setPreviewData(null);
      setError(null);
    }
  };

  const handleProcess = async () => {
    if (!file) return;

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/cleaning/preview`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      if (!response.ok) {
        throw new Error('Falha ao processar arquivo');
      }

      const data = await response.json();
      setPreviewData(data);
    } catch (err) {
      console.error(err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!file) return;

    // For download, we trigger the endpoint that returns the file stream
    // Using a simple fetch and blob approach
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${import.meta.env.VITE_API_URL}/cleaning/download`, {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`
            },
            body: formData
        });

        if (!response.ok) throw new Error("Download falhou");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cleaned_${file.name}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (err) {
        setError("Erro ao baixar arquivo: " + err.message);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center gap-2">
        <Table className="h-5 w-5 text-primary" />
        Limpeza de Balancete
      </h2>

      <p className="text-gray-600 mb-6 text-sm">
        Faça o upload do seu arquivo bruto (.csv, .xlsx, .xls) para padronizar colunas e remover linhas inválidas antes de iniciar o mapeamento.
      </p>

      {/* Upload Section */}
      <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center mb-6 hover:bg-gray-50 transition-colors">
        <input
          type="file"
          accept=".csv, .xlsx, .xls"
          onChange={handleFileChange}
          className="hidden"
          id="cleaning-upload"
        />
        <label htmlFor="cleaning-upload" className="cursor-pointer flex flex-col items-center">
            <Upload className="h-10 w-10 text-gray-400 mb-2" />
            <span className="text-primary font-medium">Clique para selecionar o balancete (CSV ou Excel)</span>
            {file && <span className="text-sm text-gray-500 mt-2">Selecionado: {file.name}</span>}
        </label>
      </div>

      <div className="flex gap-4 mb-6">
        <button
          onClick={handleProcess}
          disabled={!file || loading}
          className="bg-primary hover:bg-primary-dark text-white px-4 py-2 rounded flex items-center gap-2 disabled:opacity-50"
        >
          {loading ? 'Processando...' : 'Processar Limpeza'}
        </button>

        {previewData && (
           <button
             onClick={handleDownload}
             className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded flex items-center gap-2"
           >
             <FileDown className="h-4 w-4" />
             Baixar CSV Limpo
           </button>
        )}
      </div>

      {error && (
        <div className="bg-red-50 text-red-600 p-4 rounded mb-6">
          {error}
        </div>
      )}

      {/* Preview Table */}
      {previewData && (
        <div className="mt-6">
           <div className="flex justify-between items-center mb-2">
             <h3 className="font-semibold text-gray-700">Prévia do Resultado ({previewData.total_rows} linhas encontradas)</h3>
             <div className="text-xs text-gray-500">
               Encoding: {previewData.detected_encoding} | Separador: "{previewData.detected_separator}"
             </div>
           </div>

           <div className="overflow-x-auto border rounded">
             <table className="min-w-full divide-y divide-gray-200 text-sm">
               <thead className="bg-gray-50">
                 <tr>
                   {previewData.columns.map(col => (
                     <th key={col} className="px-3 py-2 text-left font-medium text-gray-500 uppercase tracking-wider">
                       {col}
                     </th>
                   ))}
                 </tr>
               </thead>
               <tbody className="bg-white divide-y divide-gray-200">
                 {previewData.preview.map((row, idx) => (
                   <tr key={idx}>
                     {previewData.columns.map(col => (
                       <td key={`${idx}-${col}`} className="px-3 py-2 whitespace-nowrap text-gray-700">
                         {row[col]}
                       </td>
                     ))}
                   </tr>
                 ))}
               </tbody>
             </table>
           </div>

           <div className="mt-4 p-4 bg-blue-50 rounded text-blue-800 text-sm flex gap-2">
               <ArrowRight className="h-5 w-5" />
               <p>
                 <strong>Próximo passo:</strong> Baixe o arquivo limpo acima e utilize-o na aba "Mapeamento Inteligente".
               </p>
           </div>
        </div>
      )}
    </div>
  );
};

export default DataCleaning;
