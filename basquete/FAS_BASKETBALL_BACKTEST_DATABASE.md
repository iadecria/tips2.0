# FAS BASKETBALL — HISTÓRICO, BACKTEST E AUDITORIA DIÁRIA (V1.0)

Arquivo central de registro, auditoria e conferência contínua do **Basketball Analysis System (FAS Basketball V1.0)**.
Este arquivo preserva snapshots imutáveis, decisões pré-jogo, liquidações pós-jogo (CONFERE) e auditoria de erros (MISS AUDIT) para backtests futuros e comparação Multi-IA / Shadow.

---

## 📌 METODOLOGIA E CONTRATO DE AUDITORIA

- **Versão:** 1.0 (Laboratório Independente do FAS Football)
- **Schema:** `fas-basketball-import-v1`
- **Integridade Temporal:** Pre-match rigoroso. Proibido usar resultado posterior para reconstruir tese pre-match.
- **Competition Quality Gate:** `TIER_A` (WNBA, NBA), `TIER_B` (FIBA Intercontinental, EuroLeague, NBB, ACB), `TIER_C` (Ligas menores/Torneios curtos).
- **Auditoria de Miss:** Categorias permitidas: `STATISTICAL_VARIANCE`, `BAD_SELECTION`, `MISSING_CONTEXT`, `LINEUP_CHANGE`, `DATA_QUALITY`.
- **Status de Liquidação:** `HIT`, `MISS`, `VOID`, `PENDING`.

---

## 📅 REGISTRO POR DATA

---

### [2026-09-21] — RODADA DIÁRIA (CONFERE LIQUIDADO)

- **Data da Partida:** 2026-09-21
- **Competição:** WNBA 2026 (Temporada Regular)
- **Status de Liquidação:** **LIQUIDADO / AUDITADO**

#### 1. Dallas Wings @ Phoenix Mercury
* **Mercado Registrado:** Under 178,5 Pontos (Game Total Under)
* **Resultado Oficial:** Phoenix Mercury 87 × 86 Dallas Wings
* **Pontuação Combinada:** 87 + 86 = **173 Pontos**
* **Status:** ✅ **HIT**
* **Auditoria:** A tese pre-match de retenção de ritmo nos minutos finais de um jogo equilibrado sustentou a pontuação 5,5 pontos abaixo do teto de segurança. Cesta da vitória nos segundos finais por Kahleah Copper.

#### 2. Atlanta Dream @ New York Liberty
* **Mercado Registrado:** New York Liberty +6,0 (Spread Protegido)
* **Resultado Oficial:** New York Liberty 84 × 95 Atlanta Dream
* **Margem Efetiva:** New York 84 + 6,0 = 90,0 < 95 (Atlanta cobriu por 11 pontos)
* **Status:** ❌ **MISS**
* **Miss Audit:** `STATISTICAL_VARIANCE / MISSING_CONTEXT`
  * O Atlanta Dream teve uma corrida ofensiva no 2º tempo com aproveitamento atípico em arremessos de quadra, superando a margem de proteção do Liberty.

---

### [2026-09-22] — RODADA DIÁRIA (WNBA & FIBA)

- **Snapshot ID:** `FAS_BASKETBALL_GEMINI_2026-09-22_V2`
- **Cutoff:** 2026-09-22T13:30:00-03:00
- **Contexto da Data:** Penúltima rodada da temporada regular da WNBA (5 jogos noturnos decisivos para seeding). Início da FIBA Intercontinental Cup em Pequim (jogos da madrugada/manhã já encerrados pré-cutoff).
- **Status de Liquidação:** **PARCIALMENTE LIQUIDADO** (Jogos da Costa Oeste das 23:00 em apuração final de súmula)

#### 1. Auditoria de Competições Internacionais (FIBA Intercontinental Cup)
* *Rytas Vilnius 107 × 89 RSSB Tigers* — Encerrado antes do cutoff (04:30 BRT).
* *Boca Juniors 88 × 78 Beijing Royal Fighters* — Encerrado antes do cutoff (08:30 BRT).
* *Decisão:* Conforme seção # 2 e # 3 do manual, jogos encerrados pré-cutoff não recebem pick retroativo para blindar integridade estatística.

#### 2. Grade de Fixtures WNBA e Liquidação

1. **Connecticut Sun 69 @ 79 Washington Mystics**
   - *Resultado Oficial:* 79 × 69 (Total: 148 pontos | Margem: Washington +10)
   - **SAFE:** Washington Mystics -9.5 ➔ ✅ **HIT** (Washington venceu por 10 pontos: 79 - 69 = 10 > 9.5)
   - **SAFE+:** Menos de 164.5 Pontos ➔ ✅ **HIT** (Total 148 pontos <= 164.5)

2. **Minnesota Lynx 77 @ 96 Indiana Fever**
   - *Resultado Oficial:* 96 × 77 (Total: 173 pontos | Margem: Indiana +19)
   - **SAFE:** Mais de 181.5 Pontos ➔ ❌ **MISS** (Total 173 pontos)
     - *Miss Audit:* `LINEUP_CHANGE / STATISTICAL_VARIANCE` (Olivia Miles foi desfalque de última hora no Lynx por lesão na panturrilha; ataque do Lynx caiu para apenas 77 pontos, enquanto Caitlin Clark anotou 27 pts e liderou o Fever).
   - **SAFE+:** Minnesota Lynx +4.5 Spread ➔ ❌ **MISS** (Fever venceu por 19 pontos)
     - *Miss Audit:* `LINEUP_CHANGE`
   - **PRA CIMA:** Mais de 186.5 Pontos ➔ ❌ **MISS** (Total 173 pontos)
     - *Miss Audit:* `LINEUP_CHANGE`

