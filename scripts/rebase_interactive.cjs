const { execSync } = require('child_process');
const readline = require('readline');

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

const question = (q) => new Promise(resolve => rl.question(q, resolve));

async function main() {
    console.log("--- AuditFlow Rebase Helper (Node.js/CJS) ---");
    console.log("Fetching latest changes from origin...");

    try {
        execSync('git fetch origin', { stdio: 'inherit' });
    } catch (e) {
        console.error("Failed to fetch. Check network.");
        process.exit(1);
    }

    let output;
    try {
        output = execSync('git branch -r').toString();
    } catch (e) {
        console.error("Failed to list branches.");
        process.exit(1);
    }

    const branches = output.split('\n')
        .map(b => b.trim())
        .filter(b => b.startsWith('origin/feature/') || b.startsWith('origin/fix-'));

    console.log(`\nFound ${branches.length} feature/fix branches.`);

    const auto = process.argv.includes('auto');
    if (auto) console.log("[AUTO MODE] Running non-interactively.");

    let successCount = 0;
    let failCount = 0;

    for (const branch of branches) {
        const local = branch.replace('origin/', '');

        let ans = 'y';
        if (!auto) {
            const answer = await question(`\nRebase branch '${local}'? [y(sim)/n(pular)/q(sair)] `);
            ans = answer.toLowerCase();
        } else {
            console.log(`\n[AUTO] Processing ${local}...`);
        }

        if (ans === 'q') break;
        if (ans !== 'y' && ans !== '') {
            console.log(`Skipping ${local}`);
            continue;
        }

        try {
            // Attempt to checkout. If local exists, this switches to it.
            // If we want to reset it to origin, we need -B.
            // CAUTION: -B resets local changes. Assuming this is desired for a clean rebase operation.
            console.log(`> git checkout -B ${local} ${branch}`);
            execSync(`git checkout -B ${local} ${branch}`, { stdio: 'inherit' });

            console.log(`> git rebase origin/main`);
            execSync(`git rebase origin/main`, { stdio: 'inherit' });

            console.log(`✅ Sucesso: ${local} atualizada.`);
            successCount++;
        } catch (e) {
            console.log(`❌ Erro/Conflito em ${local}. Abortando rebase deste branch.`);
            try { execSync('git rebase --abort'); } catch (err) { }
            failCount++;
        }
    }

    console.log(`\nProcesso finalizado. Sucesso: ${successCount}, Falhas: ${failCount}`);
    if (failCount > 0) console.log("Branches com falha provavelmente têm conflitos que exigem resolução manual.");

    rl.close();
}

main();
