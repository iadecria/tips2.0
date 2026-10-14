"""
FAS 3 - Odds Scanner & Ticket Multiplier (Multi-League Global Engine)
Varredura de odds oficiais da Pinnacle e principais casas para o Football Analysis System (FAS 3).
Cobre integralmente: Premier League, La Liga, Serie A, Bundesliga, Ligue 1, Liga Portugal, Brasileirão A e B.
"""

import json
import urllib.request
import datetime
import sys
from typing import Dict, List, Any, Optional

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "2949bd401486c8c955216b3fb58c68c4"
BASE_URL = "https://api.the-odds-api.com/v4"

MAJOR_LEAGUES = [
    ("soccer_epl", "Premier League (Inglaterra)"),
    ("soccer_spain_la_liga", "La Liga (Espanha)"),
    ("soccer_italy_serie_a", "Serie A (Itália)"),
    ("soccer_germany_bundesliga", "Bundesliga (Alemanha)"),
    ("soccer_france_ligue_one", "Ligue 1 (França)"),
    ("soccer_portugal_primeira_liga", "Liga Portugal"),
    ("soccer_brazil_campeonato", "Brasileirão Série A"),
    ("soccer_brazil_serie_b", "Brasileirão Série B"),
    ("soccer_uefa_champs_league", "UEFA Champions League"),
    ("soccer_uefa_nations_league", "UEFA Nations League")
]

