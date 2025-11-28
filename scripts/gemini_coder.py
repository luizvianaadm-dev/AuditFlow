meu-projeto-auditoria/
├── .github/
│   └── workflows/        # Automação (CI/CD)
│       └── audit-check.yml # Roda testes automaticamente em novos dados
├── data/
│   ├── raw/              # Arquivos Excel/CSV originais (gitignored se sensível)
│   └── processed/        # Dados limpos
├── notebooks/            # Jupyter Notebooks para exploração de dados (Python)
│   └── 01_analise_benford.ipynb
├── src/                  # Código Fonte
│   ├── app/              # O código React que criei acima
│   ├── api/              # Backend Python (FastAPI ou Flask)
│   └── scripts/          # Scripts de limpeza de dados (ETL)
├── tests/                # Testes unitários para garantir que os cálculos estão certos
├── AGENTS.md             # Instruções para IA (como conversamos antes)
├── requirements.txt      # Dependências Python (pandas, numpy, scikit-learn)
└── README.md             # Documentação do projeto

#### 2. Tecnologias Chave para Auditoria
Se você quiser levar isso adiante, recomendo adicionar estas bibliotecas Python ao seu projeto:

* **Pandas:** Para carregar e manipular planilhas Excel gigantes.
* **Scikit-learn (Isolation Forest):** Um algoritmo de IA excelente para encontrar "anomalias" (lançamentos contábeis que fogem do padrão sem você precisar criar regras manuais).
* **Fuzzywuzzy:** Para encontrar duplicatas com nomes ligeiramente diferentes (ex: "Google Brasil" vs "Google BR Ltda").

#### 3. Automação com GitHub Actions
Você pode configurar o GitHub para que, toda vez que alguém suba um arquivo CSV novo na pasta `data/`, ele rode um script automaticamente:

* **Gatilho:** Upload de `base_2024.csv`.
* **Ação:** O GitHub Action roda o script Python.
* **Resultado:** O script gera o relatório de riscos e atualiza o Dashboard automaticamente.

Se quiser, posso gerar o **script Python** que faria a análise estatística (Lei de Benford) no backend para complementar esse frontend.
