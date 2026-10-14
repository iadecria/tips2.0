# FAS ELITE DASHBOARD — PROMPT MESTRE PARA O V0.DEV (PROMPT MASTER PLAN)

> **Instruções de Uso no v0:** Copie o texto abaixo e cole diretamente na caixa de criação do **v0.dev** para gerar o frontend completo da sua plataforma de tips e análise esportiva.

---

```markdown
Crie uma aplicação web moderna, responsiva e profissional chamada "FAS Elite — Sports Analytics & Ticket Engine" (Futebol & Basquete), inspirada nos dashboards analíticos da Bloomberg e plataformas de trading esportivo de alto padrão.

### 🎨 DESIGN SYSTEM & ESTÉTICA
- Tema escuro padrão (Dark Mode nativo esportivo: background slate-950, cards slate-900/slate-850 com bordas sutis slate-800, textos claros com hierarquia nítida).
- Destaques em cores semânticas vibrantes:
  - 🟢 GREEN / Lucro: Emerald-500 / Emerald-400
  - 🔴 RED / Perda: Rose-500
  - 🟡 PENDING / Em Aberto: Amber-400
  - 🔵 SAFE / Destaque: Indigo-400 / Sky-400
  - 🟣 SUPREMO / Ouro: Violet-400 / Amber-300
- Fontes modernas (Inter ou Outfit), micro-interações suaves, badges de odds estilizados e botões de cópia rápida de boletim.

---

### 📱 ESTRUTURA E MÓDULOS PRINCIPAIS

#### 1. Header & Controles Globais
- Logo "FAS ELITE" com badge de versão "V5.0 Multi-Sport".
- Seletor de Esporte (Toggle Tabs): [ ⚽ Futebol ] | [ 🏀 Basquete (NBA / FIBA) ].
- Seletor de Data com calendário e badges de status da rodada (ex: "Champions League — 14/10" ou "NBA Preseason").
- Resumo do Dia no topo: Total de Bilhetes Ativos, ROI Projetado, e Status da Banca.

#### 2. Central de Bilhetes — Seção Principal
Crie abas ou grids para os bilhetes oficiais:

* ⭐ **CARD DE DESTAQUE: BILHETE SUPREMO (O FILÉ DO DIA / DA NOITE)**
  - O bilhete principal da tela, com borda dourada/violeta brilhante.
  - Seletor de visualização interno com 3 botões/tabs:
    - [ Global (Todas as Melhores) ]
    - [ 🥪 Turno 1 (Ex: 13:45 BRT - Almoço) ]
    - [ 🌆 Turno 2 (Ex: 16:00 BRT - Tarde/Noite) ]
  - Exibe a lista de seleções com: Horário, Jogo, Competição, Mercado, Odd individual e Badge de Status (Pendente / Green / Red).
  - Multiplicador total acumulado com cálculo automático de retorno potencial para R$ 50 e R$ 100.
  - Botão "Copiar Bilhete Formatado para WhatsApp/Telegram".

* 🥇 **TIER 1 — MÚLTIPLA 1: SAFE (Carro-Chefe)**
  - Card interativo com abas de **STOP POINTS**:
    - **Stop Point 1 (Âncora Máxima — Odd 1.70 a 1.85)**
    - **Stop Point 2 (Blindagem — Odd 2.00 a 2.20)**
    - **Stop Point 3 (Completa — Odd 2.50+)**
  - O usuário clica no Stop Point desejado e a lista de jogos/cotação atualiza instantaneamente.

* 🥈 **TIER 2 & 3 — CARDS SECUNDÁRIOS EM GRID:**
  - **Múltipla 2: SAFE+** (Odd 2.50 a 3.50 — Alavancagem balanceada).
  - **Múltipla 3: SUPER ATAQUE** (Odd 6.00 a 12.00 — Retorno agressivo).
  - **Múltipla 4: APOSENTAR O NETO** (Odd 50.00+ — Bingão recreativo).

#### 3. Módulo Exclusivo: DESAFIO SOROS 30 DIAS
- Barra de Progresso visual interativa (Dia 1 a 30) mostrando a trajetória da banca.
- Card com o dia atual:
  - Entrada do Dia (Stake em R$).
  - Odd da Entrada (Espelho do Stop Point 1).
  - Retorno Esperado.
  - Próximo Alvo.
- Histórico em formato de timeline com status de cada dia anterior (GREEN / RED) e o motivo da liquidação.

#### 4. Módulo de Conferência & Liquidação (CONFERE / AUDITORIA)
- Painel colapsável ou aba dedicada onde o usuário pode:
  - Ver os resultados finais de cada partida da rodada.
  - Clicar em "Liquidar Rodada" para ver quais pernas deram Green ou Red automaticamente.
  - Campo de texto para importar/colar o JSON do dia (`bilhetes_ativos.json`) ou exportar o relatório auditado em Markdown.

---

### 📦 MOCK DATA INICIAL (JSON EMBUTIDO PARA DEMONSTRAÇÃO)
Deixe o dashboard já carregado com os dados reais da Champions League de 14/10/2026:
- **Bilhete Supremo Global:** 7 jogos (@3.67).
- **Bilhete Supremo Turno 1 (13:45):** LASK x Liverpool (Over 1.5) + Feyenoord x Como (Over 1.5) = @1.46.
- **Bilhete Supremo Turno 2 (16:00):** Aston Villa 1X + Real Madrid X2 + City x PSG Over 1.5 + Bodø/Dortmund Over 1.5 + Stuttgart Over 0.5 = @2.51.
- **Múltipla 1 SAFE:** Stop Points 1 (@1.81), 2 (@2.14) e 3 (@2.52).
- **Desafio Soros:** Dia 1 (R$ 10,00 @1.81).
- **Dados do Basquete (NBA):** Indiana Pacers +8.5 / Over 105.5 pts, Warriors x Lakers Over 218.5 pts.

Construa com componentes Tailwind limpos, Shadcn UI (Tabs, Dialog, Card, Badge, Progress, Button, Tooltip) e layout responsivo mobile-first.
```