3. **Toronto Tempo 85 @ 97 Chicago Sky**
   - *Resultado Oficial:* 97 × 85
   - **SAFE+:** Chicago Sky Vence - Moneyline ➔ ✅ **HIT** (Chicago Sky venceu por 97x85)

4. **Golden State Valkyries 82 @ 90 Portland Fire** (OT) (23:00 BRT)
   - *Resultado Oficial:* 90 × 82 (78 × 78 no tempo regulamentar; Portland venceu no OT | Total: 172 pontos | Margem: Portland +8)
   - **SAFE:** Golden State Valkyries -8.5 ➔ ❌ **MISS** (Portland venceu 90x82)
     - *Miss Audit:* STATISTICAL_VARIANCE / UPSET (Valkyries abriu 17x0, mas sofreu apagão defensivo na reta final e caiu no OT diante de Portland descompromissado).
   - **SAFE+:** Golden State Vence 1º Tempo ➔ ✅ **HIT** (Valkyries venceu a primeira metade com folga)
   - **PRA CIMA:** Menos de 158.5 Pontos ➔ ❌ **MISS** (Prorrogação inflou placar para 172 pontos)
     - *Miss Audit:* STATISTICAL_VARIANCE

5. **Los Angeles Sparks 79 @ 89 Las Vegas Aces** (23:00 BRT)
   - *Resultado Oficial:* 89 × 79 (Total: 168 pontos | Margem: Las Vegas +10)
   - **SAFE:** Las Vegas Aces -9.5 ➔ ✅ **HIT** (89 - 79 = 10 > 9.5)
   - **SAFE+:** Las Vegas Aces 1º Tempo -6.5 ➔ ✅ **HIT** (Aces abriram vantagem no 1º tempo)
   - **PRA CIMA:** Las Vegas Aces -15.5 Spread ➔ ❌ **MISS** (Margem final travou em 10 pontos)
     - *Miss Audit:* STATISTICAL_VARIANCE

#### 3. Auditoria das Múltiplas / Bilhetes Combinados (Backtest de Bilhetes 22/09)

*   🎟️ **MÚLTIPLA SAFE (WNBA):**
    *   Sun @ Mystics: Mystics -9.5 ➔ ✅ HIT (79x69)
    *   Lynx @ Fever: Over 181.5 ➔ ❌ MISS (173 pts)
    *   Valkyries @ Fire: Valkyries -8.5 ➔ ❌ MISS (82x90)
    *   Sparks @ Aces: Aces -9.5 ➔ ✅ HIT (89x79)
    *   **Resultado da Múltipla SAFE:** ❌ **RED** (2 acertos, 2 erros)

*   🎟️ **MÚLTIPLA SAFE+ (WNBA):**
    *   Sun @ Mystics: Under 164.5 ➔ ✅ HIT (148 pts)
    *   Lynx @ Fever: Lynx +4.5 Spread ➔ ❌ MISS
    *   Tempo @ Sky: Sky ML ➔ ✅ HIT (97x85)
    *   Valkyries @ Fire: Valkyries 1ºT ➔ ✅ HIT
    *   Sparks @ Aces: Aces 1ºT -6.5 ➔ ✅ HIT
    *   **Resultado da Múltipla SAFE+:** ❌ **RED** (4 acertos, 1 erro - derrubada por Lynx +4.5)

*   🎟️ **MÚLTIPLA PRA CIMA (ATTACK):**
    *   Lynx @ Fever: Over 186.5 ➔ ❌ MISS
    *   Valkyries @ Fire: Under 158.5 ➔ ❌ MISS
    *   Sparks @ Aces: Aces -15.5 ➔ ❌ MISS
    *   **Resultado da Múltipla PRA CIMA:** ❌ **RED**

*   🎟️ **MÚLTIPLA APOSENTAR O NETO (Scanner / Alavancagem):**
    *   **Resultado:** ❌ **RED**

---

## 📊 PAINEL ACUMULADO DE BACKTEST (BASQUETE)

### A. Performance por Seleções Individuais (Singles)
| Categoria | Total Registrado | HIT | MISS | VOID | Win Rate (%) |
|---|---|---|---|---|---|
| **SAFE** | 7 | 3 | 4 | 0 | **42.9%** |
| **SAFE+** | 8 | 5 | 3 | 0 | **62.5%** |
| **PRA CIMA** | 6 | 1 | 5 | 0 | **16.7%** |
| **Total Liquidado** | 21 | 9 | 12 | 0 | **42.9%** |

### B. Performance por Múltiplas / Bilhetes Combinados (Parlays)
| Bilhete / Múltipla | Total Disputado | GREEN (HIT) | RED (MISS) | PENDENTE | Taxa de Acerto (%) |
|---|---|---|---|---|---|
| **Bilhete SAFE** | 2 | 0 | 2 | 0 | **0.0%** (2/4 pernas ontem, 1/3 hoje) |
| **Bilhete SAFE+** | 2 | 0 | 2 | 0 | **0.0%** (4/5 pernas ontem, 1/3 hoje) |
| **Bilhete PRA CIMA (ATTACK)** | 2 | 0 | 2 | 0 | **0.0%** (0/3 pernas ontem, 1/3 hoje) |
| **Bilhete APOSENTAR O NETO** | 2 | 0 | 2 | 0 | **0.0%** |

