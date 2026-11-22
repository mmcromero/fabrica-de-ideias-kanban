# UX-STD-001 - Organiza��o de telas com prioridade para celular

Vers�o: 0.1 � Data: 22/11/2026 � Estado: proposta pronta para ado��o.

## 1. Objetivo e aplica��o

Organizar as telas por tarefa. Mostrar o essencial primeiro. Permitir acesso claro aos detalhes. Reduzir a rolagem que decorre da mistura de fun��es na mesma p�gina.

Esta proposta se aplica a sistemas de gest�o, pain�is, cadastros e aplicativos web do portf�lio. Cada produto mant�m sua identidade visual. P�ginas de leitura, conversas e outros conte�dos cont�nuos precisam de avalia��o pr�pria.

O documento define organiza��o e intera��o. N�o define toda a identidade visual de um design system. N�o altera projetos existentes nem comprova conformidade completa com WCAG.

## 2. Base da proposta

| Conceito | Significado pr�tico |
| --- | --- |
| Arquitetura da informa��o | Definir grupos, nomes, rela��es e caminhos de acesso. |
| Agrupamento por tarefa | Reunir o que a pessoa precisa para alcan�ar um objetivo. |
| Divulga��o progressiva | Mostrar fun��es frequentes primeiro e oferecer detalhes sob demanda. |
| Navega��o por abas | Alternar entre poucas se��es relacionadas, com uma se��o vis�vel por vez. |
| Layout adaptativo | Ajustar a organiza��o ao espa�o dispon�vel e � forma de uso. |

N�o h� uma regra universal que determine que toda tela deve usar abas ou caber sem rolagem. A combina��o abaixo � uma decis�o de projeto, baseada nas fontes da se��o 10 e na prefer�ncia do propriet�rio. Sua efic�cia deve ser verificada no uso.

**Princ�pio central: cada tela deve ter uma tarefa principal clara e mostrar primeiro os dados e as a��es necess�rios para essa tarefa.**

## 3. Como escolher a organiza��o

| Necessidade | Padr�o preferido | Cuidado |
| --- | --- | --- |
| Mudar de �rea do sistema | Navega��o principal com destinos e nomes claros | N�o misturar destinos com bot�es de a��o. |
| Alternar entre poucas se��es do mesmo assunto | Abas | N�o separar dados que precisam ser comparados lado a lado. |
| Consultar dados de um registro | Lista com acesso � tela de detalhe | Ao voltar, preservar busca, filtros e posi��o. |
| Abrir uma informa��o curta e opcional | Bloco expans�vel, como "Ver detalhes" | N�o ocultar avisos cr�ticos nem campos necess�rios � tarefa atual. |
| Configurar muitas categorias independentes | �ndice de categorias e subp�ginas | Evitar uma coluna de formul�rios completos. |
| Executar etapas com depend�ncia real | Fluxo por etapas | Mostrar progresso, permitir retorno e preservar dados. |
| Executar uma a��o curta sem sair do contexto | Di�logo ou painel inferior | Se houver muito conte�do ou teclado apertado, usar tela pr�pria. |
| Consultar muitos registros | Busca, filtros e pagina��o ou "Carregar mais" | Mostrar quantidade, estado de carregamento e acesso ao fim da lista. |

Abas e blocos expans�veis escondem conte�do. Use t�tulos que indiquem o que existe dentro. Preserve um resumo quando ele for necess�rio para decidir se vale abrir o detalhe.

## 4. Regras obrigat�rias para novas telas

### R01 - Definir a tarefa antes do layout

Registrar: pessoa usu�ria, objetivo da tela, a��o principal e dados necess�rios. Agrupar por uso e significado. Evitar copiar a estrutura t�cnica do banco de dados para a interface.

### R02 - Separar navega��o global e local

No celular, considerar barra inferior para 3 a 5 destinos principais, quando o produto tiver essa estrutura. Para menos destinos, usar uma navega��o simples. Para mais destinos, selecionar os frequentes e oferecer acesso claro aos demais. Em telas amplas, considerar navega��o lateral. Estes padr�es n�o obrigam a usar Material ou uma biblioteca espec�fica. [S3]

Dentro de uma �rea, usar abas apenas quando as se��es forem relacionadas e puderem ser consultadas separadamente. Usar links para navegar entre p�ginas; usar o padr�o acess�vel de abas para alternar pain�is na mesma p�gina. [S2, S4]

### R03 - Manter as abas vis�veis e compreens�veis

Preferir de 2 a 4 abas locais. Esta faixa � uma conven��o interna, n�o uma exig�ncia de acessibilidade. Usar r�tulos curtos e estado selecionado claro. As abas devem caber em uma linha na largura testada. Se n�o couberem, rever os grupos ou usar um �ndice de se��es. Evitar abas dentro de abas. N�o depender de arrastar para descobrir fun��es essenciais.

### R04 - Reduzir rolagem por meio da organiza��o

N�o colocar opera��o, cadastro, hist�rico e configura��o completos na mesma coluna. Apresentar resumos com acesso aos detalhes. Cards devem resumir ou dar acesso a uma tarefa; trocar se��es por cards longos n�o resolve o problema.

