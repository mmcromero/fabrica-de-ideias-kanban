# Fábrica de Ideias Kanban · Documentação

Atualizado em 08/11/2026. Este documento registra o que foi feito, por que, o que foi testado e o que falta. Qualquer relatório sobre o projeto deve sair daqui.

Nome oficial do add-on: **Fábrica de Ideias Kanban**. Pasta: `/addons/kanban/`. Nome do add-on no histórico anterior: "Artesão Digital — Kanban".

## 1. Versões

| Versão | Situação | Resumo |
|---|---|---|
| 0.0.1 | Histórico | Primeiro add-on local, interface com dados simulados (`mock.json`), `config.yaml` com Ingress na porta 8099. |
| 0.0.3 | Histórico | Ponte com Node-RED. Opção antiga de porta `:80` corrigida para `:1880` pelo servidor. |
| 0.0.5 | Histórico | Servidor com validação de origem (Supervisor), cabeçalhos de escrita e verificação de certificado do Node-RED. |
| 0.0.6 | Histórico | Interface com colunas por labels C1–C6 e movimentação por GitHub App. |
| 0.0.7 | Histórico | `config.yaml` com versão 0.0.7, confirmada por captura de tela da tela de add-ons. |
| 0.0.8 | Histórico | Migração para GitHub Projects V2. Chamada direta ao GitHub com token nas opções. Colunas dinâmicas. |
| 0.0.9 a 0.0.12 | Histórico | Ajustes de interface (atualização otimista, aviso de exclusão, seletor de cores), versão dinâmica no cabeçalho, correções de janela de colunas. |
| 0.0.14 (código atual) | Em uso | Remoção das regras de evidência e motivo do servidor. Registrado no `server.py` como `VERSION = '0.0.14'`. Número a confirmar contra o `config.yaml`. |

Procedimento para subir versão: alterar **dois lugares**, `config.yaml` (campo `version`) e `server.py` (constante `VERSION`). O cabeçalho da interface lê a versão do servidor e não precisa de alteração.

Nomes de arquivo oficiais: `config.yaml`, `Dockerfile`, `server.py`, `public/index.html`, `icon.png`, `logo.png`. Nomes com "(1)" ou "(2)" e extensões `.txt` de upload não são referência.

## 2. Decisões

| Data | Decisão | Quem |
|---|---|---|
| 07/11/2026 | Alvo dos testes: Project "Teste HA". Tudo que estiver nele é de teste e pode ser alterado. | Dono do projeto |
| 07/11/2026 | Labels C1–C6 saem do sistema. Colunas passam a ser as opções do campo Status do Project. Histórico do método anterior preservado na seção 3. | Dono do projeto |
| 07/11/2026 | Todo quadro novo nasce com as colunas A fazer, Em execução e Concluído. Colunas podem ser adicionadas e renomeadas. Criação de quadro novo pela interface fica para versão posterior. | Dono do projeto |
| 07/11/2026 | Node-RED e GitHub App saem do fluxo. Chamada direta ao GitHub a partir do add-on, com token nas opções. | Dono do projeto |
| 07/11/2026 | Auditoria: arquivo local `/data/audit.jsonl`, campos no Project (a validar) e histórico do comentário na Issue. | Dono do projeto |
| 07/11/2026 | Token atual (exposto em registros compartilhados) fica em uso até o fim dos testes. Troca é item de backlog, com gatilho na seção 5. Troca pela aba Configuração do add-on. | Dono do projeto, com ciência da equipe responsável pela conta |
| 07/11/2026 | Cor das colunas: seletor de bolinhas com as 8 cores do GitHub (cinza, azul, verde, amarelo, laranja, vermelho, rosa, roxo). Gravada no Project e sincronizada. Hexadecimal descartado porque o GitHub não aceita. | Dono do projeto |
| 07/11/2026 | Não permitido apagar coluna que contenha cards. Aviso aparece dentro da janela de colunas. | Dono do projeto |
| 08/11/2026 | Regras de evidência (coluna de destino) e motivo (ao sair de coluna) removidas do servidor e da interface. A janela de colunas mostra nome, cor e ordem. | Dono do projeto |
| 08/11/2026 | Nome oficial do add-on: Fábrica de Ideias Kanban. | Dono do projeto |
| 08/11/2026 | Versão dinâmica: o cabeçalho mostra a versão devolvida pelo servidor. | Dono do projeto |

## 3. Método anterior (preservado para rastreabilidade)

Não deve ser usado. Fica registrado caso seja preciso consultar ou auditar operações antigas.

- **Cartões:** GitHub Issues do repositório `mmcromero/fabricacao_e_orcamentos`.
- **Colunas:** labels `C1` a `C6` nas Issues. Issue sem label ou com mais de uma label C fica em "Não classificadas".
- **Movimentação:** GitHub App via Node-RED (`a0d7b954_nodered`), endpoint `/endpoint/kanban/bridge`, com `@octokit/auth-app`.
- **Auditoria:** comentário na própria Issue a cada movimentação. Origem dessa exigência ainda não confirmada com a equipe anterior.
- **Regras:** evidência obrigatória para C5 (Em homologação) e C6 (Concluído); motivo obrigatório para reabrir uma Issue em C6. Removidas em 08/11/2026.
- **Ordenação:** pela data de atualização (`updated_at`). Não havia ordenação vertical persistente.
- **Segredo:** arquivo `/share/github-projects-auth/kanban-bridge-secret`, usado pela ponte com Node-RED.
- **Verificação de certificado:** cadeia, SNI e folha do certificado do Node-RED comparadas com `/ssl/fullchain.pem`.

