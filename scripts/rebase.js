#!/usr/bin/env node
const { exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const COLORS = {
  YELLOW: '\x1b[1;33m',
  GREEN: '\x1b[0;32m',
  RED: '\x1b[0;31m',
  CYAN: '\x1b[0;36m',
  NC: '\x1b[0m',
};

function log(color, message) {
  console.log(`${color}${message}${COLORS.NC}`);
}

async function runCommand(cmd, silent = false) {
  try {
    const { stdout, stderr } = await execPromise(cmd);
    if (!silent) console.log(stdout);
    return { success: true, stdout, stderr };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

async function rebaseAllFeatures() {
  log(COLORS.YELLOW, '=== PR Rebase Script (Node.js Version) ===')
  log(COLORS.YELLOW, 'Processando 64 feature branches...')
  try {
    // Step 1: Atualizar main
    log(COLORS.YELLOW, '\n[1/3] Atualizando branch main...')
    await runCommand('git fetch origin main:main --force')
    await runCommand('git checkout main')
    await runCommand('git pull origin main')
    log(COLORS.GREEN, '✓ Main atualizado')

    // Step 2: Listar branches
    log(COLORS.YELLOW, '\n[2/3] Encontrando feature branches...')
    const { stdout } = await execPromise(
      'git for-each-ref --format="%(refname:short)" refs/remotes/origin | grep feature'
    )
    const branches = stdout
      .split('\n')
      .map(b => b.trim())
      .filter(b => b && b.includes('feature/'))
      .map(b => b.replace('origin/', ''))
    
    if (branches.length === 0) {
      log(COLORS.RED, 'Nenhum branch feature/* encontrado!')
      process.exit(1)
    }
    
    log(COLORS.GREEN, `Encontrados ${branches.length} branches:`)
    branches.forEach((b, i) => console.log(`${i + 1}. ${b}`))

    // Step 3: Fazer rebase
    log(COLORS.YELLOW, '\n[3/3] Iniciando rebase...\n')
    let successCount = 0
    let failCount = 0

    for (const branch of branches) {
      try {
        log(COLORS.CYAN, `Rebasando: ${branch}`)
        
        // Checkout branch
        await runCommand(`git checkout origin/${branch}`, true)
        
        // Rebase com -X theirs (resolve conflitos automaticamente)
        const rebaseResult = await runCommand(
          `git rebase main -X theirs --no-edit`,
          true
        )
        
        if (rebaseResult.success) {
          // Push com force-with-lease (seguro)
          await runCommand(
            `git push origin ${branch} --force-with-lease`,
            true
          )
          log(COLORS.GREEN, `✓ Sucesso: ${branch}`)
          successCount++
        } else {
          // Abortar rebase se falhar
          await runCommand('git rebase --abort', true)
          log(COLORS.RED, `✗ Conflitos em: ${branch}`)
          failCount++
        }
      } catch (err) {
        log(COLORS.RED, `✗ Erro ao processar ${branch}: ${err.message}`)
        failCount++
      }
    }

    // Retornar ao main
    await runCommand('git checkout main')

    // Resumo
    log(COLORS.YELLOW, '\n=== RESUMO ===')
    log(COLORS.GREEN, `✓ Sucesso: ${successCount}`)
    log(COLORS.RED, `✗ Falhas: ${failCount}`)

    if (failCount === 0) {
      log(COLORS.GREEN, '\n✓ Todos os PRs foram rebasados com sucesso!')
      process.exit(0)
    } else {
      log(COLORS.YELLOW, '\n⚠ Alguns PRs falharam. Revise manualmente.')
      process.exit(1)
    }
  } catch (error) {
    log(COLORS.RED, `\nErro fatal: ${error.message}`)
    process.exit(1)
  }
}

rebaseAllFeatures()
