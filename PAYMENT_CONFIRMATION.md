# Confirmação de pagamentos PassaMoz

Fluxo real do MVP:

1. Passageiro cria a reserva.
2. Passageiro paga diretamente para a conta da própria operadora.
3. Passageiro envia a referência da transação.
4. A reserva aparece em **Reservas e pagamentos** no painel da operadora.
5. A operadora confere a transação no seu M-Pesa/e-Mola/mKesh.
6. Ao confirmar:
   - pagamento passa para `confirmed`;
   - reserva passa para `paid`;
   - `paid_at` é preenchido;
   - bilhete é criado;
   - QR Code/PDF do bilhete é gerado.
7. Ao rejeitar:
   - pagamento passa para `rejected`;
   - reserva é cancelada;
   - lugar volta a ficar disponível.

A confirmação é manual e segura: o sistema não declara que uma transferência aconteceu sem a operadora conferir a referência.
