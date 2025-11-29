# Roadmap Estratégico - AuditFlow

Este documento descreve o plano de desenvolvimento para transformar o protótipo do AuditFlow em uma plataforma SaaS robusta de Auditoria Contábil.

## 🚀 Fase 1: Identidade e Segurança (Prioridade Alta)
**Objetivo:** Transformar o sistema em um SaaS Multi-tenant seguro.
- [ ] **Backend (Auth):**
    - Criar modelo `User` vinculado à `AuditFirm`.
    - Implementar hash de senha (bcrypt).
    - Implementar autenticação via Token JWT (Access/Refresh).
    - Proteger rotas com dependência `get_current_user`.
- [ ] **Frontend (Integração):**
    - Criar `AuthContext` no React para gerenciar estado de sessão.
    - Conectar formulário de Login à API (`POST /token`).
    - Conectar formulário de Cadastro à API (`POST /firms` + criação de user admin).

## 🏢 Fase 2: Gestão de Clientes e Trabalhos
**Objetivo:** Permitir que o auditor organize seus projetos (Engagements).
- [ ] **Backend:**
    - Refinar CRUD de Clientes e Engagements.
    - Garantir isolamento de dados (usuário só vê dados da sua Firm).
- [ ] **Frontend:**
    - Dashboard Principal: Listagem de Clientes.
    - Tela de Detalhes do Cliente: Histórico de Auditorias (Engagements).
    - Modal de criação de novos Clientes/Auditorias.

## 📥 Fase 3: Ingestão de Dados Avançada
**Objetivo:** Tornar o upload de dados flexível e à prova de falhas.
- [ ] **Frontend (Smart Upload):**
    - Interface de "De-Para" de colunas (Ex: Usuário indica qual coluna do CSV é "Data" e qual é "Valor").
    - Preview dos dados antes de salvar.
- [ ] **Backend:**
    - Validação robusta de datas e formatos numéricos (R$ vs US$).
    - Processamento assíncrono para arquivos grandes (Background Tasks).

## 🔍 Fase 4: Execução e Persistência de Testes
**Objetivo:** Salvar os resultados das auditorias para consulta futura.
- [ ] **Database:**
    - Criar tabelas `TestResult` e `TestAnomaly` vinculadas ao `Engagement`.
- [ ] **Backend:**
    - Adaptar scripts (Benford/Duplicatas) para salvar output no banco.
    - API para buscar histórico de resultados.
- [ ] **Frontend:**
    - Visualização persistente dos resultados (não apenas em tempo real).
    - Dashboard de "Matriz de Risco" do Engajamento.

## 📄 Fase 5: Relatórios Oficiais
**Objetivo:** Gerar o entregável final para o auditor.
- [ ] **Gerador de Relatórios:**
    - Exportação em PDF (formato de Relatório de Auditoria).
    - Exportação em Excel (Planilhas de trabalho com anomalias).
- [ ] **Customização:**
    - Permitir adicionar comentários e observações do auditor sobre cada anomalia.

---
**Próximo Passo Recomendado:** Iniciar a **Fase 1 (Identidade e Segurança)** para garantir que toda criação de dados já nasça vinculada a um usuário e empresa reais.
