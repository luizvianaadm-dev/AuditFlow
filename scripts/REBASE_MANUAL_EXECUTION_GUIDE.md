# Guia de Execução Manual - Rebase Seguro dos 64 Branches

**Status**: ✅ PRONTO PARA EXECUÇÃO - MODO SEGURO EM EDIÇÃO
**Data**: December 21, 2025
**Objetivo**: Resolver conflitos de rebase um por um com revisão completa

---

## 📋 Situação Atual

### O que aconteceu:
- 64 feature branches em DRAFT no GitHub/Vercel
- Script de rebase automático executado → 13 branches com conflitos
- 0 branches rebasados com sucesso (todos têm conflitos)
- 13 conflitos de merge detectados e documentados

### Branches com Conflitos (Ordem de Prioridade):

```
1. feature/fs-cash-flow-endpoint              [HIGH] - Cálculo DFC
2. feature/fs-export-utils                   [HIGH] - Exportar dados
3. feature/fs-generator-response-structure   [HIGH] - Estrutura resposta
4. feature/fs-wizard-and-notes              [MED]  - Wizard notas
5. feature/mapping-and-fs-improvements       [MED]  - Mapeamento FS
6. feature/mapping-and-fs-v2                 [MED]  - Mapeamento v2
7. feature/mapping-fs-validation             [MED]  - Validação mapping
8. feature/reconciliation-module             [HIGH] - Reconciliação
9. feature/standard-chart-hierarchy-and-custom-mapping [HIGH]
10. feature/standard-chart-hierarchy-and-custom-mapping-v2 [HIGH]
11. feature/dashboard-customization-engine   [MED]
12. feature/audit-trail-implementation       [MED]
13. feature/role-based-access-control        [LOW]
```

---

## 🚀 Como Executar (3 Opções)

### **Opção 1: Via Script Interativo (RECOMENDADO - MAIS SEGURO)**

```bash
# 1. Clone ou tenha o repo localmente
cd AuditFlow

# 2. Execute o script interativo
chmod +x scripts/rebase-manual-interactive.sh
./scripts/rebase-manual-interactive.sh

# 3. Para cada branch, escolha:
#    [r] = Rebase automático com -X ours (tenta resolver automaticamente)
#    [m] = Manual (você resolve conflitos no editor)
#    [s] = Pular (deixa para depois)
#    [q] = Sair
```

### **Opção 2: Manual via GitHub (SEM TERMINAL)**

Para cada branch com conflito:

1. **Acesse a PR**: https://github.com/luizvianaadm-dev/AuditFlow/pull/75
2. **Revise a aba "Files changed"**: Veja quais arquivos têm conflitos
3. **Resolva conflitos manualmente**: 
   - Clique em "Resolve conflicts" se disponível
   - Ou edite os arquivos manualmente
   - Busque por `<<<<<<<`, `=======`, `>>>>>>>`
4. **Mergear via GitHub**: Clique "Mark as resolved" → "Merge"

### **Opção 3: Via Command Line Local (COMPLETO CONTROLE)**

```bash
cd AuditFlow
git fetch origin

# Para cada branch:
BRANCH="feature/fs-cash-flow-endpoint"

# 1. Atualizar main
git checkout main && git pull origin main

# 2. Fazer rebase do branch
git fetch origin $BRANCH:$BRANCH --force
git checkout $BRANCH
git rebase main

# 3. Se houver conflitos:
#    a. Abra os arquivos (git status mostra conflitados)
#    b. Edite e resolva (remova <<<<<<, =======, >>>>>>)
#    c. Continue: git rebase --continue
#    d. Faça push: git push origin $BRANCH --force-with-lease

# 4. Se sucesso, cria PR no GitHub (ou já existe em DRAFT)
```

---

## ✅ Checklist de Execução

Antes de começar:
- [ ] Tenha SSH ou HTTPS configurado no Git
- [ ] Tenha acesso de escrita ao repositório
- [ ] Tenha branch `main` atualizado localmente
- [ ] Comprenda que isso vai fazer push das mudanças!

Durante a execução:
- [ ] Processe branches em ordem de prioridade
- [ ] Revise cada conflito completamente
- [ ] Teste localmente se possível
- [ ] Aguarde Vercel reconstruir após push

Após execução:
- [ ] Verifique status dos PRs no GitHub
- [ ] Confirme que Vercel passou em testes
- [ ] Mergear via GitHub quando "Ready to merge"
- [ ] Delete a branch após merge

---

## 🔧 Resolução de Conflitos - Exemplos

### Exemplo 1: Conflito em models.py

```python
# ANTES (com conflito):
<<<<<<< HEAD (main)
subscription = relationship("Subscription", back_populates="firm", uselist=False)
=======
subscription = relationship("Subscription", back_populates="firm")
>>>>>>> feature/fs-cash-flow-endpoint

# DEPOIS (resolvido - mantenha uma versão):
subscription = relationship("Subscription", back_populates="firm", uselist=False)
```

### Exemplo 2: Conflito em API routes

```python
# Mantenha as mudanças do feature branch
# Se duplicado, remova uma das versões
Ou use: git rebase --continue
Ou abort e tente: git rebase --abort && git checkout .
```

---

## 📊 Esperado (Resultados)

Após completar:
- ✅ 13 branches rebasados contra main
- ✅ Sem conflitos de merge impedindo PR
- ✅ Vercel reprocessará e validará
- ✅ Branches prontos para revisar e mergear

---

## ⚠️ Se Algo Der Errado

### "Rebase failed - conflitos não foram resolvidos"
```bash
# Aborte o rebase:
git rebase --abort

# Tente novamente:
git rebase main -X ours --no-edit
```

### "Push rejected - falha na autenticação"
```bash
# Verifique SSH:
ssh -T git@github.com

# Ou use HTTPS token
```

### "Branch diverged from main"
```bash
# Force update with lease (seguro):
git push origin feature/xyz --force-with-lease
```

---

## 📞 Suporte

Para problemas:
1. Revise os logs do rebase: `git rebase --status`
2. Veja conflitos: `git diff`
3. Edite arquivos manualmente
4. Use `--continue` para prosseguir
5. Se tudo falhar: `git rebase --abort` e tente [m] manual

---

**Próximo Passo**: Execute o script ou escolha a opção que funciona melhor para você!

```bash
# Rápido e seguro:
cd AuditFlow
./scripts/rebase-manual-interactive.sh
```
