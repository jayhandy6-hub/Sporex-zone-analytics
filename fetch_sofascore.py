import requests
from bs4 import BeautifulSoup
import time

BASE = "https://www.sofascore.com"

def get_team_summary(team_name):
    # Prototype: attempt to search and return simple summary stats.
    try:
        search_url = f"{BASE}/search/teams?q={team_name.replace(' ', '%20')}"
        r = requests.get(search_url, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        # Best-effort: find a link to the team (selectors may need update)
        link = soup.find("a")
        if not link or not link.get('href'):
            return {}
        team_path = link.get('href')
        r2 = requests.get(BASE + team_path, timeout=12)
        s2 = BeautifulSoup(r2.text, "html.parser")
        # Fallback prototype values
        summary = {
            "last5_wins": 3,
            "last5_draws": 1,
            "last5_losses": 1,
            "avg_rating": 6.9
        }
        time.sleep(0.5)
        return summary
    except Exception as e:
        print('SoFASCORE fetch error for', team_name, e)
        return {}
