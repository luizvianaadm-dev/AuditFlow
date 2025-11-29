# Diretrizes para Agentes de IA - AuditFlow

Este documento serve como a "Constituição" e Base de Conhecimento para todos os agentes de IA que contribuem para o AuditFlow.

## 🌟 Visão do Produto
**AuditFlow** é uma plataforma SaaS projetada para **democratizar a auditoria de alta qualidade** para firmas de pequeno e médio porte (PMEs). O objetivo é automatizar o cumprimento rigoroso das normas contábeis e de auditoria, oferecendo ferramentas de nível "Big 4" acessíveis via web.

## 🎯 Público-Alvo e Escopo
- **Público:** Firmas de Auditoria Independentes, Auditoria de Condomínios, Prestação de Contas (Eleitoral/Terceiro Setor).
- **Problema:** Sistemas das Big 4 são caros e inacessíveis; Excel é propenso a erros e sem rastreabilidade.
- **Solução:** Um ERP de Auditoria "End-to-End" que guia o auditor desde a aceitação até o relatório final.

## 📚 Base de Conhecimento Normativo (Core Knowledge)
O sistema deve ser construído com estrita aderência às seguintes normas:

### 1. Normas de Auditoria (NBC TAs)
- **NBC TA 200:** Objetivos gerais do auditor independente.
- **NBC TA 220:** Controle de qualidade da auditoria (Aceitação e Continuidade de Clientes).
- **NBC TA 230:** Documentação de Auditoria (O sistema deve gerar papéis de trabalho automáticos).
- **NBC TA 240:** Responsabilidade do auditor em relação a fraude (Módulo de Benford e Duplicatas já implementado).
- **NBC TA 300/315/320:** Planejamento, Identificação de Riscos e **Materialidade**.
- **NBC TA 500/520/530:** Evidência de Auditoria, Procedimentos Analíticos e Amostragem.
- **NBC TA 700:** Formação da opinião e emissão do relatório.

### 2. Normas de Contabilidade (NBC TGs / IFRS)
- O sistema deve ser capaz de interpretar Balancetes e Razões Contábeis baseados nas IFRS (International Financial Reporting Standards) e CPCs.
- **Flexibilidade de Modelos:** O sistema deve suportar diferentes taxonomias de contas:
    - **Empresarial Geral:** Ativo, Passivo, PL, Resultado.
    - **Condomínios:** Fundo de Reserva, Taxas Ordinárias/Extras.
    - **Terceiro Setor:** Recursos com Restrição, Sem Restrição.

## 🏗️ Arquitetura de Módulos (Service Models)
A plataforma deve evoluir para suportar "Modelos de Serviço" específicos. O código deve ser modular para permitir plug-ins de lógica de negócio conforme o tipo de cliente:

1.  **Módulo de Aceitação & Continuidade (CRM de Auditoria):**
    - Questionários de independência.
    - Análise de risco do cliente.
2.  **Módulo de Planejamento:**
    - Cálculo automático de **Materialidade** (Global e Performance).
    - Definição da estratégia de auditoria.
3.  **Módulo de Execução (Testes Substantivos):**
    - **Ativo:** Circularização (Confirmação Externa), Teste de Liquidez.
    - **Passivo:** Busca de passivos não registrados (Search for unrecorded liabilities).
    - **Resultado:** Análise de oscilação mensal, Teste de Folha de Pagamento.
4.  **Módulo de Mapeamento (De-Para Inteligente):**
    - Interface para o auditor vincular as contas do balancete do cliente (CSV/Excel) às contas padrão do AuditFlow para padronizar os testes.

## 💻 Padrões Técnicos
- **Backend:** Python (FastAPI), SQLAlchemy, Pydantic, Pandas/Numpy (para processamento pesado).
- **Frontend:** React (Vite), Tailwind CSS (Estilo "Vorcon" - Azul Corporativo), Recharts.
- **Segurança:** Multi-tenancy rigoroso (Isolamento por `AuditFirm`), JWT Auth, Logs de Auditoria (Quem fez o quê e quando).

---
*Este arquivo deve ser consultado antes de qualquer nova feature para garantir alinhamento com as normas e a visão estratégica.*
