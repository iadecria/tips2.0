# Etapa 6 — painel e protocolo experimental

Data da implementação: 24/11/2026. O painel reproduz somente dados ligados a snapshots pré-jogo e liquidações com o mesmo `snapshotId`. Seleções são deduplicadas por partida, período, mercado, lado e linha dentro da versão/metodologia, estratégia e modo. Contagem por bilhete permanece separada para medir repetição. HIT/(HIT+MISS) exclui VOID e PENDING. ROI usa retorno bruto confirmado por recibo e stake conhecida; valores simulados ficam em grupo separado e não viram banca executada. Denominador zero resulta em “sem amostra”.

## Experimento pré-registrado

- **Métrica primária:** diferença pareada de ROI líquido por rodada elegível, com stake simulada fixa de uma unidade total por variante.
- **Variantes:** primeira SAFE; dupla das duas primeiras seleções de partidas distintas; múltipla completa. Se dupla e múltipla completa tiverem a mesma composição, contam como uma variante.
- **Período:** 30 rodadas elegíveis consecutivas, limitadas a 90 dias. Rodadas sem aposta entram na cobertura com motivo; mudanças A→B distinguem atualização de dado esportivo de perda de horário.
- **Regra de promoção:** não promover antes de 30 pares. Reportar cobertura, tamanho da amostra, diferença pareada, intervalo bootstrap de 95% e impacto financeiro. Probabilidade/Brier só se houver probabilidade numérica e origem registradas antes do kickoff; FAS Score ordinal fica excluído.

## Reconciliação do histórico

O plano cita os totais 31/47 e 24/37, mas esses pares não aparecem nas fontes locais examinadas e não há snapshots datados de futebol nesta cópia. O painel acumulado legado da base começa com outras somas (por exemplo, 33/28 para SAFE individual e 95/62 no total de singles) e não define uma chave de deduplicação compatível com a Etapa 6. Logo, não é possível reproduzir ou reconciliar 31/47 contra 24/37 sem a lista de partidas/seleções que formou cada denominador. Nenhum desses totais foi adotado como baseline. O comando atual retorna `sem amostra`, corretamente, até haver snapshots e liquidações estruturadas.

## Estado de aceite

O código e o protocolo estão implementados e cobertos por fixtures sintéticas. O aceite histórico segue pendente: faltam snapshots/liquidações estruturados no repositório e a origem dos dois totais conflitantes. As duas rodadas recentes não sustentam conclusão de desempenho nem promoção de estratégia.
