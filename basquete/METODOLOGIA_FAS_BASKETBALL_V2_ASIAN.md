# FAS BASKETBALL V2.0 — METODOLOGIA ASIAN & ELASTIC ENGINE (MELBET / PINNACLE)

Documento oficial de diretrizes, regras matemáticas e arquitetura de gestão de risco do **Basketball Analysis System (FAS Basketball V2.0)**.

---

## 🎯 1. ORIGEM E DIAGNÓSTICO DE EVOLUÇÃO (V1.0 ➔ V2.0)

A auditoria forense do banco de dados histórico (`basquete/FAS_BASKETBALL_BACKTEST_DATABASE.md`) identificou os 3 maiores fatores de variância e prejuízo no modelo tradicional de basquete:
1. **O Efeito "Garbage Time" no 4º Quarto:** Favoritos que abrem 15 a 20 pontos de vantagem colocam os reservas em quadra a 4 minutos do fim. O azarão faz uma corrida de 10-12 pontos e invalida handicaps esticados como `-7.5` ou `-9.5`.
2. **Fragilidade das Linhas Principais de Pontos:** Apostar na linha mediana da casa (ex: 228.5) causava Reds frequentes por apenas 1 ou 2 arremessos livres no estouro do cronômetro.
3. **Zebras em Vitórias Simples (Moneyline):** Apostar seco em favoritos fora de casa sem proteção em dias de aproveitamento anômalo de 3 pontos do adversário.

---

## 🛡️ 2. OS 5 PILARES DA METODOLOGIA V2.0

### Pilar 1: Spreads Positivos Elásticos (+8.5 a +14.5)
- Em confrontos equilibrados ou com favoritismo do mandante, buscar o **Spread Positivo Elástico** do time visitante estruturado (ex: de `+4.5` para `+8.5` ou `+10.5` na linha asiática da Melbet/Pinnacle).
- Para favoritos absolutos em casa (ex: Lakers, Celtics, OKC): **nunca pegar o handicap oficial esticado (-14.5)**. Reduzir a linha para um **Spread Curto de Segurança (-3.5 a -5.5)**, bastando uma vitória de 2 a 3 posses de bola.

### Pilar 2: Colchão de Segurança de 10 a 14 Pontos em Totais
- **Proibido apostar na linha principal de Over/Under.**
- Se a modelagem aponta tendência de pontuação alta (Over 226): compra-se a **linha alternativa elástica em Over 214.5 ou 216.5** (@1.28 a @1.38).
- Cria-se uma folga matemática de 10 a 12 pontos para absorver minutos com baixa eficiência ofensiva.

### Pilar 3: Contexto de Torneio (Emirates NBA Cup)
- Em jogos de Copa da NBA, o saldo de pontos (*point differential*) é critério de desempate direto na fase de grupos.
- Os times competem com intensidade até os segundos finais, blindando as apostas contra relaxamento prematuro.

### Pilar 4: Arquitetura Modular em Turnos (Stop Points)
- **Turno 1 (Costa Leste — 20:30 a 22:00 BRT):** Permite fechar um subtotal de odd @1.80 a @2.00.
- **Turno 2 (Costa Oeste — 23:00 a 00:30 BRT):** Jogos noturnos para decisão posterior; cashout e lucro não são garantidos.

### Pilar 5: Desafio Soros Basquete (30 Dias / reserva planejada; risco permanece)
- Stake inicial única de R$ 10,00.
- Odds controladas entre `@1.30` e `@1.45` em seleções de confiança máxima (duplas de mandantes fortes ou spreads estendidos).
- **Regra de Blindagem do Cofre:**
  - **Dia 5:** retirada planejada de até **R$ 10,00**, apenas se o saldo disponível permitir; isso não elimina o risco das entradas restantes.
  - **Dia 7:** retirada planejada de até **R$ 20,00**, somente se houver saldo disponível e execução confirmada.
  - Do Dia 8 ao Dia 30: o plano pretende limitar o capital exposto ao lucro acumulado, mas o risco não é zero e depende do saldo e das retiradas confirmadas.

---

## 📊 3. CATÁLOGO DE BILHETES E GESTÃO DE BANCA

1. ⭐ **Bilhete Supremo NBA (Odd @1.90 a @2.20):** Tripla de elite blindada com foco no principal retorno da noite.
2. 🛡️ **Múltipla 1 — SAFE NBA (Odd @2.80 a @3.50):** 4 seleções em 2 turnos com Stop Points.
3. 🎯 **Desafio Soros NBA (Odd @1.30 a @1.45):** 1 entrada diária de alavancagem calculada.
4. ⚡ **Múltipla 2 — Super Ataque (Odd @4.00 a @5.50):** Spreads de valor e trocação acelerada.
5. 🎲 **Múltipla 5 — O Bingo da Rodada (Round Sweep):** Cobertura integral Moneyline dos jogos da noite com stake simbólica.
