import urllib.request
import json
import datetime
import sys

sys.stdout.reconfigure(encoding='utf-8')

API_KEY = "2949bd401486c8c955216b3fb58c68c4"
BASE_URL = "https://api.the-odds-api.com/v4"

def get_odds(sport_key, markets="h2h,spreads,totals"):
    url = f"{BASE_URL}/sports/{sport_key}/odds/?apiKey={API_KEY}&regions=eu,us,uk&markets={markets}"
    req = urllib.request.Request(url, headers={"User-Agent": "Scanner/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())

def inspect_sport(sport_key, title, markets="h2h,spreads,totals"):
    print(f"\n=======================================================")
    print(f"🏆 {title} ({sport_key})")
    print(f"=======================================================")
    try:
        data = get_odds(sport_key, markets=markets)
        print(f"Total fixtures returned: {len(data)}")
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        for g in data:
            c_time_str = g.get("commence_time")
            # parse time
            c_time = datetime.datetime.fromisoformat(c_time_str.replace("Z", "+00:00"))
            hours_diff = (c_time - now_utc).total_seconds() / 3600.0
            
            # Show events within the next 18 hours
            if -1.0 <= hours_diff <= 18.0:
                home = g.get("home_team")
                away = g.get("away_team")
                # convert to BRT (UTC-3)
                brt_time = c_time - datetime.timedelta(hours=3)
                print(f"\n👉 {home} x {away}")
                print(f"   Horário: {brt_time.strftime('%d/%m/%Y %H:%M')} BRT (daqui a {hours_diff:.1f}h)")
                
                # Bookmakers
                bks = g.get("bookmakers", [])
                for b in bks:
                    b_title = b.get("title")
                    if b_title in ["Pinnacle", "Betfair", "Betsson", "1xBet", "DraftKings", "FanDuel", "BetOnline.ag"]:
                        mkts = {m.get("key"): m for m in b.get("markets", [])}
                        
                        # h2h
                        h2h = mkts.get("h2h", {}).get("outcomes", [])
                        h_price = next((o.get("price") for o in h2h if o.get("name") == home), None)
                        a_price = next((o.get("price") for o in h2h if o.get("name") == away), None)
                        draw_price = next((o.get("price") for o in h2h if o.get("name") == "Draw"), None)
                        
                        # spreads
                        spreads = mkts.get("spreads", {}).get("outcomes", [])
                        h_spread = next((f"{o.get('point'):+g} (@{o.get('price')})" for o in spreads if o.get("name") == home), None)
                        a_spread = next((f"{o.get('point'):+g} (@{o.get('price')})" for o in spreads if o.get("name") == away), None)
                        
                        # totals
                        totals = mkts.get("totals", {}).get("outcomes", [])
                        over = next((f"Over {o.get('point')} (@{o.get('price')})" for o in totals if o.get("name") == "Over"), None)
                        under = next((f"Under {o.get('point')} (@{o.get('price')})" for o in totals if o.get("name") == "Under"), None)
                        
                        line_parts = [f"   🏦 {b_title:<12} | ML: {home} @{h_price}"]
                        if draw_price:
                            line_parts.append(f"Empate @{draw_price}")
                        line_parts.append(f"{away} @{a_price}")
                        if h_spread:
                            line_parts.append(f"| Spread: {home} {h_spread} / {away} {a_spread}")
                        if over:
                            line_parts.append(f"| Totals: {over} / {under}")
                        print(" ".join(line_parts))
    except Exception as e:
        print(f"Erro ao consultar {sport_key}: {e}")

if __name__ == "__main__":
    inspect_sport("basketball_wnba", "WNBA")
    inspect_sport("basketball_nba_preseason", "NBA Preseason")
    inspect_sport("soccer_argentina_primera_division", "Argentina Primera División")
    inspect_sport("soccer_mexico_ligamx", "Liga MX")
    inspect_sport("basketball_nbl", "NBL (Austrália - Madrugada)")