---

### [2026-09-23] - RODADA DIÁRIA (BASQUETE)

- **Snapshot ID:** FAS_BASKETBALL_GEMINI_2026-09-23_V1
- **Data do Registro:** 2026-09-23
- **Horário de Registro:** 01:10:00 BRT
- **Cutoff:** 2026-09-23T01:10:00-03:00
- **Contexto da Data:** Reta final da temporada regular da WNBA (2 confrontos cruciais para fechamento da tabela) e 2ª rodada da fase de grupos da FIBA Intercontinental Cup em Pequim.
- **Status de Liquidação:** **LIQUIDADO / AUDITADO**

#### 1. Discovery e Cobertura
- Encontrados: 4
- Elegíveis: 3
- Analisados: 3
- Descartados: 1 (Shanghai Sharks vs RSSB Tigers – TIER_C / Disparidade técnica sem linhas comerciais auditadas)

#### 2. Grade de Fixtures, Resultados e Liquidação

1. **Beijing Royal Fighters 89 vs 119 NBA G League United** (FIBA Intercontinental Cup - Grupo B - 08:30 BRT)
   - *Resultado Oficial:* 89 × 119 (Total: 208 pontos | Margem: G League +30)
   - **SAFE:** NBA G League United Vence (Moneyline) ➔ ✅ **HIT** (119x89)
   - **SAFE+:** NBA G League United -6.5 Spread ➔ ✅ **HIT** (G League venceu por 30 pontos)
   - **PRA CIMA:** Mais de 168.5 Pontos ➔ ✅ **HIT** (Total 208 pontos > 168.5)
   - *Observação:* Varredura de 100% de acerto nas 3 seleções.

2. **Atlanta Dream 95 @ 84 New York Liberty** (WNBA - 18:00 BRT / 17:00 ET)
   - *Resultado Oficial:* 95 × 84 (Total: 179 pontos | Margem: Atlanta +11)
   - **SAFE:** New York Liberty +4.5 Spread Protegido ➔ ❌ **MISS** (Liberty perdeu por 11 pontos: 84 - 95 = -11)
     - *Miss Audit:* STATISTICAL_VARIANCE / UPSET (Dream garantiu seed 4 nos playoffs com intensidade defensiva e alto aproveitamento perimetral; Liberty rodou titulares na reta final).
   - **SAFE+:** New York Liberty Vence (Moneyline) ➔ ❌ **MISS** (Placar 84x95)
     - *Miss Audit:* STATISTICAL_VARIANCE
   - **PRA CIMA:** Menos de 169.5 Pontos ➔ ❌ **MISS** (Total 179 pontos > 169.5)
     - *Miss Audit:* STATISTICAL_VARIANCE

3. **Dallas Wings 92 @ 70 Seattle Storm** (WNBA - 23:00 BRT / 10:00 PM ET)
   - *Resultado Oficial:* 92 × 70 (Total: 162 pontos | Margem: Dallas +22)
   - **SAFE:** Seattle Storm -5.5 Spread ➔ ❌ **MISS** (Seattle perdeu em casa por 22 pontos)
     - *Miss Audit:* STATISTICAL_VARIANCE / UPSET (Seattle já com seed travada atuou desmobilizado; Dallas abriu vantagem desde os minutos iniciais).
   - **SAFE+:** Seattle Storm Vence 1º Tempo ➔ ❌ **MISS** (Dallas liderou o primeiro tempo)
     - *Miss Audit:* STATISTICAL_VARIANCE
   - **PRA CIMA:** Dallas Wings Team Total Under 79.5 ➔ ❌ **MISS** (Dallas anotou 92 pontos)
     - *Miss Audit:* STATISTICAL_VARIANCE

#### 3. Auditoria das Múltiplas / Bilhetes Combinados (Backtest de Bilhetes 23/09)

*   🎟️ **MÚLTIPLA 1 - SAFE (3 seleções):**
    *   Beijing vs G League: G League United Vence (ML) ➔ ✅ HIT
    *   Atlanta @ New York: New York Liberty +4.5 Spread ➔ ❌ MISS
    *   Dallas @ Seattle: Seattle Storm -5.5 Spread ➔ ❌ MISS
    *   **Resultado da Múltipla SAFE:** ❌ **RED** (1 acerto, 2 erros)

*   🎟️ **MÚLTIPLA 2 - SAFE+ (3 seleções):**
    *   Beijing vs G League: G League United -6.5 Spread ➔ ✅ HIT
    *   Atlanta @ New York: New York Liberty Vence (ML) ➔ ❌ MISS
    *   Dallas @ Seattle: Seattle Storm Vence 1º Tempo ➔ ❌ MISS
    *   **Resultado da Múltipla SAFE+:** ❌ **RED** (1 acerto, 2 erros)

*   🎟️ **MÚLTIPLA 3 - PRA CIMA (Tripla de Ataque):**
    *   Beijing vs G League: Mais de 168.5 Pontos ➔ ✅ HIT
    *   Atlanta @ New York: Menos de 169.5 Pontos ➔ ❌ MISS
    *   Dallas @ Seattle: Dallas Wings Team Total Under 79.5 ➔ ❌ MISS
    *   **Resultado da Múltipla PRA CIMA:** ❌ **RED** (1 acerto, 2 erros)

*   🎟️ **MÚLTIPLA 4 - APOSENTAR O NETO (Basquete Scanner / Cotação Alta):**
    *   **Resultado:** ❌ **RED**

---

### [2026-09-24] — RODADA DIÁRIA (BASQUETE)

