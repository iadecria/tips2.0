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
        
    day = state.get("currentDay", 3)
    stake = state.get("currentStake", 37.17)
    target_days = state.get("targetDays", 30)
    
    # Seleção do Soros Oficial 12/10: Atalanta ML (@1.54) + Criciúma 1X (@1.05) + Fortaleza 1X (@1.24) = @2.00
    mult = 1.54 * 1.05 * 1.24  # @2.00 na Pinnacle
    ret = stake * mult
    
    print("\n" + "="*55)
    print(f"🔥 DESAFIO SOROS FAS 30 DIAS — DIA {day} DE {target_days} (ELITE GLOBAL)")
    print("="*55)
    print(f"💵 Entrada de Hoje: R$ {stake:.2f} (Lucro acumulado dos Dias 1 e 2)")
    print(f"🎯 Cotação da Tripla Blindada: @{mult:.2f} (Pinnacle)")
    print(f"💰 Retorno Estimado se Bater: R$ {ret:.2f}")
    print(f"🚀 Próximo Passo: Se GREEN, os R$ {ret:.2f} serão a entrada do DIA {day + 1}!")
    print("\n📌 Seleções Obrigatórias do Soros (Máxima Proteção & Abismo Técnico):")
    print("   1️⃣ Atalanta x Venezia ➔ Atalanta Vence (Odd @1.54) [Gewiss Stadium]")
    print("   2️⃣ Criciúma x América Mineiro ➔ Criciúma ou Empate (1X) (Odd @1.05) [Heriberto Hülse]")
    print("   3️⃣ Fortaleza x CRB ➔ Fortaleza ou Empate (1X) (Odd @1.24) [Castelão]")
    print(f"   👉 Na Pinnacle: Adicione as três seleções, vá na aba ACUMULADA e confirme com R$ {stake:.2f}!")
    print("="*55)

if __name__ == "__main__":
    if "--scan" in sys.argv:
        scan_all_major_leagues(hours_ahead=36)

    # Boletim Especial Pinnacle para a Rodada de 12/10 (Consenso Multi-IA Global)
    pinnacle_tickets = [
        {
            "title": "BILHETE 1: TRIPLA ÂNCORA DE ELITE (SAFE - Europa & Brasil)",
            "multiplier": 1.54 * 1.05 * 1.24,  # @2.00
            "legs": [
                {
                    "match": "Atalanta BC x Venezia (Serie A - 13:30 BRT)",
                    "market_group": "Resultado da Partida / Linha de Dinheiro (1X2)",
                    "selection": "Atalanta Vence (Casa / 1)",
                    "odd": 1.54
                },
                {
                    "match": "Criciúma x América Mineiro (Série B - 19:30 BRT)",
                    "market_group": "Dupla Chance (1X2)",
                    "selection": "Criciúma ou Empate (1X)",
                    "odd": 1.05
                },
                {
                    "match": "Fortaleza x CRB (Série B - 16:00 BRT)",
                    "market_group": "Dupla Chance (1X2)",
                    "selection": "Fortaleza ou Empate (1X)",
                    "odd": 1.24
                }
            ]
        },
        {
            "title": "BILHETE 2: QUÁDRUPLA EQUILIBRADA (SAFE + Série A Furacão X2)",
            "multiplier": 1.54 * 1.05 * 1.24 * 1.28,  # @2.57
            "legs": [
                {
                    "match": "Atalanta BC x Venezia (13:30 BRT)",
                    "market_group": "Resultado da Partida (1X2)",
                    "selection": "Atalanta Vence",
                    "odd": 1.54
                },
                {
                    "match": "Criciúma x América Mineiro (19:30 BRT)",
                    "market_group": "Dupla Chance (1X2)",
                    "selection": "Criciúma ou Empate (1X)",
                    "odd": 1.05
                },
                {
                    "match": "Fortaleza x CRB (16:00 BRT)",
                    "market_group": "Dupla Chance (1X2)",
                    "selection": "Fortaleza ou Empate (1X)",
                    "odd": 1.24
                },
                {
                    "match": "Chapecoense x Athletico Paranaense (19:30 BRT)",
                    "market_group": "Dupla Chance (1X2)",
                    "selection": "Athletico-PR ou Empate (X2)",
                    "odd": 1.28
                }
            ]
        },
        {
            "title": "BILHETE 3: SUPER CLÁSSICOS & ATAQUE (ATTACK / PRA CIMA)",
            "multiplier": 1.80 * 1.88 * 1.98 * 1.91,  # ~12.80
            "legs": [
                {
                    "match": "Atalanta BC x Venezia (Serie A - 13:30 BRT)",
                    "market_group": "Resultado e Total",
                    "selection": "Atalanta Vence + Mais de 1.5 Gols",
                    "odd": 1.80
                },
                {
                    "match": "Famalicão x Alverca (Liga Portugal - 16:15 BRT)",
                    "market_group": "Resultado da Partida (1X2)",
                    "selection": "Famalicão Vence",
                    "odd": 1.88
                },
                {
                    "match": "Chapecoense x Athletico-PR (19:30 BRT)",
                    "market_group": "Resultado da Partida (1X2)",
                    "selection": "Athletico-PR Vence",
                    "odd": 1.98
                },
                {
                    "match": "Fortaleza x CRB (16:00 BRT)",
                    "market_group": "Resultado da Partida (1X2)",
                    "selection": "Fortaleza Vence",
                    "odd": 1.91
                }
            ]
        }
    ]
    print_pinnacle_slip(pinnacle_tickets)
    print_soros_slip()

