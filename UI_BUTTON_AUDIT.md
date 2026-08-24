# PassaMoz V3 — UI e Botões

## Melhorias implementadas

- Navegação lateral com estado ativo e menu móvel com overlay.
- Botão de modo claro/escuro com persistência no navegador.
- Contador global correto de notificações não lidas.
- Fecho das mensagens de sucesso/erro pelo utilizador.
- Feedback de carregamento em formulários para evitar duplo clique.
- Confirmação antes de ações destrutivas: cancelar, desativar, suspender, rejeitar e marcar como pago.
- Troca de origem/destino no formulário principal.
- Pesquisa redesenhada com resultados em cartões e ação clara “Ver viagem”.
- Removida a falsa interação em que cada número de lugar na pesquisa parecia ser um botão de reserva.
- Página de pagamento com estados diferentes para pendente, processamento, pago e expirado.
- Contador visual dos 15 minutos de bloqueio da reserva.
- Painel da operadora redesenhado com navegação própria e cartões de estado.
- Painel administrativo com atalhos para Operadoras, Mensalidades e Administração Django.
- Estilos responsivos para telemóvel, tablet e computador.
- Estados de foco, hover, disabled e loading padronizados.
- Melhorias de contraste e suporte visual ao modo escuro.

## Verificação

- Todos os arquivos Python passam pela compilação de sintaxe (`compileall`).
- O `manage.py check --deploy` deve ser executado no ambiente que tenha as dependências do `requirements.txt` instaladas, pois o ambiente de edição não possui Django instalado.
