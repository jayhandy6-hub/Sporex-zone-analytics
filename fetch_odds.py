import os, requests, time

ODDS_KEY = os.environ.get("THE_ODDS_API_KEY")
HEADERS = {"Accept": "application/json"}

SPORT_KEYS = {
    "Premier League": "soccer_epl",
    "LaLiga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga",
    "Ligue 1": "soccer_french_ligue_one",
    "Primeira Liga": "soccer_portugal_primeira_liga",
    "Eredivisie": "soccer_netherlands_eredivisie"
}

BASE = "https://api.the-odds-api.com/v4/sports/{}/odds"

def fetch_for_sport(sport_key):
    url = BASE.format(sport_key)
    params = {
        "apiKey": ODDS_KEY,
        "regions": "eu,uk",
        "markets": "h2h",
        "oddsFormat": "decimal"
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()

def gather_all():
    all_events = []
    for league, key in SPORT_KEYS.items():
        try:
            data = fetch_for_sport(key)
            for ev in data:
                ev["_league"] = league
                all_events.append(ev)
            time.sleep(1)
        except Exception as e:
            print(f"Erreur fetch {league}: {e}")
    return all_events

if __name__ == "__main__":
    events = gather_all()
    print(f"Récupéré {len(events)} events")
    for e in events[:3]:
        print(e.get("home_team"), "vs", e.get("away_team"))
