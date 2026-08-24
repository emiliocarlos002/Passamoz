# PassaMoz — atualização visual

A homepage foi reorganizada no estilo dashboard mostrado no mockup: menu lateral, barra superior, pesquisa de viagens em destaque, destinos, operadoras, promoções, suporte e estatísticas.

## Regra das operadoras
Os locais/terminais, rotas, horários, veículos e lugares continuam a ser dados controlados pelas operadoras. A PassaMoz apenas apresenta ao passageiro as opções publicadas.

## Rodar no VS Code
1. Abra a pasta `passamoz_final` no VS Code.
2. Crie/ative o ambiente virtual conforme o seu Windows.
3. `python -m pip install -r requirements.txt`
4. `python manage.py migrate`
5. `python manage.py runserver`
6. Abra `http://127.0.0.1:8000/`

## Render
O projeto mantém `render.yaml`, `start.sh`, `requirements.txt` e configuração de produção existentes. Não foram adicionadas dependências novas para a interface.