## 4. O que foi testado

**Teste de viabilidade (07/11/2026):** token clássico de escopo `project`, conta gratuita, fora do Home Assistant (PowerShell no Windows do dono). Aprovado:
- Autenticação por API; criação de projeto; criação de visualização Kanban (REST, opcional).
- Criação de card rascunho e colocação numa coluna (dois passos).
- Movimentação entre colunas; adição, renomeação e reordenação de colunas mantendo os IDs.
- Apagar coluna com card: o card vai para "sem status".
- Reordenação de cards: posição definida pelo card logo acima.

**Testes pelo add-on (log de 08/11/2026, versão 0.0.12):**
- Leitura do Project e do campo Status: aprovada (cards e colunas carregados).
- Chamadas `/api/move`, `/api/reorder` e `/api/columns` retornaram 200 em várias ocasiões; duas chamadas a `/api/columns` retornaram 400 (motivo não registrado no log).
- Status 200 não confirma gravação: a confirmação depende de `verified: true` e de conferência no GitHub.

**Ainda não testado:**
- Mover um card pelo botão, conferido no GitHub.
- Reordenação conferida no GitHub.
- Exclusão de coluna com card (aviso na janela de colunas).
- Troca de cor de coluna mantida sem afetar os cards.
- Devolução da cor pelo GitHub (`cor_confirmada` no audit.jsonl).
- Paginação com mais de 100 cards.
- Concorrência entre dois usuários.
- Chamadas a partir do Raspberry Pi (os testes de viabilidade foram do Windows).
- Acesso externo e MFA.
- Auditoria por campos do Project e limites de tamanho.
- Reinício do Home Assistant observado em 08/11/2026: causa não identificada no log do add-on.
- Parada do add-on pelo botão Parar mostrando estado de erro (bolinha vermelha) em vez de "parado".

## 5. Pendências e gatilhos

| Item | Quando | Gatilho |
|---|---|---|
| Concluir testes da seção 4 | Agora | Dono executa e envia novo log e `audit.jsonl` |
| Trocar token (exposto) | Antes de qualquer dado real | Fim dos testes. Dono troca em Configuração, revoga o token antigo no GitHub e avisa todos os envolvidos. |
| Confirmar origem da auditoria por comentário | Antes de desligar o método antigo | Conversa com a equipe anterior |
| Exposição externa do Home Assistant | Antes de uso fora do teste | Ativar MFA (pendente no inventário) |
| Estado "erro" ao parar o add-on | Próxima versão | Capturar log no momento da parada; tratar SIGTERM se confirmado |
| Nome da interface | Quando o dono decidir | Hoje o cabeçalho e o `<title>` dizem "Fabrica de Ideias · Kanban"; o nome oficial é "Fábrica de Ideias Kanban" |
| Alinhar versões do `config.yaml` e do `server.py` | Antes da próxima instalação | Confirmar o número único |
| Criação de quadro novo pela interface | Versão posterior | Depois de validar a leitura e a escrita |
| Concorrência entre usuários | Depois dos testes atuais | Teste com dois usuários |
| Backup e recuperação | Antes de uso real | Definir com o dono |
| Separação dos dados do Artesão Digital | Antes do Kanban Independente | Decisão de arquitetura |
| Termos de uso do GitHub para automação | Antes de uso real | Verificação com o dono |

## 6. Configuração

Todas as opções aparecem na aba Configuração do add-on:

| Opção | Valor de teste | Para que serve |
|---|---|---|
| `github_token` | (token atual) | Token de acesso. Troca: colar novo valor, salvar e reiniciar. |
| `github_owner` | (dono do Project Teste HA) | Dono do Project. |
| `github_project_number` | (número do Project Teste HA) | Número do Project. |
| `github_status_field` | `Status` | Nome do campo de coluna. |

Ao trocar qualquer valor, reinicie o add-on. Para virar ambiente final, troque os valores acima, sem mexer no código.

## 7. Arquivos de auditoria

- `/data/audit.jsonl`: uma linha por ação (mover, ordenar, editar colunas), com data, versão, usuário do Ingress, item e resultado da releitura (`verificado`). Em colunas, registra também `cores_depois` e `cor_confirmada`. Não contém o token.

## 8. Como testar

1. Instalar a versão atual no add-on pelo repositório local.
2. Conferir a configuração do item 6.
3. Abrir o Kanban pelo menu lateral e conferir as colunas Todo, In Progress e Done.
4. Mover um card pelo botão "Mover" e conferir no GitHub.
5. Mover um card no GitHub, clicar em "Atualizar" e conferir a nova coluna.
6. Reordenar dois cards na mesma coluna e conferir no GitHub.
7. Adicionar uma coluna, renomear uma e tentar apagar uma com card (deve bloquear, com aviso na janela).
8. Conferir `/data/audit.jsonl` e enviar o conteúdo.