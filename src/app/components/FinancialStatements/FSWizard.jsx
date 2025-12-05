import React, { useState, useEffect } from 'react';
import { ArrowLeft, ArrowRight, Save, Check, FileText, Calendar, Info, BookOpen, Upload, PieChart, FileCheck } from 'lucide-react';
import { getFSContext, updateFSContext, generateFS } from '../../services/fsService';

const FSWizard = ({ engagementId, onBack }) => {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [contextData, setContextData] = useState({});
  const [reportData, setReportData] = useState(null);

  useEffect(() => {
    loadContext();
  }, [engagementId]);

  const loadContext = async () => {
    setLoading(true);
    try {
      const data = await getFSContext(engagementId);
      // Ensure structure matches forms
      setContextData(data.context_data || {});
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const updateData = (block, field, value) => {
    setContextData(prev => ({
      ...prev,
      [block]: {
        ...prev[block],
        [field]: value
      }
    }));
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      await updateFSContext(engagementId, contextData);
    } catch (error) {
      console.error(error);
      alert("Erro ao salvar dados.");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    await handleSave();
    if (step < 7) setStep(step + 1);
  };

  const handleGenerate = async () => {
      setLoading(true);
      try {
          // Save context first
          await updateFSContext(engagementId, contextData);
          // Generate
          const report = await generateFS(engagementId);
          setReportData(report);
          setStep(7);
      } catch (error) {
          console.error(error);
          alert("Erro ao gerar demonstrações: " + error.message);
      } finally {
          setLoading(false);
      }
  };

  const renderStepIndicator = () => (
    <div className="flex justify-between mb-8 overflow-x-auto">
      {[
        { n: 1, label: "Identificação", icon: FileText },
        { n: 2, label: "Período", icon: Calendar },
        { n: 3, label: "Contexto", icon: Info },
        { n: 4, label: "Base Prep.", icon: BookOpen },
        { n: 5, label: "Práticas", icon: FileCheck },
        { n: 6, label: "Balancete", icon: Upload },
        { n: 7, label: "Gerar", icon: PieChart },
      ].map((s) => (
        <div
            key={s.n}
            className={`flex flex-col items-center min-w-[80px] cursor-pointer ${step === s.n ? 'text-primary' : step > s.n ? 'text-green-600' : 'text-slate-400'}`}
            onClick={() => setStep(s.n)}
        >
          <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-2 transition-colors ${
              step === s.n ? 'bg-primary text-white' : step > s.n ? 'bg-green-100 text-green-600' : 'bg-slate-100'
          }`}>
            <s.icon className="w-5 h-5" />
          </div>
          <span className="text-xs font-medium text-center">{s.label}</span>
        </div>
      ))}
    </div>
  );

  const renderStep1 = () => (
      <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-800">1. Identificação da Entidade</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                  <label className="block text-sm font-medium text-slate-700">Razão Social</label>
                  <input
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_1_identificacao?.razao_social || ''}
                    onChange={e => updateData('bloco_1_identificacao', 'razao_social', e.target.value)}
                  />
              </div>
              <div>
                  <label className="block text-sm font-medium text-slate-700">CNPJ</label>
                  <input
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_1_identificacao?.cnpj || ''}
                    onChange={e => updateData('bloco_1_identificacao', 'cnpj', e.target.value)}
                  />
              </div>
              <div>
                  <label className="block text-sm font-medium text-slate-700">Tipo de Entidade</label>
                  <select
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_1_identificacao?.tipo_entidade || ''}
                    onChange={e => updateData('bloco_1_identificacao', 'tipo_entidade', e.target.value)}
                  >
                      <option value="">Selecione...</option>
                      <option value="SA">Sociedade Anônima (S/A)</option>
                      <option value="LTDA">Limitada (Ltda)</option>
                      <option value="OSC">Terceiro Setor (OSC)</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-slate-700">Endereço Completo</label>
                  <textarea
                    className="w-full p-2 border rounded"
                    rows="2"
                    value={contextData.bloco_1_identificacao?.endereco_completo || ''}
                    onChange={e => updateData('bloco_1_identificacao', 'endereco_completo', e.target.value)}
                  />
              </div>
          </div>
      </div>
  );

  const renderStep2 = () => (
      <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-800">2. Período Contábil</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                  <label className="block text-sm font-medium text-slate-700">Início do Exercício</label>
                  <input
                    type="date"
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_2_periodo_contabil?.data_inicio_exercicio || ''}
                    onChange={e => updateData('bloco_2_periodo_contabil', 'data_inicio_exercicio', e.target.value)}
                  />
              </div>
              <div>
                  <label className="block text-sm font-medium text-slate-700">Encerramento do Exercício</label>
                  <input
                    type="date"
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_2_periodo_contabil?.data_encerramento_exercicio || ''}
                    onChange={e => updateData('bloco_2_periodo_contabil', 'data_encerramento_exercicio', e.target.value)}
                  />
              </div>
              <div className="flex items-center">
                  <input
                    type="checkbox"
                    className="mr-2"
                    checked={contextData.bloco_2_periodo_contabil?.tem_comparativo !== false}
                    onChange={e => updateData('bloco_2_periodo_contabil', 'tem_comparativo', e.target.checked)}
                  />
                  <label className="text-sm font-medium text-slate-700">Incluir Período Comparativo</label>
              </div>
          </div>
      </div>
  );

  const renderStep3 = () => (
      <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-800">3. Contexto Operacional (Nota 1)</h3>
          <div>
              <label className="block text-sm font-medium text-slate-700">Descrição da Atividade Principal</label>
              <textarea
                className="w-full p-2 border rounded h-24"
                value={contextData.bloco_3_contexto_operacional?.descricao_atividade_principal || ''}
                onChange={e => updateData('bloco_3_contexto_operacional', 'descricao_atividade_principal', e.target.value)}
              />
          </div>
          <div>
              <label className="block text-sm font-medium text-slate-700">Principais Produtos/Serviços</label>
              <textarea
                className="w-full p-2 border rounded h-24"
                value={contextData.bloco_3_contexto_operacional?.principais_produtos_servicos || ''}
                onChange={e => updateData('bloco_3_contexto_operacional', 'principais_produtos_servicos', e.target.value)}
              />
          </div>
          <div>
              <label className="block text-sm font-medium text-slate-700">Continuidade Operacional</label>
              <select
                className="w-full p-2 border rounded"
                value={contextData.bloco_3_contexto_operacional?.continuidade_operacional || 'CONTINUA'}
                onChange={e => updateData('bloco_3_contexto_operacional', 'continuidade_operacional', e.target.value)}
              >
                  <option value="CONTINUA">Continuidade Normal</option>
                  <option value="INCERTEZAS">Com Incertezas Relevantes</option>
                  <option value="RISCO">Risco de Descontinuidade</option>
              </select>
          </div>
      </div>
  );

  const renderStep4 = () => (
      <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-800">4. Base de Preparação (Nota 2)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                  <label className="block text-sm font-medium text-slate-700">Referencial Contábil</label>
                  <select
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_4_base_preparacao?.referencial_contabil || ''}
                    onChange={e => updateData('bloco_4_base_preparacao', 'referencial_contabil', e.target.value)}
                  >
                      <option value="NBC_TG">NBC TG Completa</option>
                      <option value="NBC_TG_1000">NBC TG 1000 (PME)</option>
                  </select>
              </div>
              <div>
                  <label className="block text-sm font-medium text-slate-700">Base de Mensuração</label>
                  <select
                    className="w-full p-2 border rounded"
                    value={contextData.bloco_4_base_preparacao?.base_mensuracao || 'CUSTO_HISTORICO'}
                    onChange={e => updateData('bloco_4_base_preparacao', 'base_mensuracao', e.target.value)}
                  >
                      <option value="CUSTO_HISTORICO">Custo Histórico</option>
                      <option value="VALOR_JUSTO">Valor Justo</option>
                  </select>
              </div>
          </div>
      </div>
  );

  const renderStep5 = () => (
      <div className="space-y-4">
          <h3 className="text-lg font-semibold text-slate-800">5. Práticas Contábeis (Nota 3)</h3>
          <p className="text-sm text-slate-500">Defina os métodos utilizados para avaliação de ativos e passivos.</p>

          <div className="border p-4 rounded bg-slate-50">
              <h4 className="font-medium mb-2">Estoques</h4>
              <label className="block text-sm font-medium text-slate-700">Método de Custeio</label>
              <select
                className="w-full p-2 border rounded"
                value={contextData.bloco_5_praticas_contabeis?.metodo_custeio || 'PEPS'}
                onChange={e => updateData('bloco_5_praticas_contabeis', 'metodo_custeio', e.target.value)}
              >
                  <option value="PEPS">PEPS</option>
                  <option value="MEDIA_POND">Média Ponderada</option>
                  <option value="UEPS">UEPS</option>
              </select>
          </div>

          <div className="border p-4 rounded bg-slate-50">
              <h4 className="font-medium mb-2">Imobilizado</h4>
              <p className="text-xs text-slate-500 mb-2">A tabela de vidas úteis será incluída na nota.</p>
              {/* Table logic simplified for UI */}
          </div>
      </div>
  );

  const renderStep6 = () => (
      <div className="space-y-4 text-center py-10">
          <h3 className="text-lg font-semibold text-slate-800">6. Balancete de Verificação</h3>
          <div className="max-w-md mx-auto bg-blue-50 p-6 rounded-lg border border-blue-100">
              <Check className="w-12 h-12 text-blue-500 mx-auto mb-4" />
              <p className="text-slate-700 mb-4">
                  O sistema utilizará o balancete e o mapeamento atual deste trabalho para gerar os relatórios.
              </p>
              <button onClick={handleGenerate} className="bg-primary text-white px-6 py-3 rounded-lg font-bold hover:bg-primary-dark transition-colors w-full">
                  Gerar Demonstrações
              </button>
          </div>
      </div>
  );

  const renderStep7 = () => {
      if (!reportData) return <div>Carregando relatório...</div>;

      const { balance_sheet, income_statement, notes, validations } = reportData;

      return (
          <div className="space-y-6">
              <h3 className="text-xl font-bold text-slate-800 flex items-center">
                  <Check className="w-6 h-6 text-green-500 mr-2" />
                  Demonstrações Geradas
              </h3>

              <div className="bg-white border rounded-lg shadow-sm">
                  <div className="border-b p-4 bg-slate-50 flex justify-between items-center">
                      <h4 className="font-bold text-slate-700">Validações</h4>
                      <span className={`px-2 py-1 rounded text-xs font-bold ${validations.all_checks_passed ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
                          {validations.all_checks_passed ? 'APROVADO' : 'ATENÇÃO'}
                      </span>
                  </div>
                  <div className="p-4 grid grid-cols-2 gap-4 text-sm">
                      <div className="flex justify-between">
                          <span>Equação Patrimonial (A = P + PL):</span>
                          <span>{validations.accounting_equation ? 'OK' : 'Erro'}</span>
                      </div>
                      <div className="flex justify-between">
                          <span>Conciliação DRE vs DMPL:</span>
                          <span>{validations.dre_dmpl_reconciliation ? 'OK' : 'Erro'}</span>
                      </div>
                  </div>
              </div>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {/* BP */}
                  <div className="border rounded-lg p-4">
                      <h4 className="font-bold text-center border-b pb-2 mb-4 bg-slate-100 -mx-4 -mt-4 p-3 rounded-t-lg">Balanço Patrimonial</h4>
                      <div className="space-y-2 text-sm">
                          <div className="flex justify-between font-bold"><span>ATIVO</span><span>{balance_sheet.ativo.total.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</span></div>
                          <div className="pl-4 flex justify-between"><span>Circulante</span><span>{balance_sheet.ativo.circulante.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span></div>
                          <div className="pl-4 flex justify-between"><span>Não Circulante</span><span>{balance_sheet.ativo.nao_circulante.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span></div>

                          <div className="flex justify-between font-bold mt-4"><span>PASSIVO + PL</span><span>{balance_sheet.passivo.total.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</span></div>
                          <div className="pl-4 flex justify-between"><span>Circulante</span><span>{balance_sheet.passivo.circulante.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span></div>
                          <div className="pl-4 flex justify-between"><span>Não Circulante</span><span>{balance_sheet.passivo.nao_circulante.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span></div>
                          <div className="pl-4 flex justify-between text-blue-600"><span>Patrimônio Líquido</span><span>{balance_sheet.passivo.patrimonio_liquido.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</span></div>
                      </div>
                  </div>

                  {/* DRE */}
                  <div className="border rounded-lg p-4">
                      <h4 className="font-bold text-center border-b pb-2 mb-4 bg-slate-100 -mx-4 -mt-4 p-3 rounded-t-lg">DRE</h4>
                      <div className="space-y-2 text-sm">
                          <div className="flex justify-between"><span>Receita Líquida</span><span>{income_statement.receita_liquida.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</span></div>
                          <div className="flex justify-between font-bold"><span>Lucro Bruto</span><span>{income_statement.lucro_bruto.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</span></div>
                          <div className="flex justify-between text-red-500"><span>Despesas Operacionais</span><span>({income_statement.despesas_operacionais.toLocaleString('pt-BR', {minimumFractionDigits: 2})})</span></div>
                          <div className="flex justify-between font-bold text-lg border-t pt-2 mt-2"><span>Lucro Líquido</span><span>{income_statement.lucro_liquido.toLocaleString('pt-BR', {style: 'currency', currency: 'BRL'})}</span></div>
                      </div>
                  </div>
              </div>

              {/* Notes */}
              <div className="border rounded-lg p-4 bg-slate-50">
                  <h4 className="font-bold mb-2">Notas Explicativas (Prévia)</h4>
                  <div className="space-y-4 text-sm text-slate-700">
                      <div><span className="font-bold">Nota 1:</span> {notes.nota_1}</div>
                      <div><span className="font-bold">Nota 2:</span> {notes.nota_2}</div>
                      <div><span className="font-bold">Nota 3:</span> {notes.nota_3}</div>
                  </div>
              </div>
          </div>
      );
  };

  return (
    <div className="bg-white p-6 rounded-xl shadow-lg border border-slate-200 max-w-5xl mx-auto my-8">
      <div className="flex items-center mb-6">
          <button onClick={onBack} className="mr-4 p-2 hover:bg-slate-100 rounded-full transition-colors">
              <ArrowLeft className="w-5 h-5 text-slate-500" />
          </button>
          <h1 className="text-2xl font-bold text-slate-800">Gerador de Demonstrações Financeiras</h1>
      </div>

      {renderStepIndicator()}

      <div className="min-h-[400px]">
          {loading ? (
              <div className="flex justify-center items-center h-64 text-slate-500">Processando...</div>
          ) : (
              <>
                {step === 1 && renderStep1()}
                {step === 2 && renderStep2()}
                {step === 3 && renderStep3()}
                {step === 4 && renderStep4()}
                {step === 5 && renderStep5()}
                {step === 6 && renderStep6()}
                {step === 7 && renderStep7()}
              </>
          )}
      </div>

      <div className="flex justify-between mt-8 pt-4 border-t border-slate-100">
          <button
            onClick={() => setStep(Math.max(1, step - 1))}
            disabled={step === 1}
            className="px-6 py-2 text-slate-600 hover:bg-slate-50 rounded-lg disabled:opacity-50"
          >
              Anterior
          </button>

          {step < 6 && (
              <button
                onClick={handleNext}
                className="flex items-center px-6 py-2 bg-secondary text-white rounded-lg hover:bg-secondary-dark font-medium shadow-sm transition-all"
              >
                  Próximo
                  <ArrowRight className="w-4 h-4 ml-2" />
              </button>
          )}
      </div>
    </div>
  );
};

export default FSWizard;