- **Snapshot ID:** `FAS_BASKETBALL_GEMINI_2026-09-24_V1`
- **Data do Registro:** 2026-09-24
- **Horário de Registro:** 00:20:00 BRT
- **Cutoff:** 2026-09-24T00:20:00-03:00
- **Contexto da Data:** Reta decisiva da fase de grupos da FIBA Intercontinental Cup em Pequim e encerramento da temporada regular da WNBA com definição das últimas vagas de playoffs.
- **Status de Liquidação:** **PARCIALMENTE AUDITADO / EM FINALIZAÇÃO**

#### 1. Discovery e Cobertura
- Encontrados: 5
- Elegíveis: 3
- Analisados: 3
- Descartados: 2 (Jogos amistosos europeus de pré-temporada sem liquidez)

#### 2. Grade de Fixtures, Resultados e Liquidação

1. **Boca Juniors 74 × 79 NBA G League United** (FIBA Intercontinental Cup - 08:30 BRT)
   - *Resultado Oficial:* 74 × 79 (Total: 153 pontos | Margem: G League +5)
   - **SAFE:** NBA G League United Vence (Moneyline) ➔ ✅ **HIT** (G League venceu por 79x74)
   - **SAFE+:** NBA G League United -7.5 Spread ➔ ❌ **MISS** (Venceu por 5 pontos; faltou cobrir o handicap)
     - *Miss Audit:* `STATISTICAL_VARIANCE` (Boca desacelerou o ritmo de jogo no 4º quarto com posses longas e evitou a dilatação do placar).
   - **PRA CIMA:** NBA G League United Team Total Over 89.5 Pontos ➔ ❌ **MISS** (G League anotou 79 pontos)
     - *Miss Audit:* `STATISTICAL_VARIANCE`

2. **Indiana Fever 66 @ 86 Minnesota Lynx** (WNBA - 21:00 BRT / 8:00 PM ET)
   - *Resultado Oficial:* 66 × 86 (Total: 152 pontos | Margem: Lynx +20)
   - **SAFE:** Mais de 166.5 Pontos ➔ ❌ **MISS** (Total 152 pontos < 166.5)
     - *Miss Audit:* `STATISTICAL_VARIANCE` (Defesa sufocante do Lynx no Target Center segurou o Fever em apenas 66 pontos).
   - **SAFE+:** Minnesota Lynx Vence (Moneyline) ➔ ✅ **HIT** (Lynx venceu com folga 86x66)
   - **PRA CIMA:** Indiana Fever +5.5 Spread + Mais de 168.5 Pontos ➔ ❌ **MISS**
     - *Miss Audit:* `STATISTICAL_VARIANCE`

3. **Golden State Valkyries 76 @ 75 Los Angeles Sparks** (WNBA - 20:00 BRT / 7:00 PM ET)
   - *Resultado Oficial:* 76 × 75 (Total: 151 pontos | Margem: Valkyries +1)
   - **SAFE:** Golden State Valkyries Vence (Moneyline) ➔ ✅ **HIT** (Valkyries venceu por 76x75 na Crypto.com Arena)
   - **SAFE+:** Golden State Valkyries -4.5 Spread ➔ ❌ **MISS** (Venceu por 1 ponto, não cobrindo o spread)
     - *Miss Audit:* `STATISTICAL_VARIANCE` (Sparks encostou com duas bolas de 3 nos minutos finais).
   - **PRA CIMA:** Sparks Team Total Under 78.5 ➔ ✅ **HIT** (Sparks marcou 75 pontos <= 78.5)

#### 3. 👴 APOSENTAR O NETO — Principais Linhas (Scanner Completo)

**Boca Juniors vs NBA G League United**
- 🔥🔥🔥 G League United Vence (ML) — 95 ➔ ✅ HIT
- 🔥🔥 G League United -7.5 Spread — 88 ➔ ❌ MISS
- 🔥 G League United Team Total Over 89.5 — 84 ➔ ❌ MISS
- 🔥 Mais de 168.5 Pontos — 82 ➔ ❌ MISS
- 🟢 Boca Juniors Under 82.5 — 79 ➔ ✅ HIT

**Indiana Fever @ Minnesota Lynx**
- 🔥🔥🔥 Mais de 166.5 Pontos — 91 ➔ ❌ MISS
- 🔥🔥 Minnesota Lynx Vence (ML) — 85 ➔ ✅ HIT
- 🔥 Indiana Fever +5.5 Spread — 83 ➔ ❌ MISS
- 🔥 Mais de 168.5 Pontos — 82 ➔ ❌ MISS
- 🟢 Indiana Fever Team Total Over 81.5 — 78 ➔ ❌ MISS

**Golden State Valkyries @ Los Angeles Sparks**
- 🔥🔥🔥 Valkyries Vence (ML) — 93 ➔ ✅ HIT
- 🔥🔥 Valkyries -4.5 Spread — 86 ➔ ❌ MISS
- 🔥 Sparks Team Total Under 78.5 — 81 ➔ ✅ HIT
- 🟢 Menos de 164.5 Pontos — 78 ➔ ✅ HIT (151 pts)

#### 4. Bilhetes Combinados / Múltiplas do Dia (Backtest 24/09)

