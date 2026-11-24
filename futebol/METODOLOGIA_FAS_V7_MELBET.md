# METODOLOGIA FAS V7.5 (MELBET ENGINE & ANTI-CORRELATION EDITION)

**Vigência:** A partir de 21/11/2026.  
**Alvo:** Otimização para casas da plataforma BetB2B (Melbet / 1xBet) e Gestão Quantitativa Anti-Hecatombe.

---

## 🚀 AS 6 REGRAS MESTRAS DO FAS V7.5

### 1. Stop 2 com Proteção DNB (Empate Anula / Handicap 0.0)
* **Regra:** O Stop Point 2 da SAFE substitui a Moneyline Seca (ML) vulnerável por **Empate Anula Aposta (DNB / Handicap 1 (0) ou Handicap 2 (0))**.
* **Regra de liquidação:** Se o favorito empatar, a odd daquela perna vira **@1.00 (reembolso)**; as demais pernas ainda podem perder e o resultado líquido do bilhete não é garantido.

### 2. Super Ataque Focado em Over Gols Totais / Over do Time (Anti-Trap BTTS)
* **Regra:** Proibido selecionar *Ambos os Times Marcam (BTTS Sim)* em jogos com abismo técnico evidente onde o favorito tende a golear de zero (clean sheet).
* **Aplicação:** Linhas de **Mais de 2.0 / Mais de 2.5 Gols Totais** ou **Total da Equipe Favorita Mais de 1.5** são mercados candidatos e ainda exigem evidência própria; placares de goleada não garantem acerto futuro.

### 3. Múltipla 5 no Formato de Aposta de Sistema (Sistema 6/8 e 7/8 na Melbet)
* **Regra:** A Múltipla 5 (O Improvável) é montada com 8 seleções horizontais, mas com recomendação de preenchimento na Melbet como **"Aposta de Sistema"**.
* **Benefício:** Com 6 ou 7 acertos, um sistema aceito pela casa pode gerar retorno conforme suas combinações, odds e regra de liquidação. Trate qualquer número histórico como declaração até confirmar o recibo.

### 4. Nomenclatura e Preenchimento Nativo Melbet (Anti-Eventos Dependentes)
* **Regra:** Mercados combinados (ex: *Vitória & Mais de 1.5 Gols*) devem ser informados indicando a aba exata da Melbet: **"Tempo Regulamentar + Total"** (ex: `V1 e Total Mais de 1.5 - Sim`), impedindo o travamento do cupom.

---

## 🛡️ NOVAS REGRAS ANTI-CORRELAÇÃO E GRADE CURTA (UPGRADE V7.5)

### 5. Regra de Ouro: Limite Máximo de Exposição por Time (Cap de Correlação ≤ 2 Bilhetes)
* **Diagnóstico da Falha de 20/11:** O Bayern de Munique e o Athletic Bilbao estavam presentes em 6 bilhetes simultâneos (Supremo, SAFE, SAFE+, Ataque, Dupla, Soros). A zebra nesses 2 jogos causou efeito dominó e aniquilou a grade inteira.
* **Regra Estrita:**
  1. **Cap Geral:** **Nenhum time ou partida individual pode constar em mais de 2 bilhetes na grade diária.**
  2. **Isolamento Absoluto do Desafio Soros:** O jogo selecionado para o Desafio Soros **NUNCA PODE SER O MESMO** do Bilhete Supremo nem o âncora da SAFE. O Soros deve correr em uma raia 100% isolada para que um tropeço na grade regular não afete a jornada de 30 dias.
  3. **Descorrelação de Mercados:** Se uma partida for inevitável em 2 bilhetes, ela deve estar em mercados estatisticamente independentes (ex: em um bilhete é *Gols Totais Over 1.5* e no outro é *Escanteios* ou *Dupla Chance do Visitante*).

