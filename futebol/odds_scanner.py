"""
FAS 3 - Odds Scanner & Discovery Engine V6.0 (Multi-League Global Engine)
Varredura automatizada de odds e fixtures oficiais para o Football Analysis System (FAS 3).
Cobre 20+ ligas e copas mundiais (Europa, Américas, Ásia e Copas Nacionais).
"""

import json
import urllib.request
import datetime
import sys
import os
from typing import Dict, List, Any, Optional

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Lista de chaves (suporta chave primária e rotação/fallback)
API_KEYS = [
    os.environ.get("ODDS_API_KEY", "2949bd401486c8c955216b3fb58c68c4"),
    "d6b8b0e8c8949826a7f053538c823ea4",
    "9f0c2e74288b8e85741695e2671239aa"
]
BASE_URL = "https://api.the-odds-api.com/v4"

# Catálogo completo e categorizado de competições no radar FAS
GLOBAL_COMPETITIONS = [
    # 🏆 Copas Nacionais Europeias (Cruciais para Terças e Quartas)
    ("soccer_spain_copa_del_rey", "Copa del Rey (Espanha)", "COPA_NACIONAL"),
    ("soccer_england_efl_cup", "EFL Cup / Carabao (Inglaterra)", "COPA_NACIONAL"),
    ("soccer_germany_dfb_pokal", "DFB-Pokal (Alemanha)", "COPA_NACIONAL"),
    ("soccer_italy_coppa_italia", "Coppa Italia", "COPA_NACIONAL"),
    
    # 👑 Grandes Ligas Europeias (Tier 1)
    ("soccer_epl", "Premier League (Inglaterra)", "LIGA_TIER_1"),
    ("soccer_spain_la_liga", "La Liga (Espanha)", "LIGA_TIER_1"),
    ("soccer_italy_serie_a", "Serie A (Itália)", "LIGA_TIER_1"),
    ("soccer_germany_bundesliga", "Bundesliga (Alemanha)", "LIGA_TIER_1"),
    ("soccer_france_ligue_one", "Ligue 1 (França)", "LIGA_TIER_1"),
    ("soccer_portugal_primeira_liga", "Liga Portugal", "LIGA_TIER_1"),
    ("soccer_netherlands_eredivisie", "Eredivisie (Holanda)", "LIGA_TIER_1"),
    ("soccer_turkey_super_league", "Süper Lig (Turquia)", "LIGA_TIER_1"),
    
    # 🌍 Copas Continentais
    ("soccer_uefa_champs_league", "UEFA Champions League", "CONTINENTAL"),
    ("soccer_uefa_europa_league", "UEFA Europa League", "CONTINENTAL"),
    ("soccer_uefa_europa_conference_league", "UEFA Conference League", "CONTINENTAL"),
    ("soccer_conmebol_copa_libertadores", "Copa Libertadores", "CONTINENTAL"),
    ("soccer_conmebol_copa_sudamericana", "Copa Sul-Americana", "CONTINENTAL"),
    
    # 🇧🇷 Futebol Brasileiro e Américas
    ("soccer_brazil_campeonato", "Brasileirão Série A", "BRASIL"),
    ("soccer_brazil_serie_b", "Brasileirão Série B", "BRASIL"),
    ("soccer_argentina_primera_division", "Argentina Primera", "AMERICAS"),
    ("soccer_mexico_ligamx", "Liga MX (México)", "AMERICAS"),
    
    # 🌟 Ligas Alternativas com Gigantes
    ("soccer_saudi_arabia_pro_league", "Saudi Pro League", "SPECIAL"),
    ("soccer_efl_champ", "Championship (Inglaterra)", "SEGUNDA_DIV")
]