*   🎟️ **MÚLTIPLA 1 — SAFE (Formato Modular com Stop Points):**
    *   🥇 **#1 [ÂNCORA PRIMÁRIA]:** Boca vs G League: G League United Vence (ML) ➔ ✅ **HIT** (79x74)
    *   🥈 **#2 [ÂNCORA SECUNDÁRIA]:** Valkyries @ Sparks: Golden State Valkyries Vence (ML) ➔ ✅ **HIT** (76x75)
    *   🟢 **STOP POINT 1 ➔ DUPLA ÂNCORA (Top 1 + Top 2):** ✅ **GREEN / HIT (2/2)** 🎯🎯
    *   🥉 **#3 [EXPANSÃO TRIPLA]:** Fever @ Lynx: Mais de 166.5 Pontos ➔ ❌ MISS (152 pts)
    *   🟡 **STOP POINT 2 ➔ TRIPLA EQUILIBRADA:** ❌ **RED** (derrubada pelo Under do Lynx)
    *   **Resultado da Múltipla SAFE:** **GREEN no Stop Point 1 (Dupla Âncora)** | RED na expansão tripla.

*   🎟️ **MÚLTIPLA 2 — SAFE+ (Formato Modular):**
    *   🥇 #1 G League United -7.5 Spread ➔ ❌ MISS (venceu por 5)
    *   🥈 #2 Golden State Valkyries -4.5 Spread ➔ ❌ MISS (venceu por 1)
    *   🥉 #3 Minnesota Lynx Vence (ML) ➔ ✅ HIT (86x66)
    *   **Resultado da Múltipla SAFE+:** ❌ **RED**

*   🎟️ **MÚLTIPLA 3 — PRA CIMA (Tripla de Valor):**
    *   G League United Team Total Over 89.5 Pontos ➔ ❌ MISS
    *   Fever @ Lynx: Fever +5.5 + Over 168.5 Pontos ➔ ❌ MISS
    *   Sparks Team Total Under 78.5 Pontos ➔ ✅ HIT
    *   **Resultado:** ❌ **RED**

*   🎟️ **MÚLTIPLA 4 — APOSENTAR O NETO (Alavancagem Máxima da Rodada):**
    *   G League -7.5 + Valkyries -4.5 + Lynx ML + Fever Over 168.5 + Sparks Under 78.5.
    *   **Resultado:** ❌ **RED**

#### 4. ⏰ Protocolo de Lembrete T-60min
*   **Primeiro Jogo FIBA:** Boca vs G League (08:30 BRT) ➔ Lembrete às **07:30 BRT**
*   **Primeiro Jogo WNBA:** Valkyries @ Sparks (20:00 BRT) ➔ Lembrete às **19:00 BRT**
*   **Checklist:** Injury reports oficiais e confirmação de minutos dos titulares.

---

### [2026-09-25] — RODADA DIÁRIA (BASQUETE V2.0 BLINDADO)

- **Snapshot ID:** `FAS_BASKETBALL_GEMINI_2026-09-25_V1`
- **Data do Registro:** 2026-09-25
- **Horário de Registro:** 00:52:00 BRT
- **Cutoff:** 2026-09-25T13:00:00-03:00
- **Contexto da Data:** Abertura da temporada 2026/27 da EuroLeague Basketball (Rodada 1). Dia de descanso na FIBA Intercontinental Cup e entressafra de playoffs da WNBA.
- **Protocolo de Blindagem Ativo:** **SAFE Quality Gates V2.0** (Veto a Spreads Negativos em SAFE, Veto a Linhas Cheias de Over, Foco em Moneyline de Favorito e Handicap Positivo Protegido).
- **Status de Liquidação:** **LIQUIDADO / AUDITADO (100% GREEN NA SAFE V2.0)**

#### 1. Discovery e Cobertura
- Encontrados: 4
- Elegíveis: 3
- Analisados: 3 (Fenerbahçe x Virtus Bologna, Partizan x Olimpia Milano, Beşiktaş x Valencia Basket)
- Descartados: 1 (Brisbane Bullets x Illawarra Hawks na NBL — jogo das 06:30 BRT matutino de alta volatilidade)

#### 2. Grade de Fixtures, Resultados e Liquidação (V2.0)

1. **Beşiktaş J.K. 94 × 96 Valencia Basket** (EuroLeague - Rodada 1 - 14:00 BRT)
   - *Resultado Oficial:* 94 × 96 (Total: 190 pontos | Margem: Valencia +2)
   - **SAFE:** Valencia Basket +5.5 Spread Positivo Protegido ➔ ✅ **HIT** (Valencia venceu o confronto direto por 96x94 em Istambul)
   - **SAFE+:** Valencia Basket Vence (Moneyline) ➔ ✅ **HIT** (Valencia venceu por 96x94)
   - **PRA CIMA:** Menos de 162.5 Pontos ➔ ❌ **MISS** (Total 190 pontos)
     - *Miss Audit:* `STATISTICAL_VARIANCE` (Jogo acelerado com 27 bolas de 3 convertidas somadas).

2. **Fenerbahçe SK 78 × 68 Virtus Segafredo Bologna** (EuroLeague - Rodada 1 - 14:45 BRT)
   - *Resultado Oficial:* 78 × 68 (Total: 146 pontos | Margem: Fenerbahçe +10)
   - **SAFE:** Fenerbahçe Vence (Moneyline) ➔ ✅ **HIT** (Fenerbahçe dominou o 2º tempo e venceu por 10 pontos)
   - **SAFE+:** Fenerbahçe Vence o 1º Tempo ➔ ✅ **HIT** (Fenerbahçe liderou na primeira metade)
   - **PRA CIMA:** Fenerbahçe -7.5 Spread ➔ ✅ **HIT** (78 - 68 = 10 > 7.5)

