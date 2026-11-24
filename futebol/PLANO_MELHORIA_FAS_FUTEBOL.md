# Plano de melhoria do FAS Futebol

**Projeto de execução** — `C:\Users\Pichau\Downloads\project\26\tips2.0`. Todos os caminhos abaixo são relativos a essa raiz. Este roteiro complementa `futebol/PLANO_ARQUITETURA_AUTOMACAO_FAS.md`. O objetivo é conseguir reproduzir uma rodada, corrigir a liquidação e medir se as mudanças melhoram a seleção de mercados. A auditoria de 21 e 23/11/2026 fornece casos de regressão, não uma estimativa de desempenho futuro.

## Instrução para o modelo executor

Execute a primeira etapa ainda aberta. Leia apenas os arquivos indicados e seus chamadores diretos. Antes de editar, confirme a raiz e identifique alterações existentes do usuário. Trabalhe no fluxo de futebol usado pelo CLI e pelos agendamentos. Preserve o basquete, os relatórios originais e os formatos lidos por notificadores e simuladores. Reutilize funções e testes existentes. Se precisar de dados de teste, use cópias temporárias. Para validar localmente, substitua Telegram, sincronização pública e chamadas externas por adaptadores de teste. Não efetue apostas. Não apresente uma etapa como concluída se algum critério de aceite falhar.

Ao encerrar cada etapa, informe arquivos alterados, comando de teste reproduzível, resultado observado e próxima etapa. Se outro modelo assumir, entregue esse resumo junto com este plano. Uma etapa por vez permite usar um contexto curto.

## 1. Fixar a base de comparação

**Entradas.** `fas_cli.py`, workflows em `.github/workflows/`, `futebol/fas_engine.py`, `futebol/confere_engine.py`, `futebol/bilhetes_ativos.json` e trechos datados da base de backtest. Localize qual rotina lê, modifica e publica cada arquivo. Confira se arquivos na raiz são cópias antes de contar uma rodada duas vezes.

**Entrega.** Criar casos de teste locais de 21/11 e das trilhas A e B de 23/11. Anotar a procedência dos campos. Distinguir stake e retorno declarados no projeto de valores confirmados por recibo. Quando faltar composição pré-jogo, conservar a lacuna.

**Aceite.** O replay bruto identifica cinco bilhetes operacionais em 23/11, R$ 64,80 de stake declarada e R$ 0 de retorno. O Soros teórico de R$ 17,94 fica exclusivamente na trilha A. O sistema A tem 2/8 acertos e o B tem 0/7. Se uma cópia divergir, mostrar o caminho e o campo divergente.

## 2. Congelar cada versão da grade

**Entrega.** No fluxo matinal e de revalidação, salvar um snapshot datado antes da liquidação. Identificar versão da metodologia, trilha, horário com fuso, versão anterior, motivo da troca, bilhete, stake total e componentes. Para cada seleção registrar partida, início, período, mercado, lado, linha, odd, horário e origem da cotação. Manter o JSON ativo como interface compatível. Registrar a liquidação vinculada ao snapshot. Campos desconhecidos em registros antigos devem ficar explicitamente desconhecidos. Não inferir retrospectivamente a ordem das âncoras.

**Aceite.** Revalidar gera B e preserva A. Reexecutar o mesmo evento não duplica entradas. Uma falha de gravação deixa disponível a última versão íntegra. A seleção de um jogo já iniciado fica fora da nova grade pré-jogo. Um leitor existente continua abrindo o JSON ativo.

## 3. Aplicar as regras antes de divulgar o bilhete

**Entradas.** `futebol/METODOLOGIA_FAS_V7_MELBET.md` e `FAS_PROMPT_MESTRE_EXECUCAO_DIARIA.md`. Formalizar, com exemplos, quais regras valem em cada versão. Resolver explicitamente o limiar ambíguo “menos de 8 a 10”, os formatos de sistema permitidos e se o Brasileirão é admitido em grade curta. Não importar limites financeiros de outra cópia do projeto sem confirmar sua adoção. Enquanto houver ambiguidade real, marcar o caso como revisão e prosseguir com as regras inequívocas.

**Entrega.** Validar por trilha e por conjunto de bilhetes efetivamente simultâneos. Contar cada equipe e partida uma vez por bilhete, incluindo sistemas. Reportar também a stake dos bilhetes envolvidos e a exposição das combinações internas. Distinguir “diferente do Supremo e da âncora” de “exclusivo na grade”. Mercados diferentes não bastam para demonstrar independência. Validar formato da grade curta, exclusão de secundários, proteção DNB declarada e incompatibilidades entre seleções. Uma violação deve impedir o selo de conformidade e identificar os bilhetes afetados.

**Aceite.** Na B de 23/11, detectar Inter, Botafogo e Santos em três bilhetes cada, o Improvável em uma grade declarada curta e a SAFE sem DNB. Em 21/11, apontar a repetição de Palmeiras–Flamengo no Soros e no Ataque. A avaliação mostra qual definição de isolamento foi satisfeita. Testar uma grade conforme e uma grade vazia.

## 4. Corrigir cotação, liquidação e saldo

**Entrega.** Centralizar a aritmética em uma rotina utilizada pelo fluxo real. Distinguir simples, acumulada, variantes de stop e sistema k/n. Em odds decimais, a acumulada multiplica as odds vencedoras, usa fator 1 em anulação e zera com uma derrota. Para sistemas, distribuir a stake total entre as combinações aceitas e somar seus retornos. Respeitar a regra documentada de arredondamento da casa ou identificar a simulação como estimativa. Registrar retorno bruto e resultado líquido em campos distintos. Usar recibo quando houver boost, combinação especial, taxa ou diferença de odd. Sem suporte para uma regra de liquidação ou sem resultado verificável, manter pendente. Atualizar o ciclo e o cofre Soros uma única vez por liquidação operacional.

