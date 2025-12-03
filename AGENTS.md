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
# Diretrizes para Agentes de IA - AuditFlow

Este documento serve como a "Constituição" e Base de Conhecimento para todos os agentes de IA que contribuem para o AuditFlow.

## 🌟 Visão do Produto
**AuditFlow** é uma plataforma SaaS projetada para **democratizar a auditoria de alta qualidade** para firmas de pequeno e médio porte (PMEs). O objetivo é automatizar o cumprimento rigoroso das normas contábeis e de auditoria, oferecendo ferramentas de nível "Big 4" acessíveis via web.

## 🎯 Público-Alvo e Escopo
- **Público:** Firmas de Auditoria Independentes, Auditoria de Condomínios, Prestação de Contas (Eleitoral/Terceiro Setor).
- **Problema:** Sistemas das Big 4 são caros e inacessíveis; Excel é propenso a erros e sem rastreabilidade.
- **Solução:** Um ERP de Auditoria "End-to-End" que guia o auditor desde a aceitação até o relatório final.

## 📚 Base de Conhecimento Normativo (Core Knowledge)
O sistema deve ser construído com estrita aderência às seguintes normas (referência CFC e CPC):

### 1. Normas de Auditoria (NBC TAs) e Serviços Correlatos
- **NBC TA 200:** Objetivos gerais do auditor independente.
- **NBC TA 220:** Controle de qualidade (Aceitação e Continuidade).
- **NBC TA 230:** Documentação de Auditoria.
- **NBC TA 240:** Responsabilidade do auditor em relação a fraude (Módulo de Benford e Duplicatas).
- **NBC TA 300/315/320:** Planejamento e **Materialidade**.
- **NBC TA 500/520/530:** Evidência, Procedimentos Analíticos e Amostragem.
- **NBC TA 700:** Relatório do Auditor Independente.
- **NBC TA 800 (Considerações Especiais):** Auditorias de demonstrações contábeis elaboradas de acordo com estruturas para **propósitos especiais** (Essencial para Condomínios e Entidades Específicas).
- **NBC TSC 4400 (Trabalhos de Procedimentos Previamente Acordados - PPA):** Fundamental para auditorias que não visam uma "opinião" sobre as demonstrações como um todo, mas sim a verificação de itens específicos (ex: Prestação de Contas de Síndico, Verificação de Convênios).

### 2. Normas de Contabilidade (NBC TGs / IFRS / CPCs)
- O sistema deve interpretar a contabilidade conforme os **CPCs (Comitê de Pronunciamentos Contábeis)**.
- **ITG 2005 (Entidades Condominiais):** Norma específica que rege a contabilidade de condomínios edilícios (Fundo de Reserva, rateio de despesas, etc). A plataforma deve estar preparada para este padrão.
- **ITG 2002 (Entidade sem Finalidade de Lucros):** Para o Terceiro Setor.

## 🏗️ Arquitetura de Templates (Segmentação de Mercado)
A plataforma deve oferecer **"Templates de Auditoria"** distintos para atender PMEs de diferentes segmentos. O usuário seleciona o template no início do trabalho (Engagement):

1.  **Template BR GAAP (Empresarial Padrão):**
    - **Foco:** Balanço Patrimonial, DRE, DMPL.
    - **Normas:** NBC TAs Completo + CPCs PME.
    - **Testes:** Materialidade Global, Circularização, Estoques.

2.  **Template Condominial (Nicho Forte):**
    - **Foco:** Recebimentos vs Pagamentos (Fluxo de Caixa), Inadimplência, Fundo de Reserva, Obras.
    - **Normas:** NBC TA 800, NBC TSC 4400 (PPA), ITG 2005.
    - **Relatório:** Parecer do Auditor (se completo) ou Relatório de Constatações Factuais (se PPA).

3.  **Template Terceiro Setor:**
    - **Foco:** Projetos Específicos, Restrições de Recursos, Gratuidade.
    - **Normas:** ITG 2002.

## ⚙️ Módulos Funcionais
1.  **Módulo de Aceitação & Continuidade (CRM):** Questionários de independência (NBC TA 220).
2.  **Módulo de Planejamento (Materialidade):** Deve permitir metodologias flexíveis (ex: Planilhas proprietárias importadas) para cálculo de materialidade global e de performance.
3.  **Módulo de Execução:** Testes Substantivos (Ativo/Passivo) e Analíticos (Benford/Duplicatas).
4.  **Módulo de Mapeamento (De-Para Inteligente):** Interface para vincular o balancete do cliente (CSV) à taxonomia padrão do template escolhido.

## 💻 Padrões Técnicos
- **Backend:** Python (FastAPI), SQLAlchemy, Pydantic, Pandas/Numpy.
- **Async/Background:** Celery + Redis (para processamento pesado).
- **Monitoramento:** Prometheus + Grafana (Métricas), JSON Logs (Logging).
- **Frontend:** React (Vite), Tailwind CSS (Estilo "Vorcon"), Recharts.
- **Segurança:** Multi-tenancy rigoroso, JWT Auth.

---
*Este arquivo deve ser consultado antes de qualquer nova feature para garantir alinhamento com as normas e a visão estratégica.*