3. **KK Partizan NIS 92 × 76 Olimpia Milano** (EuroLeague - Rodada 1 - 15:45 BRT)
   - *Resultado Oficial:* 92 × 76 (Total: 168 pontos | Margem: Partizan +16)
   - **SAFE:** Partizan NIS +4.5 Spread Positivo Protegido ➔ ✅ **HIT** (Partizan venceu direto por 16 pontos de vantagem!)
   - **SAFE+:** Partizan NIS Vence (Moneyline) ➔ ✅ **HIT** (Partizan venceu por 92x76 no caldeirão de Belgrado)
   - **PRA CIMA:** Partizan NIS Vence o 1º Tempo ➔ ✅ **HIT** (Partizan construiu ampla vantagem logo no 1ºT)

#### 3. 👴 APOSENTAR O NETO — Principais Linhas (Scanner Completo)

**Fenerbahçe vs Virtus Bologna**
- Fenerbahçe Vence (ML) — 97 ➔ ✅ HIT (78x68)
- Fenerbahçe Vence 1º Tempo — 91 ➔ ✅ HIT
- Fenerbahçe -7.5 Spread — 84 ➔ ✅ HIT
- Mais de 158.5 Pontos — 80 ➔ ❌ MISS (146 pts)
- Virtus Bologna Under 76.5 — 82 ➔ ✅ HIT (68 pts)

**KK Partizan vs Olimpia Milano**
- Partizan +4.5 Spread — 93 ➔ ✅ HIT (92x76)
- Partizan Vence (ML) — 87 ➔ ✅ HIT (92x76)
- Partizan Vence 1º Tempo — 82 ➔ ✅ HIT
- Menos de 164.5 Pontos — 79 ➔ ❌ MISS (168 pts)
- Milano Under 80.5 — 81 ➔ ✅ HIT (76 pts)

**Beşiktaş vs Valencia Basket**
- Valencia Basket +5.5 Spread — 91 ➔ ✅ HIT (96x94)
- Valencia Basket Vence (ML) — 84 ➔ ✅ HIT (96x94)
- Menos de 162.5 Pontos — 80 ➔ ❌ MISS (190 pts)
- Beşiktaş Under 81.5 — 78 ➔ ❌ MISS (94 pts)

#### 4. Auditoria das Múltiplas / Bilhetes Combinados (Arquitetura Modular Rankeada V2.0)

*   🎟️ **MÚLTIPLA 1 — SAFE (Formato Modular com Stop Points) [BOLETIM OFICIAL PINNACLE]:**
    *   🥇 **#1 [ÂNCORA PRIMÁRIA]:** Fenerbahçe Vence (Moneyline) ➔ ✅ **HIT** (78x68) — Odd @1.10
    *   🥈 **#2 [ÂNCORA SECUNDÁRIA]:** Partizan NIS +4.5 Spread Positivo ➔ ✅ **HIT** (92x76) — Odd @1.28
    *   🟢 **STOP POINT 1 ➔ DUPLA ÂNCORA (Top 1 + Top 2):** ✅ **GREEN TOTAL (2/2)** 🎯🎯 *(Odd real batida: **@1.41**)*.
    *   🥉 **#3 [EXPANSÃO TRIPLA]:** Valencia Basket +5.5 Spread Positivo ➔ ✅ **HIT** (96x94) — Odd @1.50
    *   🟡 **STOP POINT 2 ➔ TRIPLA EQUILIBRADA (Top 1 + Top 2 + Top 3):** ✅ **GREEN ESPETACULAR (3/3 - 100% DE APROVEITAMENTO)!** 🎯🎯🎯 *(Odd real batida: **@2.12**)*.
    *   **Resultado da Múltipla SAFE:** ✅ **GREEN TOTAL EM TODOS OS STOP POINTS!** A blindagem V2.0 funcionou com perfeição cirúrgica.

*   🎟️ **MÚLTIPLA 2 — SAFE+ (Moneyline / Secas):**
    *   🥇 #1 Fenerbahçe Vence 1º Tempo ➔ ✅ HIT
    *   🥈 #2 Partizan NIS Vence (ML) ➔ ✅ HIT (92x76)
    *   🟢 **STOP POINT 1 ➔ Dupla SAFE+:** ✅ **GREEN (2/2)** 🎯
    *   🥉 #3 Valencia Basket Vence (ML) ➔ ✅ HIT (96x94)
    *   🟡 **STOP POINT 2 ➔ Tripla SAFE+:** ✅ **GREEN MONSTRUOSO (3/3)!** 🎯🎯🎯

*   🎟️ **MÚLTIPLA 3 — PRA CIMA (Tripla de Alta Assimetria):**
    *   Fenerbahçe -7.5 Spread (✅) + Partizan 1ºT ML (✅) + Beşiktaş/Valencia Under 162.5 (❌).
    *   **Resultado:** ❌ **RED** (2 acertos, 1 erro — derrubada pelo Over inesperado na Turquia).

#### 5. ⏰ Auditoria do Protocolo T-60min
*   **Jogos da EuroLeague (14:00, 14:45, 15:45 BRT):** Escalações e injury reports confirmados no prazo. Larkin liderou Fener, Carlik Jones orquestrou o Partizan e Valencia rodou 10 jogadores com intensidade.

