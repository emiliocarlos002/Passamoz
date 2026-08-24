# Pagamentos reais do PassaMoz

O PassaMoz agora separa dois fluxos:

1. **Gateway/API** — M-Pesa, e-Mola e mKesh podem ser iniciados pelo checkout quando a operadora possui uma carteira de gateway configurada. A chave secreta fica somente nas variáveis de ambiente do servidor.
2. **Manual** — transferência bancária ou outro método sem API: o passageiro paga para os dados mostrados pela operadora e envia a referência; a operadora valida antes de liberar o bilhete.

## Arquitetura escolhida

O adaptador atual usa o NetShop como gateway. A documentação pública do NetShop descreve uma API REST, webhooks e suporte a M-Pesa, e-Mola, mKesh e cartões. A aplicação não guarda a chave secreta no banco.

## Configuração no Render

Defina as variáveis de ambiente:

- `NETSHOP_BASE_URL=https://www.netshop.co.mz/api`
- `NETSHOP_API_KEY=<chave de produção>`
- `PAYMENT_GATEWAY_TIMEOUT=20`
- `PAYMENT_WEBHOOK_TOKEN=<segredo interno opcional>`

Depois, cada operadora ativa o método no painel e informa apenas o **ID público da carteira** (`gateway_wallet_id`).

## Webhook

Endpoint do PassaMoz: `/api/v1/payments/webhook/`. O endpoint atualiza a transação e, quando o gateway informa sucesso, marca a reserva como paga.

**Importante:** antes de produção, o formato exato do webhook e os headers de assinatura fornecidos pela conta NetShop devem ser configurados no adaptador, sem colocar segredos no frontend.

## Fluxo final

Passageiro escolhe viagem → lugar é reservado → escolhe pagamento → gateway inicia cobrança → gateway confirma → PassaMoz marca pagamento/reserva como pagos → bilhete e QR Code ficam disponíveis.
