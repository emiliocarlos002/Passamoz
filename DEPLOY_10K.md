# PassaMoz — preparação para 10.000+ usuários

Esta versão melhora a base de produção, mas 10.000 usuários **não é uma garantia automática**.
É necessário testar a carga no ambiente real.

## Antes do deploy
1. Criar PostgreSQL no Render.
2. Configurar `DATABASE_URL` ou as variáveis `POSTGRES_*` conforme o serviço.
3. Definir `SECRET_KEY` forte.
4. Definir `DEBUG=False`.
5. Definir `ALLOWED_HOSTS` com o domínio real.
6. Configurar `REDIS_URL` quando Redis estiver disponível.
7. Rodar migrations.
8. Rodar `collectstatic`.

## Testes recomendados
- Pesquisa de viagens sob carga.
- Reserva simultânea do mesmo assento.
- Pagamentos simultâneos.
- Login simultâneo.
- Picos de tráfego.
- Erros de banco/conexão.
- Recuperação após reinício do servidor.

## Escalonamento
Comece com 2–3 workers e ajuste conforme CPU/RAM e resultados dos testes. Não aumente workers
indefinidamente: cada worker consome memória.

## Segurança
Nunca coloque senhas, tokens, chaves de API ou credenciais no GitHub.