def query_odds_api(sport_key: str, markets: str = "h2h,totals") -> List[Dict[str, Any]]:
    """Consulta odds da API com tentativa em múltiplas chaves e timeout seguro"""
    for api_key in API_KEYS:
        if not api_key:
            continue
        url = f"{BASE_URL}/sports/{sport_key}/odds/?apiKey={api_key}&regions=eu,us,uk&markets={markets}"
        req = urllib.request.Request(url, headers={"User-Agent": "FAS3-GlobalScanner/6.0"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                rem = resp.headers.get("x-requests-remaining")
                return data
        except Exception:
            continue
    return []

def calculate_double_chance(home_odd: float, draw_odd: float) -> float:
    """Calcula odd justa de Dupla Chance 1X"""
    if not home_odd or not draw_odd or home_odd <= 0 or draw_odd <= 0:
        return 0.0
    return round(1.0 / ((1.0 / home_odd) + (1.0 / draw_odd)), 2)

def scan_all_radar(hours_ahead: int = 40):
    """Varre todas as 20+ ligas e copas e classifica as melhores oportunidades do FAS"""
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    print("\n" + "="*70)
    print(f"🌍 VARREDURA FAS 3 GLOBAL V6.0: COBERTORES DE ELITE (PRÓXIMAS {hours_ahead}h)")
    print("="*70)
    
    all_events = []
    
    for sport_key, league_name, category in GLOBAL_COMPETITIONS:
        fixtures = query_odds_api(sport_key)
        for g in fixtures:
            c_str = g.get("commence_time")
            if not c_str:
                continue
            ct = datetime.datetime.fromisoformat(c_str.replace("Z", "+00:00"))
            diff_h = (ct - now_utc).total_seconds() / 3600.0
            if -1.0 <= diff_h <= hours_ahead:
                brt = ct - datetime.timedelta(hours=3)
                all_events.append({
                    "league": league_name,
                    "category": category,
                    "commence_brt": brt,
                    "home": g.get("home_team"),
                    "away": g.get("away_team"),
                    "bookmakers": g.get("bookmakers", [])
                })
                
    print(f"Total de jogos identificados na varredura global: {len(all_events)}")
    
    if not all_events:
        print("ℹ️ Dica: Quando a quota da API expirar, a varredura web setorizada do prompt mestre assume automaticamente.")
        return

    # Categorizadores FAS:
    super_favoritos = []
    mandantes_fortes = []
    
    for ev in all_events:
        home = ev["home"]
        away = ev["away"]
        # Extrair melhor bookmaker (Pinnacle ou BetOnline/Betfair)
        bk = next((b for b in ev["bookmakers"] if b.get("title") in ["Pinnacle", "Betfair", "Betsson", "1xBet"]), None)
        if not bk and ev["bookmakers"]:
            bk = ev["bookmakers"][0]
            
        if bk:
            mkts = {m.get("key"): m for m in bk.get("markets", [])}
            h2h = mkts.get("h2h", {}).get("outcomes", [])
            h_odd = next((o.get("price") for o in h2h if o.get("name") == home), None)
            d_odd = next((o.get("price") for o in h2h if o.get("name") == "Draw"), None)
            a_odd = next((o.get("price") for o in h2h if o.get("name") == away), None)
            
            ev["h_odd"] = h_odd
            ev["d_odd"] = d_odd
            ev["a_odd"] = a_odd
            ev["dc_1x"] = calculate_double_chance(h_odd, d_odd) if h_odd and d_odd else None
            
            if h_odd and h_odd <= 1.35:
                super_favoritos.append(ev)
            elif a_odd and a_odd <= 1.35:
                super_favoritos.append(ev)
            elif h_odd and 1.36 <= h_odd <= 1.85:
                mandantes_fortes.append(ev)

    print("\n" + "⭐"*30)
    print("🎯 SUPER FAVORITOS / ABISMO TÉCNICO (Odd Seca <= 1.35 — Base Supremo e Soros):")
    print("⭐"*30)
    for f in super_favoritos:
        t_str = f["commence_brt"].strftime("%d/%m %H:%M")
        print(f"  👉 [{t_str} BRT - {f['league']}] {f['home']} (1: @{f['h_odd']}) x {f['away']} (2: @{f['a_odd']}) | DC 1X: @{f['dc_1x']}")

    print("\n" + "🏰"*30)
    print("🛡️ MANDANTES DE CALDEIRÃO (Odd 1.36 a 1.85 — Base SAFE e SAFE+):")
    print("🏰"*30)
    for f in mandantes_fortes:
        t_str = f["commence_brt"].strftime("%d/%m %H:%M")
        print(f"  👉 [{t_str} BRT - {f['league']}] {f['home']} (1: @{f['h_odd']}) x {f['away']} (2: @{f['a_odd']}) | DC 1X: @{f['dc_1x']}")

if __name__ == "__main__":
    scan_all_radar(hours_ahead=40)