| Caso de regressão | Resultado esperado |
|---|---|
| Stops de 21/11 | Produtos publicados por perna dão aproximadamente 1,64 e 1,74. Sinalizar discrepâncias com 1,76 e 2,72. |
| SAFE B de 23/11 | 1,22 × 1,22 × 1,35 dá 2,01 arredondado. Investigar 1,82. |
| DNB empatado e outra perna perdida | DNB anulado e bilhete perdido. Se as demais vencerem, pagar o produto das vencedoras. |
| 6/8 em 21/11 | 28 combinações. Com as seis odds ganhadoras publicadas e divisão igual, retorno estimado de 0,1522 por unidade. Verificar aceitação dos mercados do mesmo jogo antes de chamar o valor de realizado. |
| 5/7 com zero acertos | 21 combinações, retorno zero. |
| Repetição do CONFERE | Mesmo saldo e mesmo estado Soros após duas execuções. A trilha teórica nunca movimenta a banca operacional. |

## 5. Fazer o CONFERE apresentar somente resultados rastreáveis

**Entrega.** Remover os placares fixos de `futebol/confere_engine.py`. Produzir o resumo com as seleções do snapshot e evidências de resultado vinculadas à mesma partida, data e período. Preservar fonte e horário. Um placar final não liquida por si só mercado de primeiro tempo ou escanteios. Se relatório, JSON e recibo divergirem, mostrar a divergência. Gerar a mensagem em modo local antes de qualquer publicação.

**Aceite.** A mensagem de 23/11 não contém jogos fixos de 20/11. Exibe A e B com seus próprios denominadores. Fonte faltante produz pendência. Falha do notificador não altera saldo nem duplica liquidação no retry. Validar via entrada normal com envio e sincronização substituídos em teste.

## 6. Medir assertividade e testar uma melhoria por vez

**Entrega.** Derivar o painel das seleções liquidadas. Para assertividade, deduplicar por partida, período, mercado, lado e linha dentro de cada estratégia avaliada. Contar ocorrências por bilhete separadamente para medir concentração. Mostrar HIT, MISS, VOID e pendentes, taxa HIT/(HIT+MISS), cobertura por rodada, tamanho da amostra, retorno e ROI com stake conhecida. Com denominador zero, exibir “sem amostra”. Separar versões, simulação e execução. Reconciliar os 31/47 do painel legado com os 24/37 das grades examinadas de setembro antes de adotar qualquer dos dois como referência geral.

**Experimento inicial.** Fixar ranking e composição antes do kickoff. Nas mesmas rodadas elegíveis comparar a primeira SAFE, a dupla das duas primeiras de jogos distintos e a múltipla completa, com a mesma stake total simulada. Quando dupla e completa coincidirem, identificá-las como a mesma composição. Registrar dias sem aposta e motivo de troca A→B. Separar troca por dado esportivo da troca por perda de horário. Se houver probabilidade declarada, registrar definição e origem antes do resultado e posteriormente avaliar calibração e Brier nas previsões aplicáveis. FAS Score ordinal não pode alimentar esse cálculo como percentual.

**Aceite.** O painel é reproduzível a partir dos snapshots, explica o denominador de cada métrica e não mistura o green teórico com o saldo realizado. Antes de coletar novas rodadas, definir a métrica primária, o período de avaliação e a comparação pareada. Só propor promoção de uma variante após relatar tamanho e incerteza da diferença, cobertura e impacto financeiro. Duas rodadas servem para validar o software, não para declarar uma estratégia superior.

## Conclusão da entrega

Rodar o fluxo local completo com uma grade válida, uma inválida, uma revalidação e uma rodada parcialmente liquidada. Repetir a liquidação e conferir os saldos. Entregar o comando de replay, resultados das regressões e decisões ainda pendentes. Revisar a linguagem do prompt e da metodologia para que “conforme”, “premiado”, “lucrativo” e “probabilidade” só apareçam quando a respectiva evidência estiver disponível.

## Registro da conclusão local — 24/11/2026

- Replay em diretório temporário: grade conforme aceita e congelada; grade inválida bloqueada antes de notificar/sincronizar; revalidação V1→V2 preservou V1 e ligou V2 à versão anterior; CONFERE parcial manteve uma seleção HIT e outra PENDING; retry não duplicou liquidação nem movimentou Soros sem recibo.
- Testes foram executados com notificações substituídas e caminho de sincronização inexistente. Nenhuma aposta, mensagem ou sincronização pública foi realizada.
- Os prompts diários de futebol e basquete foram incorporados a `FAS_PROMPT_MESTRE_EXECUCAO_DIARIA.md`; os dois arquivos antigos foram removidos para evitar seleção acidental. As metodologias seguem separadas por esporte.
- Revalidação de basquete registrada em `basquete/REVALIDACAO_LOCAL_FAS_BASQUETE_2026-11-24.md`. Não foram alterados os históricos de partidas.
- **Pendência de dados:** não há snapshots históricos de futebol nesta cópia, e as fontes locais não contêm a procedência dos totais 31/47 e 24/37. O painel retorna “sem amostra”; nenhum total legado foi promovido a baseline e a Etapa 6 não autoriza concluir superioridade de estratégia.