Na abertura, apresentar t�tulo, contexto e acesso � a��o principal. Permitir rolagem natural dentro do assunto atual. N�o usar altura fixa, corte de conte�do ou redu��o de fonte para fazer tudo caber. Evitar rolagens verticais aninhadas; permitir exce��es funcionais, como uma conversa, com teste de uso.

**Gatilho de revis�o:** se uma tela de opera��o ou configura��o passar de duas alturas �teis de conte�do no cen�rio de refer�ncia, revisar sua estrutura. Isso exige an�lise, n�o divis�o autom�tica. Registrar o tamanho da janela, o estado dos dados e a justificativa. Listas, texto ampliado e leitura cont�nua podem precisar de mais espa�o. Esse limite � uma heur�stica interna, sem validade universal.

### R05 - Preservar contexto e dados

Trocar abas ou abrir detalhes n�o pode apagar campos, sele��o ou filtros. Ao retornar a uma lista, restaurar a posi��o quando for apropriado. O bot�o Voltar deve seguir a navega��o do navegador quando houver mudan�a de rota. Se sair puder perder dados, oferecer uma forma clara de salvar ou descartar. N�o exigir confirma��o quando n�o houver perda.

### R06 - Manter a��es pr�ximas da tarefa

Destacar uma a��o principal por contexto. Manter a��es secund�rias acess�veis. Usar verbos claros: "Salvar produto", "Criar pedido", "Aplicar filtros". Usar barra fixa apenas se ela ajudar a execu��o. Ela n�o pode cobrir campos, mensagens ou controles. Considerar a �rea segura do aparelho e o teclado virtual.

### R07 - Oferecer resposta imediata

Indicar carregamento ou processamento ap�s a a��o. Prevenir envio duplicado enquanto o pedido estiver em andamento. Mostrar sucesso, falha ou pr�ximo passo. Preservar o que foi digitado quando houver erro. Em formul�rios com se��es ocultas, indicar a se��o com erro e abrir o campo necess�rio.

### R08 - Garantir acesso e leitura

Usar controles com r�tulos, foco vis�vel e opera��o por teclado. N�o transmitir estado apenas por cor. Implementar abas e blocos expans�veis conforme os padr�es WAI-ARIA aplic�veis, com HTML sem�ntico sempre que poss�vel. [S4, S5]

Adotar �rea de toque de pelo menos 44 � 44 pixels CSS nos controles comuns da aplica��o. Esse � um padr�o interno de conforto. O crit�rio WCAG 2.2 AA 2.5.8 estabelece 24 � 24 pixels CSS ou condi��es de exce��o; n�o confundir os dois valores. [S7]

Permitir reorganiza��o do conte�do a 320 pixels CSS de largura sem perda de informa��o ou fun��o e sem rolagem em duas dire��es, salvo conte�do que exige layout bidimensional. N�o bloquear zoom. [S6]

Manter texto comum com contraste m�nimo de 4,5:1; para texto grande, 3:1, conforme defini��o e exce��es do crit�rio 1.4.3. Verificar tamb�m os demais requisitos de acessibilidade aplic�veis. Barras fixas n�o devem cobrir o controle em foco; esta norma exige visibilidade integral, mais forte que o m�nimo do crit�rio 2.4.11. [S8, S9]

## 5. Modelos de tela

| Tipo | Estrutura inicial recomendada |
| --- | --- |
| In�cio | Resumo curto, pend�ncias e acesso �s tarefas frequentes. |
| Lista | T�tulo e a��o principal; busca; filtros; registros resumidos; controle de quantidade. |
| Detalhe | Identifica��o e estado; a��es; poucas se��es relacionadas; hist�rico sob demanda. |
| Cadastro curto | Campos necess�rios e a��o de salvar no mesmo contexto. |
| Cadastro extenso | Grupos de campos; etapas apenas quando houver sequ�ncia real; revis�o antes da conclus�o quando necess�ria. |
| Configura��es | �ndice de categorias e telas espec�ficas; resumo dos valores atuais quando �til. |
| Painel | Indicadores que apoiam a decis�o atual; relat�rios completos em destinos pr�prios. |

## 6. Exemplo ilustrativo - Central Editorial

Este exemplo n�o � uma auditoria da aplica��o existente.

| N�vel | Organiza��o proposta |
| --- | --- |
| Contexto da conta | Conta ativa vis�vel; troca de conta acess�vel, se houver v�rias contas. |
| �reas principais | Editorial � Mensagens � Contas � Ajustes. |
| Dentro de Editorial | Rascunhos � Agendados � Publicados. |
| Registro | Linha ou card curto com miniatura, t�tulo e estado. |
| Edi��o | Tela pr�pria com campos necess�rios e pr�via acess�vel. |
| Detalhes t�cnicos | Acesso espec�fico, conforme perfil e necessidade. |

Resultado esperado: a pessoa entra na �rea que precisa, localiza um registro e abre o detalhe. Todas as �reas n�o precisam aparecer como se��es completas na mesma p�gina. O resultado precisa ser testado com tarefas reais.