#### 6. 📊 Conclusão da Blindagem V2.0 no Basquete
*   **Taxa de Acerto nas Linhas SAFE:** **3/3 (100%)**
*   **Bilhete Dupla Âncora (@1.41):** ✅ **GREEN**
*   **Bilhete Tripla Equilibrada (@2.12):** ✅ **GREEN**
*   **Bilhete Tripla SAFE+:** ✅ **GREEN**
*   *A proibição de spreads negativos e a priorização de handicaps positivos na EuroLeague provou ser a melhor salvaguarda contra zebras.*

---

### [2026-10-14] — RODADA DIÁRIA (NBA PRESEASON — VALIDAÇÃO TEAM TOTAL V2.5)

- **Snapshot ID:** `FAS_BASKETBALL_2026-10-14_V1`
- **Data do Registro:** 2026-10-14
- **Horário de Registro:** 20:15:00 BRT
- **Cutoff:** 2026-10-14T20:30:00-03:00
- **Contexto da Data:** Super rodada da NBA Preseason com 5 jogos na grade (Hornets @ Celtics, Nets @ Heat, Bulls @ Bucks, Suns @ Spurs, Nuggets @ Clippers). 
- **Inovação Metodológica Testada em Produção:** Regra **Team Total First** na Melbet após constatação de corte de catálogo em Game Totals (rebaixamento de linhas no Total 1 e Total 2).
- **Status de Liquidação:** **LIQUIDADO / AUDITADO (100% GREEN NO TURNO 1)**

#### 1. Discovery e Cobertura
- Encontrados: 5
- Elegíveis: 4 (Hornets @ Celtics, Nets @ Heat, Suns @ Spurs, Nuggets @ Clippers)
- Descartados / Vetados na SAFE: 1 (Bulls @ Bucks — vetado devido ao risco de rotação profunda de pré-temporada; decisão acertadíssima, pois os Bucks perderam por 104x125).

#### 2. Grade de Fixtures, Resultados e Liquidação

1. **Charlotte Hornets 93 × 114 Boston Celtics** (TD Garden - 20:30 BRT)
   - *Resultado Oficial:* 93 × 114 (Total: 207 pontos | Celtics: 114 pontos)
   - **SAFE (Original):** Boston Celtics Acima de 111.5 Pontos (@1.33) ➔ ✅ **HIT** (Celtics marcou 114)
   - **SAFE (Melbet V2.5 - Total 2):** Boston Celtics Acima de 108.5 Pontos (@1.33) ➔ ✅ **HIT** (Celtics marcou 114 com 5.5 pontos de folga!)

2. **Brooklyn Nets 128 × 144 Miami Heat** (Kaseya Center - 20:30 BRT)
   - *Resultado Oficial:* 128 × 144 (Total: 272 pontos | Heat: 144 pontos)
   - **SAFE (Original Game Total):** Mais de 223.5 Pontos Totais (@1.36) ➔ ✅ **HIT** (272 pontos totais!)
   - **SAFE (Melbet V2.5 - Total 2):** Miami Heat Acima de 112.5 Pontos (@1.375) ➔ ✅ **HIT** (Heat pulverizou a linha marcando 144 pontos!)
   - **SAFE+ / Dupla Chance:** Miami Heat 1X no tempo normal (@1.39) ➔ ✅ **HIT** (Heat venceu por 144x128)

3. **Phoenix Suns 103 × 123 San Antonio Spurs** (Frost Bank Center - 21:00 BRT)
   - *Resultado Oficial:* 103 × 123 (Total: 226 pontos | Spurs: 123 pontos)
   - **SAFE (Original):** San Antonio Spurs Acima de 109.5 Pontos (@1.35) ➔ ✅ **HIT** (Spurs marcou 123 pontos!)
   - **SAFE (Melbet V2.5):** San Antonio Spurs Vence - V1 (@1.26) ➔ ✅ **HIT** (Spurs venceu com folga por 20 pontos de vantagem)

4. **Chicago Bulls 125 × 104 Milwaukee Bucks** (Fiserv Forum - 21:00 BRT)
   - *Auditoria de Veto:* Vetado da tripla de confiança devido ao risco de poupança dos titulares dos Bucks. Bulls venceu por 125x104 confirmando o acerto cirúrgico do filtro de proteção.

#### 3. Auditoria dos Bilhetes / Turnos do Basquete

*   🎟️ **TURNO 1 — PRIME TIME (Celtics + Heat + Spurs):**
    *   Hornets @ Celtics: Celtics Over 108.5 / 111.5 (@1.33) ➔ ✅ **HIT** (114 pts)
    *   Nets @ Heat: Heat Over 112.5 (@1.375) / 1X (@1.39) ➔ ✅ **HIT** (144 pts)
    *   Suns @ Spurs: Spurs Vence V1 (@1.26) / Over 109.5 (@1.35) ➔ ✅ **HIT** (123 pts)
    *   **Resultado do Turno 1:** ✅ **GREEN TOTAL ABSOLUTO!** Multiplicador de **@2.30 a @2.50** liquidado e colocado no bolso antes de dormir! 🎯🎯🎯

*   🎟️ **DUPLA ÂNCORA BLINDADA (Stop Point 1):**
    *   Celtics Over 108.5 (@1.33) + Heat Over 112.5 (@1.375) ➔ ✅ **GREEN TOTAL (@1.83)!** 🎯🎯

---

### [2026-10-15] — RODADA DIÁRIA (EUROLEAGUE & NBA PRESEASON)

