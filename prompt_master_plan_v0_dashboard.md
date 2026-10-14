# FAS ELITE — PROMPT MASTER PLAN EXECUTIVO PARA O V0.DEV

> **Como usar no v0:** Copie todo o conteúdo abaixo e cole no chat do seu projeto no **[v0.dev](https://v0.dev)**. Ele vai instruir a IA a estruturar o sistema completo, com sincronização em tempo real, gráficos, relatórios e a nova Escada Oficial de Bilhetes.

---

```markdown
Você é o engenheiro frontend sênior responsável pela plataforma "FAS ELITE — Sports Analytics & Trading Desk" (Next.js 14, TailwindCSS, Shadcn UI, Lucide Icons, Recharts).

Vamos refinar e elevar o dashboard para o padrão executivo final, integrando a Escada Oficial de Níveis, Sincronização Automática via GitHub e Central de Relatórios/Gráficos.

---

### 1. 🎨 IDENTIDADE VISUAL & AMBIENTE (BLOOMBERG HUD DESK)
- Tema escuro imersivo (Slate-950 puro, cards em Slate-900 com bordas suaves Slate-800/60).
- Cores Semânticas de Alta Precisão:
  - 🟢 GREEN: Emerald-400 / Emerald-500
  - 🔴 RED: Rose-500
  - 🟡 PENDING: Amber-400
  - 🟣 SUPREMO (Ouro/Filé): Violet-400 / Amber-400
  - 🔵 SAFE / Âncora: Sky-400 / Indigo-400
- Microinterações suaves, badges com pill design e números em fonte tabular/mono para alinhamento financeiro impecável.

---

### 2. ⚡ SINCRONIZAÇÃO DE DADOS & PERSISTÊNCIA (ZERO COMPLEXIDADE)
Implemente a camada de dados no `localStorage` com duas vias de atualização:
1. **Botão 'Sincronizar GitHub' (1 Clique no Header):**
   - Faz um `fetch()` direto do repositório público raw:
     `https://raw.githubusercontent.com/iadecria/tips/main/futebol/bilhetes_ativos.json`
   - Atualiza o estado do dashboard instantaneamente sem precisar recarregar a página.
   - Mostra toast notification de sucesso: "Dados sincronizados com o repositório oficial!".
2. **Modal 'Importar / Editar JSON':**
   - Modal acessível pelo ícone de engrenagem/código no header onde o usuário pode visualizar, colar ou editar manualmente o JSON do dia e salvar no `localStorage`.

---

### 3. 🏛️ A ESCADA OFICIAL DE BILHETES (ORGANIZAÇÃO EM ABAS/SEÇÕES)

O layout deve organizar os bilhetes exatamente na hierarquia de assertividade:

#### 🎯 NÍVEL 0 — DESAFIO SOROS (O Sniper Sagrado)
- Card compacto com borda destacada e barra de progresso visual do Dia 1 ao 30.
- Regra de ouro: Apenas 1 ou no máximo 2 jogos de convicção absoluta (Odd @1.25 a @1.45).
- Exibe: Dia Atual, Stake de Entrada (R$), Odd Sniper, Retorno Potencial e Histórico de Dias Anteriores (badges clicáveis Green/Red).

#### ⭐ NÍVEL 1 — BILHETE SUPREMO (O Filé do Dia / Da Noite)
- O card de destaque principal com seletor interno de abas:
  - `[ 🌐 Global (Todas as Melhores) ]`
  - `[ 🥪 Turno 1 (Almoço / Prime Time) ]` ➔ Liquidação rápida antecipada.
  - `[ 🌆 Turno 2 (Tarde / Late Night) ]` ➔ Jogos complementares.
- Barra de Progresso visual animada de acertos (ex: 2/7 Batendo ➔ barra em Emerald preenchendo).
- Botão "Copiar Boletim" no rodapé para formatar o texto com emojis e copiar para WhatsApp/Telegram.
- Simulador de Stake interativo (input de valor em R$ recalculando o retorno na hora).

#### 🥇 NÍVEL 2 — MÚLTIPLA 1: SAFE (Carro-Chefe / 70% da Banca)
- Card com abas interativas dos Stop Points:
  - `[ 🟢 Stop Point 1 (Âncora Máxima @1.60 a @1.85) ]`
  - `[ 🟡 Stop Point 2 (Blindagem @1.85 a @2.15) ]`
  - `[ 🔴 Stop Point 3 (Completa @2.20 a @2.60) ]`
- Alternar o stop point altera instantaneamente a lista de jogos e a cotação final.

#### 🥈 NÍVEL 3, 4 E 5 — GRADES SECUNDÁRIAS (GRID DE 3 COLUNAS)
- **Múltipla 2: SAFE+** (Odd 2.50 a 3.50 — Alavancagem balanceada).
- **Múltipla 3: SUPER ATAQUE** (Odd 6.00 a 12.00 — Retorno agressivo com handicaps).
- **Múltipla 4: APOSENTAR O NETO** (Odd 50.00 a 150.00+ — Bingão recreativo de moeda de troco).

---

### 4. 📊 NOVA ABA: 'RELATÓRIOS & PERFORMANCE'
Crie uma aba de navegação superior chamada "Relatórios":
- **Gráfico de Evolução Patrimonial (LineChart - Recharts):** Curva de crescimento da banca dia a dia com tooltip financeiro.
- **Gráfico de Taxa de Acerto (PieChart / Donut):** Distribuição percentual de Greens vs Reds.
- **Tabela de Histórico de Rodadas Anteriores:** Lista com data, evento, cotação, status de liquidação e lucro/prejuízo registrado.

---

### 5. 🏀 COMPATIBILIDADE MULTI-ESPORTE (FUTEBOL & BASQUETE)
- No topo, o toggle `[ ⚽ Futebol (Champions League) ] | [ 🏀 Basquete (NBA / FIBA) ]` deve alternar o conteúdo:
  - **Futebol:** Exibe os jogos da Champions League (LASK, Liverpool, Aston Villa, Real Madrid, City, PSG).
  - **Basquete:** Exibe a rodada da NBA Preseason com foco obrigatório em **Pontos do Time (Team Total Over)** (Celtics Over 111.5, Spurs Over 109.5) e **Spreads Positivos Elásticos** (Nuggets +7.5).

Construa uma interface fluida, sem erros de tipagem, utilizando componentes Shadcn nativos (Tabs, Card, Badge, Progress, Dialog, Button, Tooltip, Input).
```