def get_league_odds(sport_key: str) -> List[Dict[str, Any]]:
    """Consulta odds da liga com timeout resiliente"""
    url = f"{BASE_URL}/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=eu,us,uk&markets=h2h,totals"
    req = urllib.request.Request(url, headers={"User-Agent": "FAS3-OddsClient/2.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"⚠️ Erro ao consultar {sport_key}: {e}")
        return []

def calculate_double_chance_odd(home_odd: float, draw_odd: float) -> float:
    """Calcula a odd justa de Dupla Chance 1X a partir de Home e Draw"""
    if not home_odd or not draw_odd:
        return 0.0
    prob = (1.0 / home_odd) + (1.0 / draw_odd)
    return round(1.0 / prob, 2)

def scan_all_major_leagues(hours_ahead: int = 36):
    """Varre todas as grandes ligas ativas e exibe fixtures com odds Pinnacle"""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    print("\n" + "="*65)
    print(f"🌍 VARREDURA FAS 3: TODAS AS GRANDES LIGAS (PRÓXIMAS {hours_ahead}h)")
    print("="*65)
    
    total_found = 0
    for sport_key, league_name in MAJOR_LEAGUES:
        fixtures = get_league_odds(sport_key)
        valid_events = []
        for g in fixtures:
            ct = datetime.datetime.fromisoformat(g["commence_time"].replace("Z", "+00:00"))
            diff_hours = (ct - now_utc).total_seconds() / 3600.0
            if -1.0 <= diff_hours <= hours_ahead:
                brt = ct - datetime.timedelta(hours=3)
                valid_events.append((brt, g))
                
        if valid_events:
            valid_events.sort(key=lambda x: x[0])
            print(f"\n🏆 {league_name} ({len(valid_events)} jogos no período)")
            for brt_time, g in valid_events:
                total_found += 1
                home = g.get("home_team")
                away = g.get("away_team")
                
                # Extrair Pinnacle
                pinn_data = next((b for b in g.get("bookmakers", []) if b.get("title") == "Pinnacle"), None)
                h_odd, d_odd, a_odd = "-", "-", "-"
                if pinn_data:
                    h2h = {m.get("key"): m for m in pinn_data.get("markets", [])}.get("h2h", {}).get("outcomes", [])
                    h_odd = next((o.get("price") for o in h2h if o.get("name") == home), "-")
                    d_odd = next((o.get("price") for o in h2h if o.get("name") == "Draw"), "-")
                    a_odd = next((o.get("price") for o in h2h if o.get("name") == away), "-")
                
                time_fmt = brt_time.strftime("%d/%m %H:%M")
                print(f"  👉 [{time_fmt} BRT] {home} x {away}")
                print(f"     Pinnacle: 1: @{h_odd} | X: @{d_odd} | 2: @{a_odd}")

    print(f"\nTotal de eventos consolidados no radar: {total_found}")
    print("="*65)

def print_pinnacle_slip(tickets: List[Dict[str, Any]]):
    print("\n" + "="*55)
    print("📋 GUIA DE EXECUÇÃO: BOLETIM OFICIAL PINNACLE (pinnacle.bet.br)")
    print("="*55)
    for idx, t in enumerate(tickets, 1):
        print(f"\n🎫 {t['title']} — Multiplicador: @{t['multiplier']:.2f}")
        print(f"💰 Retorno com R$ 50: R$ {50 * t['multiplier']:.2f} | Com R$ 100: R$ {100 * t['multiplier']:.2f}")
        print("📌 Passo a passo no site:")
        for s in t['legs']:
            print(f"   ▫️ Jogo: {s['match']}")
            print(f"      ➔ Categoria: [{s['market_group']}]")
            print(f"      ➔ Linha: {s['selection']} (Odd Pinnacle: @{s['odd']})")
        print(f"   👉 No boletim à direita, clique na aba 'ACUMULADA' / 'PARLAY' e confirme!")

def print_soros_slip():
    import os
    state_file = os.path.join(os.path.dirname(__file__), "soros_state.json")
    if not os.path.exists(state_file):
        return
    with open(state_file, "r", encoding="utf-8") as f:
        state = json.load(f)
        
    day = state.get("currentDay", 1)
    stake = state.get("currentStake", 10.00)
    target_days = state.get("targetDays", 30)
    
    # Seleção do Soros Oficial 14/10 (Espelho Stop Point 1): Liverpool Over 1.5 (@1.20) + Aston Villa 1X (@1.18) + Real Madrid X2 (@1.28) = @1.81
    mult = 1.20 * 1.18 * 1.28  # @1.81 na Pinnacle
    ret = stake * mult
    
    print("\n" + "="*55)
    print(f"🔥 DESAFIO SOROS FAS 30 DIAS — DIA {day} DE {target_days} (UEFA CHAMPIONS LEAGUE)")
    print("="*55)
    print(f"💵 Entrada de Hoje: R$ {stake:.2f} (Gestão de Reinício Dia 1)")
    print(f"🎯 Cotação da Tripla Blindada: @{mult:.2f} (Pinnacle)")
    print(f"💰 Retorno Estimado se Bater: R$ {ret:.2f}")
    print(f"🚀 Próximo Passo: Se GREEN, os R$ {ret:.2f} serão a entrada do DIA {day + 1}!")
    print("\n📌 Seleções Obrigatórias do Soros (Espelho Stop Point 1 SAFE):")
    print("   1️⃣ LASK Linz x Liverpool ➔ Mais de 1.5 Gols (Odd @1.20) [Raiffeisen Arena]")
    print("   2️⃣ Aston Villa x Fenerbahçe ➔ Aston Villa ou Empate (1X @1.18) [Villa Park]")
    print("   3️⃣ AS Roma x Real Madrid ➔ Real Madrid ou Empate (X2 @1.28) [Stadio Olimpico]")
    print(f"   👉 Na Pinnacle: Adicione as três seleções, vá na aba ACUMULADA e confirme com R$ {stake:.2f}!")
    print("="*55)

if __name__ == "__main__":
    if "--scan" in sys.argv:
        scan_all_major_leagues(hours_ahead=36)

    # Boletim Especial Pinnacle para a Rodada de 14/10 (UEFA Champions League - FAS 3 V5.0)
    pinnacle_tickets = [
        {
            "title": "⭐ BILHETE SUPREMO: O FILÉ DO DIA (Todas as Melhores Opções da Champions League)",
            "multiplier": 1.20 * 1.18 * 1.28 * 1.18 * 1.18 * 1.12 * 1.22,  # @3.67
            "legs": [
                {
                    "match": "LASK Linz x Liverpool (13:45 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.20
                },
                {
                    "match": "Aston Villa x Fenerbahçe (16:00 BRT)",
                    "market_group": "Dupla Chance",
                    "selection": "Aston Villa ou Empate (1X)",
                    "odd": 1.18
                },
                {
                    "match": "AS Roma x Real Madrid (16:00 BRT)",
                    "market_group": "Dupla Chance",
                    "selection": "Real Madrid ou Empate (X2)",
                    "odd": 1.28
                },
                {
                    "match": "Manchester City x Paris Saint-Germain (16:00 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.18
                },
                {
                    "match": "Bodø/Glimt x Borussia Dortmund (16:00 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.18
                },
                {
                    "match": "Slovan Bratislava x VfB Stuttgart (16:00 BRT)",
                    "market_group": "Total de Gols da Equipe",
                    "selection": "VfB Stuttgart 1+ Gol (Team Over 0.5)",
                    "odd": 1.12
                },
                {
                    "match": "Feyenoord x Como (13:45 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.22
                }
            ]
        },
        {
            "title": "BILHETE 1: TRIPLA ÂNCORA BLINDADA (SAFE - Champions League)",
            "multiplier": 1.20 * 1.18 * 1.28,  # @1.81
            "legs": [
                {
                    "match": "LASK Linz x Liverpool (13:45 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.20
                },
                {
                    "match": "Aston Villa x Fenerbahçe (16:00 BRT)",
                    "market_group": "Dupla Chance",
                    "selection": "Aston Villa ou Empate (1X)",
                    "odd": 1.18
                },
                {
                    "match": "AS Roma x Real Madrid (16:00 BRT)",
                    "market_group": "Dupla Chance",
                    "selection": "Real Madrid ou Empate (X2)",
                    "odd": 1.28
                }
            ]
        },
        {
            "title": "BILHETE 2: QUÁDRUPLA FORTE COM GOLS DA CHAMPIONS (SAFE + Man City x PSG Over 1.5)",
            "multiplier": 1.20 * 1.18 * 1.28 * 1.18,  # @2.14
            "legs": [
                {
                    "match": "LASK Linz x Liverpool (13:45 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.20
                },
                {
                    "match": "Aston Villa x Fenerbahçe (16:00 BRT)",
                    "market_group": "Dupla Chance",
                    "selection": "Aston Villa ou Empate (1X)",
                    "odd": 1.18
                },
                {
                    "match": "AS Roma x Real Madrid (16:00 BRT)",
                    "market_group": "Dupla Chance",
                    "selection": "Real Madrid ou Empate (X2)",
                    "odd": 1.28
                },
                {
                    "match": "Manchester City x Paris Saint-Germain (16:00 BRT)",
                    "market_group": "Total de Gols",
                    "selection": "Mais de 1.5 Gols",
                    "odd": 1.18
                }
            ]
        },
        {
            "title": "BILHETE 3: SUPER CLÁSSICOS & ATAQUE (ATTACK / PRA CIMA)",
            "multiplier": 1.62 * 1.48 * 1.42,  # ~3.40
            "legs": [
                {
                    "match": "Aston Villa x Fenerbahçe (16:00 BRT)",
                    "market_group": "Resultado da Partida (1X2)",
                    "selection": "Aston Villa Vence",
                    "odd": 1.62
                },
                {
                    "match": "Manchester City x Paris Saint-Germain (16:00 BRT)",
                    "market_group": "Ambos os Times Marcam",
                    "selection": "Ambos Marcam - Sim",
                    "odd": 1.48
                },
                {
                    "match": "LASK Linz x Liverpool (13:45 BRT)",
                    "market_group": "Resultado e Total",
                    "selection": "Liverpool Vence + Mais de 1.5 Gols",
                    "odd": 1.42
                }
            ]
        }
    ]
    print_pinnacle_slip(pinnacle_tickets)
    print_soros_slip()

