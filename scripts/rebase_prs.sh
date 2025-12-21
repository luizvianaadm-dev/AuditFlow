#!/bin/bash

# ============================================================================
# rebase_prs.sh - Rebase Automático de PRs contra main atualizado
# Uso: ./scripts/rebase_prs.sh
# ============================================================================

set -e  # Exit on error

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=== Iniciando Rebase de PRs ===${NC}"

# 1. Atualizar main
echo -e "${YELLOW}[1/3] Atualizando branch main...${NC}"
git fetch origin main:main --force
git checkout main
git pull origin main

# 2. Listar branches de PRs do Jules (feature/* branches)
echo -e "${YELLOW}[2/3] Encontrando branches de PRs...${NC}"
BRANCHES=$(git for-each-ref --format='%(refname:short)' refs/remotes/origin | grep 'feature/' | sort)

if [ -z "$BRANCHES" ]; then
    echo -e "${RED}Nenhum branch 'feature/*' encontrado!${NC}"
    exit 1
fi

echo -e "${GREEN}Encontrados:${NC}"
echo "$BRANCHES" | nl

# 3. Fazer rebase de cada branch
echo -e "${YELLOW}[3/3] Iniciando rebase de cada branch...${NC}"

SUCCESS_COUNT=0
FAIL_COUNT=0

while IFS= read -r BRANCH; do
    if [ -z "$BRANCH" ]; then continue; fi
    
    BRANCH_NAME=$(echo "$BRANCH" | sed 's|origin/||')
    
    echo ""
    echo -e "${YELLOW}Rebasando: ${GREEN}$BRANCH_NAME${NC}"
    
    # Checkout branch
    if ! git checkout "$BRANCH" 2>/dev/null; then
        echo -e "${RED}✗ Erro ao fazer checkout de $BRANCH_NAME${NC}"
        FAIL_COUNT=$((FAIL_COUNT + 1))
        continue
    fi
    
    # Tenta rebase
    if git rebase main -X theirs --no-edit 2>/dev/null; then
        # Push com force
        if git push origin "$BRANCH_NAME" --force-with-lease 2>/dev/null; then
            echo -e "${GREEN}✓ Sucesso: $BRANCH_NAME${NC}"
            SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
        else
            echo -e "${RED}✗ Erro ao fazer push de $BRANCH_NAME${NC}"
            FAIL_COUNT=$((FAIL_COUNT + 1))
        fi
    else
        # Se houver conflitos, aborta o rebase
        echo -e "${RED}✗ Conflitos encontrados em $BRANCH_NAME - abortando${NC}"
        git rebase --abort 2>/dev/null || true
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi
done <<< "$BRANCHES"

# Retornar ao main
git checkout main

# Resumo
echo ""
echo -e "${YELLOW}=== Resumo ===${NC}"
echo -e "${GREEN}✓ Sucesso: $SUCCESS_COUNT${NC}"
echo -e "${RED}✗ Falhas: $FAIL_COUNT${NC}"

if [ $FAIL_COUNT -eq 0 ]; then
    echo -e "${GREEN}Todos os PRs foram rebasados com sucesso!${NC}"
    exit 0
else
    echo -e "${YELLOW}Alguns PRs falharam. Revise manualmente.${NC}"
    exit 1
fi