## 7. Crit�rios de revis�o e aceite

Cada nova tela deve registrar evid�ncias dos itens aplic�veis. Marcar "n�o aplic�vel" com uma raz�o. Uma captura de tela comprova apar�ncia, mas n�o comprova preserva��o de dados, teclado ou navega��o.

- [ ] A tarefa principal est� definida e os grupos t�m nomes claros.
- [ ] A a��o principal e o contexto aparecem na abertura do cen�rio de refer�ncia.
- [ ] N�o h� fun��es independentes empilhadas sem justificativa.
- [ ] Abas cabem, indicam sele��o e n�o separam informa��es de compara��o obrigat�ria.
- [ ] Conte�do oculto tem acesso claro; erros e avisos cr�ticos continuam percept�veis.
- [ ] Trocar de se��o e voltar preserva dados e contexto.
- [ ] Busca, filtros e retorno � lista funcionam com volume realista de registros.
- [ ] A interface informa carregamento, sucesso, erro e estado vazio.
- [ ] Controles funcionam com toque, teclado e leitor de tela nas tarefas avaliadas.
- [ ] Testes em 320, 360 e 390 pixels CSS de largura, com altura registrada, n�o mostram cortes nem sobreposi��es.
- [ ] Amplia��o de texto e zoom, teclado virtual e orienta��o horizontal foram avaliados.
- [ ] As barras fixas n�o cobrem conte�do ou foco.
- [ ] Telas que acionam o gatilho de comprimento foram revistas e t�m justificativa.
- [ ] O fluxo foi avaliado em aparelho m�vel real antes da homologa��o.

Os tamanhos de teste de 360 e 390 pixels s�o amostras internas. N�o definem a lista completa de aparelhos suportados. A avalia��o acima n�o equivale a uma auditoria completa de WCAG.

## 8. Indicadores para verificar se melhorou

Comparar o fluxo anterior e o proposto com as mesmas tarefas: localizar um item, editar e salvar, consultar hist�rico e voltar. Registrar tempo, erros, retornos desnecess�rios, perda de contexto e esfor�o percebido. Contar toques e dist�ncia de rolagem como apoio; um n�mero menor, sozinho, n�o comprova melhoria.

## 9. Texto reutiliz�vel para demandas e AGENTS.md

> Aplique UX-STD-001 na vers�o adotada pelo projeto. Planeje primeiro para celular. Defina a tarefa principal. Agrupe o conte�do por uso. Mostre o essencial e ofere�a detalhes sob demanda. Use abas para poucas se��es relacionadas que possam ser consultadas separadamente. Use telas pr�prias para tarefas extensas. Preserve dados, filtros e posi��o ao navegar. Evite empilhar fun��es independentes e evite rolagens aninhadas. Mantenha a��es claras, retorno imediato e acesso por teclado. N�o corte conte�do para reduzir a altura. Entregue o mapa das se��es e as evid�ncias dos crit�rios de aceite. Registre as exce��es com justificativa.

Para ado��o no portf�lio: escolher o reposit�rio central da norma, ajustar conflitos com regras j� existentes e referenciar sua vers�o nas instru��es dos projetos. Esta proposta n�o foi registrada em Git nem aplicada �s interfaces existentes.

## 10. Fontes consultadas

Consulta em 22/11/2026. As fontes sustentam os princ�pios e requisitos indicados. Quantidades de abas, gatilho de altura, modelos e checklist s�o decis�es desta proposta.

- S1 - Nielsen Norman Group, [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/): essencial primeiro e fun��es especializadas sob demanda.
- S2 - GOV.UK Design System, [Tabs](https://design-system.service.gov.uk/components/tabs/): crit�rios de escolha, compara��o entre se��es e limites do componente. Sua implementa��o em telas pequenas n�o � adotada automaticamente por esta norma.
- S3 - Android Developers, [Layouts and navigation patterns](https://developer.android.com/design/ui/mobile/guides/layout-and-content/layout-and-nav-patterns): navega��o principal, secund�ria e adapta��o ao espa�o. Orienta��es de aplicativo nativo usadas como refer�ncia, n�o como exig�ncia para web.
- S4 - W3C WAI-ARIA APG, [Tabs Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/): sem�ntica, sele��o e teclado.
- S5 - W3C WAI-ARIA APG, [Accordion Pattern](https://www.w3.org/WAI/ARIA/apg/patterns/accordion/): se��es expans�veis acess�veis.
- S6 - W3C, [Understanding Reflow - 1.4.10](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html).
- S7 - W3C, [Understanding Target Size (Minimum) - 2.5.8](https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html).
- S8 - W3C, [Understanding Contrast (Minimum) - 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html).
- S9 - W3C, [Understanding Focus Not Obscured (Minimum) - 2.4.11](https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html).

Limite da pesquisa: as orienta��es foram consultadas, mas nenhum projeto foi inspecionado e nenhum teste com usu�rios foi executado nesta entrega. N�o h� evid�ncia para prometer uma redu��o espec�fica de tempo, erros ou rolagem.
