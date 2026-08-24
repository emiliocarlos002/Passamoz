# PassaMoz — publicar no Render

## Opção 1: Blueprint (mais fácil)
1. Envie este projeto para o GitHub.
2. No Render, crie um novo Blueprint.
3. Selecione o repositório.
4. O Render encontrará `render.yaml`.
5. Preencha `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS` quando solicitado.
6. Faça o deploy.

## Opção 2: Web Service manual
- Build Command: `./build.sh`
- Start Command: `./start.sh`
- Runtime: Python
- Defina `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.
- Conecte o PostgreSQL do Render para fornecer `DATABASE_URL`.

## Importante
O plano gratuito possui limitações de recursos e não equivale a 10.000 usuários simultâneos garantidos.
Esta configuração deixa o projeto mais simples de publicar e cria uma base melhor para escalar.
