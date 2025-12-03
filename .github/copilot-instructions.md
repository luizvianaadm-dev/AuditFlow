<!-- AuditFlow — Copilot agent guidance (pt-BR) -->
# Diretrizes rápidas para agentes de IA (AuditFlow)

Seja prático: pequenas mudanças funcionais e explicações claras ajudam auditores e desenvolvedores. Concentre-se no comportamento observável — onde os arquivos mostram regras (tests, serviços, scripts) siga essas regras.

## Visão geral rápida
- Backend: FastAPI em `src/api/main.py` — endpoints principais:
  - `POST /analyze/benford` -> usa `src/scripts/benford_analysis.py`
  - `POST /analyze/duplicates` -> usa `src/scripts/duplicate_analysis.py`
  - `POST /upload` e `/health` (simples)
- Frontend: componente React em `src/app/components/BenfordDashboard.jsx` e `src/app/services/auditService.js` (fetch para `http://localhost:8000`).
- Scripts analíticos (núcleo da lógica):
  - `src/scripts/benford_analysis.py` — cálculo da Lei de Benford; usa notação científica para extrair o primeiro dígito; anomalia considerada se desvio > 0.05.
  - `src/scripts/duplicate_analysis.py` — agrupa por `amount` e usa `thefuzz.token_sort_ratio` (>85) para marcar pares suspeitos.

## Regras de desenvolvimento e padrões do projeto
- UI: Tailwind CSS *obrigatório* (veja `scripts/AGENTS.md`). Não introduza Bootstrap/Material.
- Strings e formatação localizadas: formato de moeda deve usar `pt-BR` — ex.: `value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' })`.
- Componentização: se um componente visualizar 100+ linhas mova partes para subcomponentes.
- Mock data: quando não houver backend, adicione um gerador `generateTransactions(count)` no início do arquivo de componente.

## Regras técnicas e thresholds detectadas nos arquivos
- Benford: desvio absoluto > 0.05 => marque como anomalia (ver `benford_analysis.py`).
- Duplicatas: agrupar por `amount` exato; depois usar `thefuzz.token_sort_ratio` com limite **>85** para pares (ver `duplicate_analysis.py`).

## Dependências e comandos práticos
- Instale dependências Python (já listadas em `requirements.txt`).
  - Exemplo: `python -m pip install -r requirements.txt`
- Rodar API localmente:
  - `uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000`
  - O frontend espera `http://localhost:8000` para o serviço de análise.
- Rodar testes unitários (unittest está em `tests/`):
  - `python -m unittest discover -v`

## Como modificar sem quebrar ideias do projeto
- Ao alterar lógica analítica (Benford / Duplicates) preserve as entradas/saídas usadas pelos testes (`tests/`) e mantenha os formatos JSON esperados pelo frontend (`observe expected_frequencies`, `anomalies`, `details`).
- Se for alterar o limiar (ex: 0.05 ou 85), atualize os testes correspondentes em `tests/`.

## Pontos úteis para PRs e revisões
- Inclua pequenos testes unitários para qualquer mudança algorítmica; os testes existentes demonstram formato e cobertura desejáveis.
- Seja explícito sobre linguagem e região (pt-BR) quando retornar mensagens/erros (veja mensagens em `BenfordDashboard.jsx`).

---
Se algo não estiver claro ou quiser que eu adicione exemplos de PR templates / testes adicionais, diga qual parte quer que eu expanda. ✅
