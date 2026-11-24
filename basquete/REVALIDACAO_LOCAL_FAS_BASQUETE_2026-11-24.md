# Revalidação local do FAS Basquete — 24/11/2026

## Escopo

Leitura somente local de `bilhetes_ativos.json`, `soros_state.json`, `fas_engine.py`, do prompt mestre e da base histórica. Nenhuma rotina de envio/sincronização foi executada e nenhum registro original foi alterado.

## Achados verificáveis

1. **A grade de 20/11 não é reproduzível como snapshot.** O JSON ativo tem `status: SETTLED`, placares e resultados declarados, mas não há snapshot pré-jogo, fonte/horário por resultado nem recibo estruturado. Assim, os valores ficam como declarações do registro, sem confirmação independente.
2. **O estado Soros é aritmeticamente compatível com a declaração.** O registro diz stake R$ 10,00, retorno R$ 13,70, HIT e Dia 1; `soros_state.json` diz banca R$ 13,70 e próximo Dia 2. Não há recibo que confirme esse crédito.
3. **Dois placares do Bingo estão invertidos em relação ao quadro do mesmo JSON.** O quadro lista Toronto 105 × 102 Detroit e Washington 98 × 94 Chicago. As seleções Raptors @ Pistons e Wizards @ Bulls guardam, respectivamente, `102x105` e `94x98`. Os estados MISS dos picks coincidem com o quadro, mas os placares anexados às seleções não.
4. **A SAFE modular não tem liquidação operacional demonstrada.** Stop 1 está MISS e Stop 2 HIT, enquanto o ticket agregado está MISS e `actualReturn` é zero. Como o artefato não informa se os turnos foram executados com stakes independentes, não é possível afirmar o retorno do Stop 2.
5. **O fluxo atual de publicação não é seguro para replay local.** `run_basketball_pipeline()` formata a mensagem, chama Telegram e tenta `sync_public.py`; não cria snapshot, não valida estrutura e não oferece modo local. A rotina não foi invocada nesta revalidação.

## Resultado

Revalidação **parcial, com divergências de qualidade de dados e ausência de evidência de execução**. Os números de 7/9 picks e o Soros Dia 1 são preservados como declarações históricas, sem promover isso a desempenho confirmado. É necessário corrigir as anotações em uma nova versão/errata, nunca sobrescrever o original, e adotar snapshots e liquidação rastreável antes de reutilizar esses registros como amostra do painel.
