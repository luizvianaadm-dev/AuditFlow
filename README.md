# AuditFlow

**Auditoria na Prática com Inteligência e Conformidade Normativa**

## Sobre o Projeto

O **AuditFlow** é uma plataforma Full Stack projetada para automatizar e guiar o processo de auditoria contábil e financeira. O sistema foi concebido para seguir rigorosamente as **Normas Brasileiras de Contabilidade (NBC TAs)** e as **Normas Internacionais de Auditoria (ISA)**, garantindo que cada etapa do trabalho do auditor esteja em conformidade com os requisitos regulatórios.

A proposta é oferecer um fluxo de trabalho (*workflow*) passo a passo, onde o auditor é conduzido desde o planejamento até a emissão do relatório, com ferramentas de automação para testes substantivos, controle de qualidade e documentação.

## Visão

Criar uma aplicação onde a tecnologia atua como um facilitador do cumprimento normativo, reduzindo riscos de auditoria e aumentando a eficiência dos trabalhos.

## Funcionalidades Planejadas

O sistema é estruturado em módulos que correspondem às fases da auditoria:

### 1. Pré-Compromisso e Planejamento (NBC TA 300)
*   **Aceitação de Cliente:** Checklist automatizado para avaliação de integridade e ética.
*   **Estratégia Global:** Definição do escopo, cronograma e equipe.
*   **Materialidade:** Cálculo automático e revisão de materialidade global e de performance.

### 2. Avaliação de Riscos (NBC TA 315)
*   **Matriz de Riscos:** Identificação e classificação de riscos de distorção relevante (inerente e de controle).
*   **Entendimento da Entidade:** Mapeamento do ambiente de negócios e estrutura de governança.
*   **Controles Internos:** Documentação e teste de controles chave.

### 3. Execução e Evidência (NBC TA 500)
*   **Automação de Testes Substantivos:**
    *   Análise via **Lei de Benford** para detecção de anomalias estatísticas.
    *   Detecção de *Outliers* e padrões suspeitos em lançamentos contábeis.
*   **Amostragem de Auditoria (NBC TA 530):** Ferramentas para seleção estatística e não estatística de itens.
*   **Papéis de Trabalho Eletrônicos:** Geração, indexação e armazenamento seguro de evidências.
*   **Confirmações Externas (NBC TA 505):** Gestão do processo de circularização.

### 4. Conclusão e Relatório (NBC TA 700)
*   **Revisão Final:** Checklist de conclusão e revisão de eventos subsequentes.
*   **Emissão de Relatório:** Geração automática da opinião do auditor baseada nas evidências coletadas e julgamentos documentados.

## Normas e Conformidade

O AuditFlow integra o conhecimento das normas diretamente no fluxo de trabalho.

*   **Conhecimento Integrado:** Não é necessário fazer o upload manual das normas. A lógica do sistema já incorpora os requisitos fundamentais das NBC TAs e ISAs.
*   **Atualização Contínua:** O sistema é projetado para evoluir conforme as revisões do Conselho Federal de Contabilidade (CFC) e Ibracon.

## Stack Tecnológica

O projeto utiliza uma arquitetura moderna para garantir performance, segurança e escalabilidade.

*   **Frontend:** React 18+, Tailwind CSS, Recharts (Visualização de Dados), Lucide-React (Ícones).
*   **Backend:** (A definir - focado em processamento de dados e regras de negócio).
*   **Banco de Dados:** (A definir - focado em integridade e segurança das evidências).

## Contribuindo

Consulte o arquivo `AGENTS.md` na raiz do projeto para diretrizes detalhadas sobre padrões de código, UI/UX e regras de desenvolvimento.

---
*AuditFlow - Transformando a auditoria com tecnologia e conformidade.*