### 6. Protocolo de Grade Curta (Short Slate Protocol — Dias com Poucos Jogos)
* **Gatilho:** Rodadas com **menos de 8 a 10 jogos no radar com dados de qualidade** (típico de segundas-feiras, sextas reduzidas ou pós-data FIFA).
* **Proibição de Inflar Bilhetes Artificiais:** Em dias com poucos jogos, é expressamente **PROIBIDO** gerar 6 ou 7 bilhetes múltiplos reciclando as mesmas partidas. Isso gera uma falsa ilusão de diversificação que na verdade multiplica o risco.
* **Estrutura Compacta Obrigatória em Dias de Poucos Jogos:**
  - ⭐ **1x Bilhete Supremo** (Foco principal do dia).
  - 🛡️ **1x Múltipla SAFE** (com jogos 100% diferentes do Supremo).
  - 🎯 **1x Desafio Soros** (com jogo 100% diferente de ambos).
  - *(Múltiplas secundárias como Neto, Ataque e Improvável ficam AUTOMATICAMENTE SUSPENSAS para preservar a banca).*

## Resolução operacional V7.5 — limiar, sistemas e Brasileirão

Esta seção esclarece as regras da V7.5 para aplicação consistente com o prompt FAS3 V5. Em conflitos de quantidade e exposição, a V7.5, vigente desde 21/11/2026, prevalece para a grade operacional; o prompt V5 continua orientando o scanner e a análise que não conflitam com estas travas.

1. **Limiar de grade curta:** conte fixtures únicos que passaram pelos critérios de qualidade, não seleções nem ocorrências em bilhetes. `0–9` fixtures é grade curta; `10` ou mais é grade cheia. A escolha de `10` como limite superior interpreta conservadoramente o intervalo ambíguo “menos de 8 a 10”. Registre a contagem antes de montar os bilhetes. Sem contagem, marque revisão; ainda aplique as travas V7.5 que forem inequívocas.
2. **Estrutura curta:** uma aposta Supremo, uma SAFE e um Soros. SAFE e Supremo não compartilham fixtures. Ataque, SAFE+, Improvável, Neto e múltipla própria do Brasileirão ficam suspensos como apostas. O FAS Rodada continua permitido como scanner informativo, sem stake ou cupom.
3. **Improvável em grade cheia:** oito seleções horizontais e somente Sistema `6/8` ou `7/8`. Sistema `5/7`, acumulada simples rotulada como sistema, quantidade diferente de oito ou formato ausente não recebe conformidade. A orientação antiga do prompt V5 de 10–14 seleções não se aplica a uma grade operacional V7.5.
4. **Brasileirão:** com mais de três fixtures qualificados do Brasileirão no mesmo dia e grade cheia, o prompt V5 permite a múltipla da rodada, sujeita ao teto de exposição. Em grade curta, prevalece a suspensão V7.5 para aposta secundária; a análise FAS Rodada pode continuar sem aposta.
5. **Exposição e isolamento:** conte cada fixture e equipe no máximo uma vez por bilhete, inclusive em sistemas e entre os Stop Points da SAFE. O limite é dois bilhetes por equipe e por fixture. Soros não pode compartilhar fixture com nenhum jogo do Supremo nem com a âncora do Stop 1 da SAFE. “Diferente do Supremo/âncora” não significa “exclusivo na grade”: reporte as duas condições separadamente.
6. **Independência:** mercados distintos não provam independência. A metodologia cita gols e escanteios como exemplo de famílias independentes; qualquer outro par no mesmo fixture sem justificativa explícita fica em revisão. A revisão não ganha selo de conformidade.
7. **SAFE:** Stop 2 deve declarar DNB/Handicap 0. Se faltar essa declaração, a grade não recebe selo conforme.

**Exemplos de fronteira:** 9 fixtures qualificados → compacta, sem Improvável nem cupom Brasileiro; 10 → grade cheia, na qual 4 fixtures qualificados do Brasileirão permitem a múltipla específica se o cap ainda for respeitado. Em grade cheia, Improvável 6/8 com oito pernas é permitido; 5/7 com sete pernas é violação.
