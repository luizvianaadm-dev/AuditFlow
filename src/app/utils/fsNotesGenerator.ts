export interface FSContextInput {
  razao_social: string;
  tipo_entidade: string;
  regime_tributacao: string;
  contexto: {
    endereco_simplificado?: string;
    descricao_atividade_principal: string;
    principais_produtos_servicos: string;
    principais_mercados: string[];
    publico_alvo: string[];
    unidades_filiais?: string;
    data_encerramento_exercicio: string;
    fatos_relevantes_periodo?: string;
  };
  base_preparacao: {
    base_mensuracao: string;
    moeda_apresentacao: string;
    estimativas_contabeis: string[];
  };
  praticas: {
    metodo_custeio?: string;
    // Add other specific practice fields if needed
  };
}

export interface FSNotesOutput {
  nota_1: string;
  nota_2: string;
  nota_3: string;
  validations: {
    consistent: boolean;
    warnings: string[];
  };
}

export const generateFinancialNotes = (input: FSContextInput): FSNotesOutput => {
  const warnings: string[] = [];

  // --- Validação Básica ---
  if (!input.razao_social) warnings.push("Razão Social não informada.");
  if (!input.contexto.descricao_atividade_principal) warnings.push("Atividade principal não descrita.");

  // --- Nota 1: Contexto Operacional ---
  const mercados = input.contexto.principais_mercados?.join(", ") || "mercados diversos";
  const publico = input.contexto.publico_alvo?.join(", ") || "público geral";

  const nota1 = `
A **${input.razao_social}** é uma sociedade ${input.tipo_entidade}, com sede em ${input.contexto.endereco_simplificado || "endereço não informado"}, tendo por objeto social principal ${input.contexto.descricao_atividade_principal}.

Suas operações concentram-se em ${input.contexto.principais_produtos_servicos}, atuando predominantemente nos mercados ${mercados}, com foco em ${publico}. As atividades são desenvolvidas através de ${input.contexto.unidades_filiais || "sua sede"}.

No exercício findo em ${input.contexto.data_encerramento_exercicio}, ${input.contexto.fatos_relevantes_periodo ? `destacam-se os seguintes eventos relevantes: ${input.contexto.fatos_relevantes_periodo}.` : "não houve eventos extraordinários que comprometessem a continuidade."}

As demonstrações financeiras foram preparadas no pressuposto da continuidade normal dos negócios.
  `.trim();

  // --- Nota 2: Base de Preparação ---
  const estimativas = input.base_preparacao.estimativas_contabeis?.join(", ") || "nenhuma estimativa crítica";

  const nota2 = `
As demonstrações financeiras foram preparadas de acordo com as práticas contábeis adotadas no Brasil, incluindo os Pronunciamentos emitidos pelo Comitê de Pronunciamentos Contábeis (CPC).

A base de preparação é o **${input.base_preparacao.base_mensuracao || "Custo Histórico"}**, acrescido ou ajustado, quando aplicável, pela mensuração de determinados ativos e passivos financeiros ao valor justo.

A moeda funcional e de apresentação é o **${input.base_preparacao.moeda_apresentacao || "BRL"}**.

A elaboração requer o uso de estimativas e julgamentos contábeis. As principais áreas incluem: ${estimativas}.
  `.trim();

  // --- Nota 3: Práticas Contábeis ---
  // Generating generic text based on standard practices, customized by inputs
  const nota3 = `
As principais práticas contábeis adotadas são:

**3.1. Apresentação das Demonstrações:** Elaboradas de acordo com o CPC 26, sob regime de competência.

**3.2. Caixa e Equivalentes:** Incluem dinheiro em caixa, depósitos bancários e aplicações de liquidez imediata.

**3.3. Estoques:** Mensurados ao custo ou valor realizável líquido, dos dois o menor. O método de custeio adotado é o **${input.praticas.metodo_custeio || "PEPS"}**.

**3.4. Ativo Imobilizado:** Demonstrado ao custo de aquisição, deduzido de depreciação acumulada calculada pelo método linear.

**3.5. Passivos:** Reconhecidos quando a entidade tem uma obrigação legal ou construtiva presente.

**3.6. Receitas:** Reconhecidas quando os riscos e benefícios são transferidos ou o serviço é prestado.
  `.trim();

  return {
    nota_1: nota1,
    nota_2: nota2,
    nota_3: nota3,
    validations: {
      consistent: warnings.length === 0,
      warnings
    }
  };
};
