# PR Rebase Guide - AuditFlow

## Problema
Os 64 PRs criados pelo Jules (feature branches) ficaram com conflitos após as atualizações recentes na branch `main` (FirmSettings.jsx fix, etc.).

## Solução: Rebase Automático

Usamos um script bash que:
1. Atualiza a branch `main`
2. Lista todos os branches `feature/*`
3. Faz rebase contra `main` com estratégia `-X theirs`
4. Resolve conflitos automaticamente (mantendo mudanças do PR)
5. Faz force push com `-force-with-lease` (seguro)
6. Retorna resumo com estatísticas

## Como Usar

### Pré-requisitos
- Git instalado e configurado
- SSH/Token GitHub configurado
- Estar na raiz do repositório

### Execução

```bash
# 1. Clonar repositório (se não tiver)
git clone git@github.com:luizvianaadm-dev/AuditFlow.git
cd AuditFlow

# 2. Dar permissão de execução ao script
chmod +x scripts/rebase_prs.sh

# 3. Executar o script
./scripts/rebase_prs.sh
```

## O que Acontece

**Fase 1: Atualização**
```
[1/3] Atualizando branch main...
```
O script faz checkout de `main` e puxa as últimas mudanças.

**Fase 2: Descoberta**
```
[2/3] Encontrando branches de PRs...
Encontrados:
 1 feature/reconciliation-module
 2 feature/financial-statements-wizard
...
 64 feature/some-feature
```
Todos os branches `feature/*` são listados.

**Fase 3: Rebase**
```
[3/3] Iniciando rebase de cada branch...

Rebasando: feature/reconciliation-module
✓ Sucesso: feature/reconciliation-module
Rebasando: feature/financial-statements-wizard
✓ Sucesso: feature/financial-statements-wizard
...
```
Cada branch é rebasado e pushed automaticamente.

**Resumo Final**
```
=== Resumo ===
✓ Sucesso: 60
✗ Falhas: 4
Alguns PRs falharam. Revise manualmente.
```

## Entendendo o Rebase

### Por que `-X theirs`?
- `theirs` = accept incoming (branch do PR) em caso de conflito
- Mantém as mudanças do PR intactas
- Resolve conflitos automaticamente
- É seguro porque estamos rebasando PRs, não main

### Por que `--force-with-lease`?
- Mais seguro que `--force`
- Verifica se alguém mais fez push enquanto re basavámos
- Protege contra sobrescrita acidental

## Após o Rebase

### 1. Verificar PRs
- Acesse GitHub > Pull Requests
- Os PRs agora devem estar **sem merge conflicts**
- O bot do Vercel vai fazer rebuild
- Aguarde status "Ready to merge"

### 2. Revisar Mudanças
- Abra cada PR
- Leia a descrição
- Clique em "Files changed" para ver diff
- Aprove se tudo estiver correto

### 3. Mergear
- Clique "Merge pull request"
- Escolha "Squash and merge" (recomendado)
- Depois delete a branch

## Se Algo Der Errado

### "Conflitos encontrados em feature/xyz"
Alguns PRs podem ter conflitos que o script não conseguiu resolver.

**Solução:**
```bash
# Abrir o PR manualmente
git fetch origin feature/xyz:feature/xyz
git checkout feature/xyz
git rebase main -X theirs
# Resolver conflitos manualmente se necessário
git rebase --continue
git push origin feature/xyz --force-with-lease
```

### "Erro ao fazer push"
GitHub pode estar rejeitando o push.

**Soluções:**
- Verifique SSH/Token: `git config --list | grep github`
- Tente com HTTPS em vez de SSH
- Verifique permissões no GitHub

## Status Atual

- **PRs Totais**: 64
- **Data do último Rebase**: [DATA]
- **PRs Sucesso**: [X]
- **PRs Falhados**: [Y]
- **PRs Mergeados**: [Z]

## Referências

- [Git Rebase Docs](https://git-scm.com/docs/git-rebase)
- [Conflict Resolution](https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging)
- [GitHub PR Workflow](https://docs.github.com/en/pull-requests)

---

**Criado por**: Comet (AI Assistant)
**Data**: Dec 21, 2025
**Status**: Ativo♪
