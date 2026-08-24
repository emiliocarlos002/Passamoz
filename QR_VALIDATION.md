# Validação de QR Code PassaMoz

URL: `/validar-bilhete/`

Apenas utilizadores associados a uma operadora ativa conseguem validar bilhetes.

Fluxo:
1. Funcionário abre a página no telemóvel.
2. Autoriza acesso à câmera.
3. Escaneia o QR Code do bilhete.
4. O servidor verifica o código.
5. Confirma que o bilhete pertence à própria operadora.
6. Confirma que a reserva está paga.
7. Confirma que a viagem não está cancelada/finalizada.
8. Mostra passageiro, rota, horário e lugar.

O QR Code contém apenas o UUID do bilhete; os dados completos são consultados no servidor.
