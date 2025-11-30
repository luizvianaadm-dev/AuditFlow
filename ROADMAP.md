# Roadmap Estratégico - AuditFlow

Este documento descreve o plano de desenvolvimento para transformar o protótipo do AuditFlow em uma plataforma SaaS robusta de Auditoria Contábil.

## 🚀 Fase 1: Identidade e Segurança (Concluída)
**Objetivo:** Transformar o sistema em um SaaS Multi-tenant seguro.
- [x] **Backend (Auth):**
    - Criar modelo `User` vinculado à `AuditFirm`.
    - Implementar hash de senha (bcrypt).
    - Implementar autenticação via Token JWT (Access/Refresh).
    - Proteger rotas com dependência `get_current_user`.
- [x] **Frontend (Integração):**
    - Criar `AuthContext` no React para gerenciar estado de sessão.
    - Conectar formulário de Login à API (`POST /token`).
    - Conectar formulário de Cadastro à API (`POST /firms` + criação de user admin).

## 🏢 Fase 2: Gestão de Clientes e Trabalhos (Concluída)
**Objetivo:** Permitir que o auditor organize seus projetos (Engagements).
- [x] **Backend:**
    - Refinar CRUD de Clientes e Engagements.
    - Garantir isolamento de dados (usuário só vê dados da sua Firm).
- [x] **Frontend:**
    - Dashboard Principal: Listagem de Clientes.
    - Tela de Detalhes do Cliente: Histórico de Auditorias (Engagements).
    - Modal de criação de novos Clientes/Auditorias.

## 📥 Fase 3: Ingestão de Dados e Execução (Concluída)
**Objetivo:** Tornar o upload de dados flexível e executar testes.
- [x] **Frontend (Smart Upload):**
    - Interface de Upload no contexto da Auditoria.
- [x] **Backend:**
    - Processamento de CSV e execução de testes (Benford/Duplicatas).

## 🔍 Fase 4: Persistência e Histórico (Concluída)
**Objetivo:** Salvar os resultados das auditorias para consulta futura.
- [x] **Database:**
    - Criar tabelas `AnalysisResult` vinculadas ao `Engagement`.
- [x] **Backend:**
    - Endpoints para rodar testes e salvar resultados automaticamente.
- [x] **Frontend:**
    - Visualização do histórico de testes realizados.

## 📄 Fase 5: Relatórios Oficiais (Concluída)
**Objetivo:** Gerar o entregável final para o auditor.
- [x] **Gerador de Relatórios:**
    - Exportação em PDF com cabeçalho, resumo e detalhes.
    - Exportação em Word (DOCX) editável.
    - Exportação de dados brutos (Excel/CSV).

## 🧠 Fase 6: Expansão de Auditoria (Concluída)
**Objetivo:** Implementar lógica de auditoria profunda e modelos de serviço específicos.

### 6.1 Mapeamento Inteligente (De-Para)
- [x] **Interface de Mapping:** Interface para vincular colunas do CSV à taxonomia padrão.
- [x] **Taxonomia Padrão:** Planos de Contas Padrão implementados.

### 6.2 Planejamento e Materialidade (NBC TA 320)
- [x] **Calculadora de Materialidade:** Wizard para definir benchmarks e calcular Materialidade Global/Performance.
- [x] **Sumário de Ajustes:** Comparativo de erros não ajustados vs materialidade.

### 6.3 Testes Substantivos Avançados
- [x] **Circularização:** Gerador de cartas (Bancos/Advogados/Fornecedores).
- [x] **Teste de Folha:** Reconciliação folha contábil vs financeira.
- [x] **Amostragem Estatística (NBC TA 530):** Amostragem Aleatória e Estratificada.

### 6.4 Módulo de Aceitação (CRM)
- [x] **Questionário de Independência:** Checklist para aceitação de novos clientes (NBC TA 220).

---

## 🏗️ Fase 7: Infraestrutura e Otimização (Concluída)
**Objetivo:** Preparar a aplicação para ambiente de produção robusto.

- [x] **Containerização (Docker):** Criar Dockerfiles otimizados e Docker Compose para orquestração.
- [x] **Monitoramento:** Prometheus + Grafana e Logs JSON.
- [x] **Banco de Dados:** Migrar de SQLite para PostgreSQL (Suporte adicionado).
- [x] **Processamento Assíncrono:** Implementar Celery/Redis.
- [x] **CI/CD:** Pipelines de teste (Github Actions).

## 💰 Fase 8: Negócios e Monetização (Concluída)
**Objetivo:** Transformar o sistema em um produto comercializável.

- [x] **Billing Engine:** Gestão de Planos, Assinaturas e Histórico de Pagamentos.
- [x] **Landing Page:** Página pública de apresentação do produto.
- [x] **UI/UX Profissional:** Redesign do Dashboard e Navegação.
