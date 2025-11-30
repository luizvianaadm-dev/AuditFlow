# Guia de Deploy - AuditFlow

Este documento orienta como levar o AuditFlow do ambiente de desenvolvimento (Codespaces/Local) para produção.

## 🏠 Codespaces vs Produção

- **GitHub Codespaces:** É um ambiente de **desenvolvimento**. Use para editar código, rodar testes e visualizar o app enquanto programa. Ele "hiberna" quando você não está usando.
- **Produção (Vercel/Railway/AWS):** É onde seus clientes acessam o sistema. Fica online 24/7.

---

## 🚀 Opção Recomendada: Stack Separada

Para escalar e aproveitar o plano gratuito/barato de serviços modernos, recomendamos separar o Frontend do Backend.

### 1. Frontend (React) -> Vercel
A Vercel é a melhor plataforma para apps React/Vite.

1.  Crie uma conta na [Vercel](https://vercel.com).
2.  Clique em "Add New..." -> "Project".
3.  Importe seu repositório do GitHub (`auditflow`).
4.  **Configurações de Build:**
    - Framework Preset: `Vite` (deve detectar automaticamente).
    - Root Directory: `./` (raiz).
5.  **Variáveis de Ambiente:**
    - Adicione `VITE_API_URL` com o endereço do seu Backend (veja passo 2). Ex: `https://auditflow-api.railway.app`.
6.  Clique em **Deploy**.

### 2. Backend (FastAPI + Worker + DB) -> Railway
O Railway suporta Docker e serviços complexos (Redis/Postgres) muito bem.

1.  Crie uma conta no [Railway](https://railway.app).
2.  Crie um "New Project" -> "Deploy from GitHub repo".
3.  Selecione o repositório `auditflow`.
4.  O Railway vai tentar detectar o Dockerfile.
    - **Atenção:** Como temos dois Dockerfiles (`Dockerfile.backend` e `Dockerfile.frontend`), você precisa configurar qual usar.
    - No Railway, vá em Settings -> Build -> Dockerfile Path e defina `Dockerfile.backend`.
5.  **Adicionar Banco de Dados:**
    - No painel do Railway, clique "New" -> "Database" -> "PostgreSQL".
    - O Railway criará as variáveis `DATABASE_URL` automaticamente.
6.  **Adicionar Redis:**
    - No painel, clique "New" -> "Database" -> "Redis".
    - O Railway criará as variáveis `REDIS_URL` automaticamente.
7.  **Worker (Celery):**
    - Adicione um novo serviço baseado no *mesmo* repositório.
    - Configure o "Start Command" deste serviço para: `celery -A src.api.tasks.celery_app worker --loglevel=info`.
    - Certifique-se de que ele tem acesso às mesmas variáveis de ambiente (`DATABASE_URL`, `REDIS_URL`).

---

## 🐳 Opção Alternativa: Docker Compose (VPS)

Se preferir usar uma máquina virtual (AWS EC2, DigitalOcean Droplet, Linode):

1.  Clone o repositório na máquina.
2.  Crie um arquivo `.env` com as senhas.
3.  Execute:
    ```bash
    docker-compose up -d --build
    ```
4.  O Frontend estará na porta 3000 e Backend na 8000.
5.  Use Nginx na VPS para fazer o proxy reverso e configurar SSL (Certbot).

## ⚠️ Configurações Importantes

- **CORS:** No arquivo `src/api/main.py`, a configuração de CORS está permitindo tudo (`["*"]`). Em produção, altere para o domínio do seu frontend na Vercel (ex: `https://auditflow.vercel.app`).
- **Secret Key:** Defina a variável de ambiente `SECRET_KEY` no Backend com uma string aleatória segura para assinar os tokens JWT.
