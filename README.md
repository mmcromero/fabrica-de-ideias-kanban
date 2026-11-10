# Fábrica de Ideias Kanban

Código-fonte do add-on Home Assistant **Fábrica de Ideias Kanban**, versão de referência **0.0.25**.
Integração com **GitHub Projects V2**, por API no `server.py`, com interface em `kanban/public/index.html`.

## Estrutura

- `kanban/`: arquivos do add-on (manifesto, servidor Python, interface e imagens).
- `docs/DOCUMENTACAO.md`: documentação histórica recebida com a instalação local. Algumas referências a versões anteriores estão desatualizadas.
- `prototipos/`: interface e dados de demonstração antigos; não são incluídos no contêiner pelo Dockerfile.
- `scripts/verificar-fonte.py`: checagem local, sem conexão à rede, para conferência de versão e proteção inicial de credenciais.

## Segurança e instalação

- O valor padrão de `github_token` foi **esvaziado** em `kanban/config.yaml` antes da publicação.
- O token real deve ser fornecido **somente pela configuração do add-on** e armazenado fora do Git, no volume de dados do Home Assistant.
- Nunca versionar `/data/options.json`, `audit.jsonl`, `board_order.json`, backups ou credenciais.
- O token utilizado na instalação de testes foi anteriormente exposto em material compartilhado. Sua substituição e revogação devem ser planejadas fora deste repositório, preservando o serviço atual.
- Este repositório registra o código. **Publicar no GitHub não instala, atualiza nem migra o add-on local existente.**
- Não desinstalar a versão local aprovada sem plano de migração e backup.
- A distribuição automática pelo GitHub Actions **ainda não está configurada**; deverá ser especificada e validada separadamente.

## Verificação

```sh
python3 scripts/verificar-fonte.py
```

## Licença

Nenhuma licença de reutilização de terceiros foi concedida por este repositório. Um repositório público não torna o código automaticamente open source. A escolha da licença fica pendente de decisão do proprietário.