- **Snapshot ID:** `FAS_MULTI_SPORT_2026-10-15_V1`
- **Data do Registro:** 2026-10-15
- **Cutoff:** 2026-10-15T14:45:00-03:00
- **Contexto da Data:** Rodada com EuroLeague de alto nível (Real Madrid, Fenerbahçe, Valencia) e sequência da NBA Preseason (Knicks, Pistons, Mavericks).
- **Status de Liquidação:** **LIQUIDADO / AUDITADO (100% GREEN NA EUROLEAGUE & SOROS BASQUETE DIA 2 GREEN)**

#### 1. Discovery e Cobertura
- Analisados: 6 fixtures (3 EuroLeague + 3 NBA Preseason)
- Elegíveis: 6

#### 2. Grade de Fixtures, Resultados e Liquidação

1. **Real Madrid 111 × 92 LDLC ASVEL** (WiZink Center - 15:45 BRT)
   - *Resultado Oficial:* 111 × 92 (Total: 203 pontos | Real Madrid: 111 pontos)
   - **SAFE (Original Team Total):** Real Madrid Acima de 84.5 Pontos (@1.32) ➔ ✅ **HIT** (Real marcou 111 com 26.5 pts de folga!)
   - **SAFE+:** Real Madrid -10.5 Handicap (@1.78) ➔ ✅ **HIT** (Venceu por 19 pontos: 111 - 92 = 19 > 10.5)
   - **ATTACK:** Real Madrid Acima de 92.5 Pontos (@1.66) ➔ ✅ **HIT** (111 pontos!)

2. **Fenerbahçe 74 × 65 Partizan Belgrade** (Ülker Sports Arena - 14:45 BRT)
   - *Resultado Oficial:* 74 × 65 (Margem: Fenerbahçe +9 | Recorde de 14 tocos)
   - **SAFE:** Fenerbahçe Vence - Moneyline (@1.28) ➔ ✅ **HIT** (74x65)

3. **Valencia Basket 88 × 91 Maccabi Tel Aviv** (Roig Arena - 15:30 BRT)
   - *Resultado Oficial:* 88 × 91 (Margem: Maccabi +3)
   - **SAFE (Spread Positivo Protegido):** Valencia Basket +5.5 Handicap (@1.30) ➔ ✅ **HIT** (88 + 5.5 = 93.5 > 91)

4. **Toronto Raptors 120 @ 122 New York Knicks** (Madison Square Garden - 20:30 BRT)
   - *Resultado Oficial:* 120 × 122 (Total: 242 pontos | Knicks: 122 pontos)
   - **SAFE (Sniper Soros Basquete):** New York Knicks Acima de 109.5 Pontos (@1.33) ➔ ✅ **HIT** (122 pontos!)
   - **SAFE+:** New York Knicks -6.5 Handicap (@1.82) ➔ ❌ **MISS** (Knicks venceu por apenas 2 pontos: 122 - 120 = 2 < 6.5)
     - *Miss Audit:* `STATISTICAL_VARIANCE` (Raptors reagiu no 4º quarto com 41 pontos contra os reservas dos Knicks).
   - **ATTACK:** Knicks Vence + Mais de 220.5 Pontos (@2.60) ➔ ✅ **HIT** (122x120 e 242 pts totais!)

5. **Minnesota Timberwolves 106 @ 128 Detroit Pistons** (Target Center - 20:00 BRT)
   - *Resultado Oficial:* 106 × 128 (Margem: Pistons +22)
   - **SAFE:** Minnesota Timberwolves +6.5 Handicap (@1.35) ➔ ❌ **MISS** (Pistons dominaram amplamente com 128x106)
     - *Miss Audit:* `MISSING_CONTEXT / LINEUP_CHANGE` (Wolves rodou banca profunda e Pistons jogaram em ritmo elevado de transição).

6. **New Orleans Pelicans 101 @ 97 Dallas Mavericks** (American Airlines Center - 21:30 BRT)
   - *Resultado Oficial:* 101 × 97 (Mavericks: 97 pontos)
   - **SAFE:** Dallas Mavericks Acima de 108.5 Pontos (@1.35) ➔ ❌ **MISS** (Mavericks travou em 97 pontos)
     - *Miss Audit:* `LINEUP_CHANGE` (Dallas poupou Kyrie Irving e Cooper Flagg; rotação mista sofreu no aproveitamento de perímetro).
   - **ATTACK:** Mavericks Vence + Mais de 218.5 Pontos (@2.45) ➔ ❌ **MISS** (Pelicans 101x97)

#### 3. Auditoria dos Bilhetes de Basquete

*   🥪 **TURNO 1 — TARDE / EUROLEAGUE (@2.20):**
    *   Real Madrid Over 84.5 (@1.32) + Fener ML (@1.28) + Valencia +5.5 (@1.30)
    *   **Resultado:** ✅ **GREEN TOTAL HISTÓRICO NA EUROLEAGUE (3/3 @2.20)!** 🎯🎯🎯

*   🎟️ **DUPLA ÂNCORA TEAM TOTAL (Stop Point 1 @1.76):**
    *   Real Madrid Over 84.5 (@1.32) + Knicks Over 109.5 (@1.33)
    *   **Resultado:** ✅ **GREEN TOTAL (@1.76)!** 🎯🎯

*   🔥 **DESAFIO SOROS BASQUETE — DIA 2 (SNIPER):**
    *   **Entrada:** R$ 13,30
    *   **Seleção:** Raptors @ Knicks ➔ New York Knicks Acima de 109.5 Pontos (@1.33)
    *   **Resultado:** ✅ **GREEN TOTAL (Knicks 122 pts)!**
    *   **Retorno:** R$ 17,69. Avança consagrado para o **DIA 3 DE 30** com **R$ 17,69**!




