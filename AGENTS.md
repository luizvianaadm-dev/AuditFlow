AGENTS.md - Diretrizes do Projeto AuditFlow

Este arquivo contém o contexto e regras para agentes de IA (Google Jules, Copilot, etc.) trabalhando neste repositório de Auditoria Contábil.

1. Contexto do Projeto

Nome: AuditFlow Platform

Objetivo: Plataforma Full Stack de automação de auditoria passo a passo, em conformidade com as Normas NBC TAs e Normas de Contabilidade, incluindo visualização de dados para detecção de fraudes.

Público: Auditores e Contadores (interface deve ser séria, limpa e profissional).

2. Stack Tecnológica (Frontend)

Framework: React 18+ (Create React App ou Vite).

Linguagem: JavaScript (ES6+) ou JSX.

Estilização: Tailwind CSS (obrigatório). Não utilize arquivos .css separados ou styled-components.

Gráficos: Recharts (para gráficos de linha, pizza e barras).

Ícones: Lucide-React.

3. Stack Tecnológica (Backend)

Framework: FastAPI.

Linguagem: Python 3.10+.

Tipagem: Obrigatório o uso de Type Hints (tipagem estrita) em todas as funções e modelos.

Dependências de Dados: Pandas, Numpy.

4. Padrões de UI/UX (Design System)

Paleta de Cores:

Fundo: bg-slate-50

Sidebar/Header: bg-slate-900

Acentos: text-blue-600 para ações principais.

Risco Alto: text-red-600 / bg-red-50 (Alertas).

Risco Baixo/Normal: text-green-600 / bg-green-50.

Componentes:

Use rounded-xl para cartões.

Sombras suaves (shadow-sm) em elementos brancos.

5. Regras de Dados (Mock vs Real)

Ao criar novas visualizações, se não houver backend conectado, crie uma função geradora de dados falsos (mock) no início do arquivo (ex: generateTransactions(count)).

Formatação de Moeda: Sempre use pt-BR (R$).

Ex: value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })

6. Diretrizes de Código

Componentização: Se um componente visual (como um Card ou Gráfico) tiver mais de 100 linhas, separe-o em um componente funcional menor dentro do mesmo arquivo ou pasta.

Hooks: Use useState e useEffect para gerenciamento de dados.

Imports:

Mantenha imports de bibliotecas (React, Recharts) no topo.

Imports de ícones (Lucide) logo abaixo.

7. O que NÃO fazer

❌ Não use Bootstrap ou Material UI. Use apenas classes utilitárias do Tailwind.

❌ Não use class, use sempre className.

❌ Não hardcode textos de erro genéricos. Use termos de auditoria (ex: "Divergência de Valor", "Fornecedor Não Homologado").
