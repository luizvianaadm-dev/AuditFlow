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
- **Flexibilidade de Modelos:** O sistema deve suportar diferentes taxonomias de contas e estruturas de relatório:
    - **Empresarial Geral (CPC 26):** Ativo, Passivo, PL, Resultado (DRE).
    - **Condomínios:** Foco em Recebimentos vs Pagamentos, Fundo de Reserva, Inadimplência.
    - **Terceiro Setor (ITG 2002):** Recursos com Restrição vs Sem Restrição, Superávit/Déficit.

## 🏗️ Arquitetura de Módulos (Service Models)
A plataforma deve evoluir para suportar "Modelos de Serviço" específicos. O código deve ser modular para permitir plug-ins de lógica de negócio conforme o tipo de cliente:

1.  **Módulo de Aceitação & Continuidade (CRM de Auditoria):**
    - Questionários de independência (NBC TA 220).
2.  **Módulo de Planejamento:**
    - Cálculo automático de **Materialidade** (Global e Performance).
3.  **Módulo de Execução (Testes Substantivos):**
    - **Ativo:** Circularização, Teste de Liquidez.
    - **Passivo:** Busca de passivos não registrados.
    - **PPA (NBC TSC 4400):** Checklists específicos acordados com o cliente (ex: "Verificar se todas as notas fiscais acima de R$ 1.000 têm 3 orçamentos").
4.  **Módulo de Mapeamento (De-Para Inteligente):**
    - Interface para vincular o balancete do cliente (CSV) à taxonomia padrão do AuditFlow.

## 💻 Padrões Técnicos
- **Backend:** Python (FastAPI), SQLAlchemy, Pydantic, Pandas/Numpy.
- **Frontend:** React (Vite), Tailwind CSS (Estilo "Vorcon"), Recharts.
- **Segurança:** Multi-tenancy rigoroso, JWT Auth.

---
*Este arquivo deve ser consultado antes de qualquer nova feature para garantir alinhamento com as normas e a visão estratégica.*
