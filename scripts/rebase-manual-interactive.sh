#!/bin/bash

# Script para Rebase Manual e Interativo de Branches com Conflitos
# Uso: ./rebase-manual-interactive.sh
# Este script processa 1 branch por vez, permitindo revisão manual de conflitos

set -e

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║     REBASE MANUAL - MODO INTERATIVO COM REVISÃO SEGURA         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Atualizar main
echo "📍 Atualizando branch main..."
git fetch origin main:main --force
git checkout main
git pull origin main
echo "✅ Branch main atualizado"
echo ""

# Array de branches com conflitos conhecidos
BRANCHES_COM_CONFLITOS=(
  "feature/fs-cash-flow-endpoint"
  "feature/fs-export-utils"
  "feature/fs-generator-response-structure"
  "feature/fs-wizard-and-notes"
  "feature/mapping-and-fs-improvements"
  "feature/mapping-and-fs-v2"
  "feature/mapping-fs-validation"
  "feature/reconciliation-module"
  "feature/standard-chart-hierarchy-and-custom-mapping"
  "feature/standard-chart-hierarchy-and-custom-mapping-v2"
  "feature/dashboard-customization-engine"
  "feature/audit-trail-implementation"
  "feature/role-based-access-control"
)

SUCCESS_COUNT=0
FAIL_COUNT=0
SKIP_COUNT=0

# Processar cada branch
for branch in "${BRANCHES_COM_CONFLITOS[@]}"; do
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🔄 Processando: $branch"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo ""
  
  # Opções de ação
  echo "Opções:"
  echo "  [r] Rebase com resolução automática (ours)"
  echo "  [m] Rebase manual (requer resolução)"
  echo "  [s] Pular branch"
  echo "  [q] Sair"
  echo ""
  
  read -p "Escolha uma opção [r/m/s/q]: " choice
  
  case $choice in
    r)
      echo "Tentando rebase automático com estratégia 'ours'..."
      if git fetch origin "$branch:$branch" --force 2>/dev/null; then
        git checkout "$branch" 2>/dev/null || true
        if git rebase main -X ours --no-edit 2>/dev/null; then
          if git push origin "$branch" --force-with-lease 2>/dev/null; then
            echo "✅ $branch - Rebase e push bem-sucedidos"
            ((SUCCESS_COUNT++))
          else
            echo "❌ $branch - Falha no push"
            ((FAIL_COUNT++))
          fi
        else
          echo "⚠️ $branch - Conflitos detectados (rebase abortado)"
          git rebase --abort 2>/dev/null || true
          ((FAIL_COUNT++))
        fi
      else
        echo "❌ $branch - Não existe ou não acessível"
        ((FAIL_COUNT++))
      fi
      ;;
    m)
      echo "Abrindo editor para resolução manual..."
      git fetch origin "$branch:$branch" --force
      git checkout "$branch"
      git rebase main || {
        echo "ℹ️ Conflitos encontrados. Resolva manualmente:"
        echo "   1. Edite os arquivos com conflito (busque <<<<<<, ======, >>>>>>)"
        echo "   2. Execute: git rebase --continue"
        echo "   3. Execute: git push origin $branch --force-with-lease"
        read -p "Pressione Enter quando terminar..."
      }
      ((SUCCESS_COUNT++))
      ;;
    s)
      echo "⏭️ Pulando $branch"
      ((SKIP_COUNT++))
      ;;
    q)
      echo ""
      echo "Saindo..."
      break
      ;;
    *)
      echo "❌ Opção inválida"
      continue
      ;;
  esac
  
  echo ""
done

# Resumo Final
echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    RESUMO FINAL DO PROCESSAMENTO                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo "✅ Sucesso:     $SUCCESS_COUNT"
echo "❌ Falhas:      $FAIL_COUNT"
echo "⏭️ Pulados:     $SKIP_COUNT"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Próximos passos:"
echo "1. Verifique branches falhados manualmente"
echo "2. Resolva conflitos no PR do GitHub"
echo "3. Aguarde Vercel reconstruir cada branch"
echo "4. Mergear via GitHub quando 'Ready to merge'"
echo ""
echo "✨ Processo concluído!"
