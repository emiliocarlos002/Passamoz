# PassaMoz v2

**Sua viagem. Seu bilhete. Seu destino.**

Plataforma Django para venda de bilhetes de transporte de passageiros em Moçambique.

## O que esta versão traz

- Identidade visual PassaMoz.
- Interface responsiva para celular e computador.
- Passageiros com cadastro, login e recuperação de conta.
- Operadoras com candidatura e aprovação administrativa.
- Rotas, veículos, lugares e viagens.
- Pesquisa por origem, destino e data.
- Contas de M-Pesa, e-Mola e mKesh por operadora.
- Pagamento direcionado à conta informada pela operadora.
- Registro de referência da confirmação de pagamento.
- QR Code e PDF do bilhete.
- Painel administrativo para operadoras.
- Estrutura de cobrança mensal das operadoras, sem comissão por bilhete.
- API inicial em `/api/v1/` preparada para futuro aplicativo Android/iOS.

## Administrador

Não existe cadastro público de administrador.

    python manage.py createsuperuser

## Instalação

    python -m venv .venv
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py runserver

Acesse `http://127.0.0.1:8000/`.

## API para o futuro app

    GET /api/v1/health/
    GET /api/v1/trips/

Esta é uma API inicial. Para o aplicativo completo, recomenda-se adicionar autenticação por tokens,
endpoints de reservas, pagamentos, bilhetes, notificações e validação QR.

## Pagamentos

A aplicação mantém a estrutura para M-Pesa, e-Mola e mKesh, mas não inventa integrações financeiras.
Para transações reais serão necessárias as APIs oficiais, credenciais sandbox/produção, webhooks,
idempotência, assinatura/validação de callbacks e regras específicas de cada provedor.

## Mensalidade

A plataforma não cobra comissão sobre cada bilhete. O administrador pode controlar mensalidades
por operadora em `/plataforma/mensalidades/`.

## Produção

Configure SECRET_KEY segura, DEBUG=False, ALLOWED_HOSTS, HTTPS, PostgreSQL, e-mail real,
armazenamento de media, backups, logs e as integrações oficiais de pagamento.


AVISO: makemigrations não foi executado automaticamente neste ambiente. Execute `python manage.py makemigrations` antes de `migrate` se necessário.


## Fluxo principal corrigido

1. Crie uma conta em `/conta/cadastrar/`.
2. Entre em `/conta/entrar/`.
3. Use **Viagens** para pesquisar viagens publicadas.
4. Abra uma viagem e escolha um lugar.
5. Faça a reserva e envie a referência do pagamento.
6. A operadora confirma o pagamento no painel.
7. O passageiro recebe o bilhete com QR Code e PDF.
8. A operadora pode validar o QR Code em `/validar-bilhete/`.

As URLs antigas de `/compras/` continuam a funcionar como redirecionamentos para o fluxo novo.

## Teste rápido local

Depois de instalar as dependências e executar as migrações, use `python manage.py seed_demo` para criar uma operadora, uma rota Maputo → Xai-Xai, 20 lugares, contas de pagamento e uma viagem publicada de demonstração. Depois abra `/` e clique em **Pesquisar viagem**.


## PassaMoz V3 — melhorias de produção

Esta versão adiciona: ciclo de vida de reservas (pendente, processamento, pago, expirado, cancelado e reembolsado), bloqueio concorrente de lugares, expiração de 15 minutos, pagamentos idempotentes, eventos de webhook, emissão automática do bilhete após confirmação e base para checkout de vários lugares/passageiros.

### Expiração de reservas
O comando `python manage.py expire_bookings` deve ser executado periodicamente em produção (por exemplo, a cada 1 minuto) para libertar reservas expiradas. O fluxo do passageiro também verifica a expiração ao abrir/enviar o pagamento.

### Pagamentos
Configure `PAYMENT_WEBHOOK_TOKEN` no ambiente. Quando o gateway suportar assinatura HMAC, envie `X-Passamoz-Webhook-Signature` com HMAC-SHA256 do corpo usando o mesmo segredo.

### Segurança
Em produção mantenha `DEBUG=False`, use `SECRET_KEY` gerada no ambiente, PostgreSQL, HTTPS e configure `ALLOWED_HOSTS` e `CSRF_TRUSTED_ORIGINS`.

## Ativação segura da conta da operadora

Após a aprovação pelo administrador, a operadora não entra diretamente no painel. O PassaMoz gera um link de ativação de uso único, válido pelo número de horas definido em `PASSAMOZ_ACTIVATION_TIMEOUT_HOURS` (24 por padrão). O link abre uma página para definir uma nova senha; depois da confirmação, a conta fica ativada e o utilizador é conectado automaticamente ao painel da operadora. O administrador pode reenviar o link de ativação a qualquer momento enquanto a conta estiver ativa mas ainda não ativada.

Fluxo: `Candidatura → Aprovação → E-mail de ativação → Definir senha → Conta ativada → Painel da operadora`.

## Cadastro profissional de operadora
A candidatura de operadora agora possui interface mobile-first em etapas visuais, com dados da empresa, localização, responsável, contactos e dados de transporte. Os novos campos são persistidos na entidade `Transporter` e a migração `0006_operator_application_details` deve ser aplicada com `python manage.py migrate`.
