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

---

## 🔮 Fase 6: Expansão Pós-MVP (Próximos Passos)
**Objetivo:** Implementar lógica de auditoria profunda e modelos de serviço específicos.

### 6.1 Mapeamento Inteligente (De-Para)
- [ ] **Interface de Mapping:** Permitir que o usuário diga que a coluna "Vl. Liq." do CSV corresponde ao campo "Valor" do sistema.
- [ ] **Taxonomia Padrão:** Criar Planos de Contas Padrão (Modelo Geral, Modelo Condomínio).

### 6.2 Planejamento e Materialidade (NBC TA 320)
- [ ] **Calculadora de Materialidade:** Wizard para definir benchmarks (Receita, Ativo Total) e percentuais para calcular a Materialidade Global e de Performance.
- [ ] **Matriz de Risco:** Vincular contas contábeis a riscos específicos (Alto/Médio/Baixo).

### 6.3 Testes Substantivos Avançados
- [ ] **Circularização:** Módulo para gerar cartas de circularização (Fornecedores/Bancos/Advogados) em PDF/Word.
- [ ] **Teste de Folha:** Re cálculo global da folha vs GPS/SEFIP.
- [ ] **Amostragem Estatística (NBC TA 530):** Ferramenta para selecionar amostras aleatórias ou estratificadas para testes de detalhes.

### 6.4 Módulo de Aceitação (CRM)
- [ ] **Questionário de Independência:** Checklist para aceitação de novos clientes (NBC TA 220).
