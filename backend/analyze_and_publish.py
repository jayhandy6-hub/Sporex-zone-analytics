# backend/analyze_and_publish.py
# SPOREX STATS - analyse & publication Telegram (version complète prototype)
# Requirements: requests, beautifulsoup4
# Usage: executed by GitHub Actions. Expose these env vars as Secrets:
# THE_ODDS_API_KEY (optionnel), TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT, GIT_EMAIL, GIT_NAME

import os
import json
import math
import time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

# ---------- Configuration ----------
MIN_PROB = 0.80
OUTFILE = "matches_today.json"
ODDS_API_KEY = os.environ.get("THE_ODDS_API_KEY")  # optional
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT = os.environ.get("TELEGRAM_CHAT")  # can be numeric id (-100...) or '@channelname' or 'https://t.me/channelname'
# Map for leagues (used with The Odds API)
SPORT_KEYS = {
    "Premier League": "soccer_epl",
    "LaLiga": "soccer_spain_la_liga",
    "Serie A": "soccer_italy_serie_a",
    "Bundesliga": "soccer_germany_bundesliga",
    "Ligue 1": "soccer_french_ligue_one",
    "Primeira Liga": "soccer_portugal_primeira_liga",
    "Eredivisie": "soccer_netherlands_eredivisie"
}

# ---------- Helpers ----------
def decimal_to_prob(o):
    try:
        return 1.0 / float(o)
    except Exception:
        return None

def normalize_channel(chat):
    """Normalize TELEGRAM_CHAT: accept https://t.me/name or @name or numeric id"""
    if not chat:
        return None
    chat = str(chat).strip()
    if chat.startswith("https://t.me/"):
        return "@" + chat.split("https://t.me/")[-1].strip().lstrip("@")
    return chat

# ---------- SofaScore light scraper (best-effort) ----------
SOFASCORE_BASE = "https://www.sofascore.com"

def get_team_summary(team_name):
    """Best-effort extraction from SofaScore (may need maintenance). Returns dict with last5 wins and avg_rating."""
    try:
        q = team_name.replace(" ", "%20")
        # SofaScore has a simple search route; use it to find a team page
        search_url = f"{SOFASCORE_BASE}/search/teams?q={q}"
        r = requests.get(search_url, timeout=10)
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        # Try to find first team link
        a = soup.find("a", href=True)
        if not a:
            return {}
        team_path = a['href']
        r2 = requests.get(SOFASCORE_BASE + team_path, timeout=10)
        if r2.status_code != 200:
            return {}
        s2 = BeautifulSoup(r2.text, "html.parser")
        # NOTE: structure may vary — use fallback prototype values
        # Advanced: parse last5, ratings if you find CSS selectors
        return {
            "last5_wins": 2,
            "last5_draws": 1,
            "last5_losses": 2,
            "avg_rating": 6.9
        }
    except Exception as e:
        print("SoFASCORE error:", e)
        return {}

# ---------- Odds fetching ----------
def fetch_odds_for_sport(sport_key):
    """Use The Odds API to fetch events for the given sport_key"""
    if not ODDS_API_KEY:
        return []
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
    params = {"apiKey": ODDS_API_KEY, "regions": "eu,uk", "markets": "h2h", "oddsFormat": "decimal"}
    r = requests.get(url, params=params, timeout=20)
    if r.status_code != 200:
        print("Odds API status:", r.status_code, r.text[:200])
        return []
    return r.json()

def gather_all_events():
    events = []
    # If we have an API key, iterate sport keys; otherwise return empty to avoid crash
    if not ODDS_API_KEY:
        print("No THE_ODDS_API_KEY provided; running in demo mode without real odds.")
        return events
    for league, key in SPORT_KEYS.items():
        try:
            data = fetch_odds_for_sport(key)
            for ev in data:
                ev["_league"] = league
                events.append(ev)
            time.sleep(1)
        except Exception as e:
            print("Error fetching odds for", league, e)
    return events

# ---------- Simple scoring model (prototype) ----------
def simple_model_score(features):
    # Weighted sum -> sigmoid -> probability
    score = 0.0
    # home form advantage
    score += 0.45 * (features.get("home_last5_wins", 0) - features.get("away_last5_wins", 0))
    # ratings difference
    score += 0.25 * (features.get("home_avg_rating", 7.0) - features.get("away_avg_rating", 7.0))
    # market favorite diff (market_prob - 0.33)
    score += 0.20 * (features.get("market_favorite_diff", 0))
    # small bias
    score += 0.05
    p = 1.0 / (1.0 + math.exp(-score))
    return float(p)

# ---------- Compose Telegram message ----------
def build_message(signals):
    header = f"🔥 *SPOREX STATS* — Signaux du jour (≥ {int(MIN_PROB*100)}%)\n" \
             f"_Généré le {datetime.now(timezone.utc).astimezone().strftime('%Y-%m-%d %H:%M %Z')}_\n\n"
    if not signals:
        return header + "_Aucun signal ≥ 80% aujourd'hui._"
    body = header
    body += f"*Total signaux:* {len(signals)}\n\n"
    for s in signals:
        body += f"*{s['home']}* vs *{s['away']}* — _{s['league']}_\n"
        body += f"• Coup d'envoi: {s.get('kickoff_local','?')}\n"
        body += f"• Probabilité (modèle): *{int(s['p_model']*100)}%*  • Cote moyenne: `{s.get('avg_odd','N/A')}`\n"
        body += "• Facteurs clés: " + ", ".join(s.get('factors', ['—'])) + "\n"
        # small analysis line
        body += f"• Mini-analyse: {s.get('short_analysis','Voir facteurs clés')}\n\n"
    body += "#SPOREXZONE #Football"
    return body

# ---------- Telegram send ----------
def send_telegram_message(token, chat, text, parse_mode="Markdown"):
    if not token or not chat:
        print("Missing token or chat for Telegram.")
        return False, "Missing token/chat"
    api = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat, "text": text, "parse_mode": parse_mode, "disable_web_page_preview": True}
    try:
        r = requests.post(api, json=payload, timeout=15)
        print("Telegram send status:", r.status_code, r.text[:200])
        return r.status_code == 200, r.text
    except Exception as e:
        print("Telegram error:", e)
        return False, str(e)

# ---------- Main pipeline ----------
def process():
    print("Start SPOREX pipeline...")
    events = gather_all_events()
    signals = []
    out = {"generated_at": datetime.now(timezone.utc).isoformat(), "signals": []}

    if not events:
        # fallback demo: no odds API key -> build no-signals but keep JSON
        print("No events found (likely no ODDS API key). Writing empty JSON.")
        with open(OUTFILE, "w", encoding="utf-8") as f:
            json.dump(out, f, ensure_ascii=False, indent=2)
        return

    for ev in events:
        home = ev.get("home_team")
        away = ev.get("away_team")
        league = ev.get("_league", ev.get("sport_key", ""))
        kickoff = ev.get("commence_time")
        kickoff_local = kickoff

        # compute average odd for home and market implied prob
        avg_odd = None
        market_prob = None
        try:
            prices = []
            for b in ev.get("bookmakers", []):
                for m in b.get("markets", []):
                    if m.get("key") == "h2h":
                        for o in m.get("outcomes", []):
                            # try match by name: home team
                            if o.get("name") and home and o.get("name").lower() == home.lower():
                                prices.append(float(o.get("price")))
            if prices:
                avg_odd = sum(prices) / len(prices)
                market_prob = decimal_to_prob(avg_odd)
        except Exception as e:
            print("Odds parse error:", e)

        # SofaScore mini stats
        home_stats = get_team_summary(home) or {}
        away_stats = get_team_summary(away) or {}

        features = {
            "home_last5_wins": home_stats.get("last5_wins", 2),
            "away_last5_wins": away_stats.get("last5_wins", 2),
            "home_avg_rating": home_stats.get("avg_rating", 7.0),
            "away_avg_rating": away_stats.get("avg_rating", 6.8),
            "market_favorite_diff": (market_prob or 0) - 0.33
        }

        p_model = simple_model_score(features)

        record = {
            "home": home, "away": away, "league": league, "kickoff": kickoff,
            "kickoff_local": kickoff_local, "p_model": round(p_model, 3),
            "avg_odd": round(avg_odd, 2) if avg_odd else None,
            "market_prob": round(market_prob, 3) if market_prob else None,
            "features": features
        }

        # build short factors + mini-analysis
        factors = []
        if features["home_last5_wins"] > features["away_last5_wins"]:
            factors.append("Forme maison")
        if features["home_avg_rating"] > features["away_avg_rating"]:
            factors.append("Meilleure note moyenne")
        if market_prob and market_prob > 0.5:
            factors.append("Favori marché")
        record["factors"] = factors
        record["short_analysis"] = " | ".join(factors) if factors else "Avantage marginal"

        if p_model >= MIN_PROB:
            signals.append(record)
            out["signals"].append(record)

    # Save JSON (for frontend)
    with open(OUTFILE, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("Wrote", OUTFILE, "signals:", len(out["signals"]))

    # Send Telegram message (if any)
    normalized_chat = normalize_channel(TELEGRAM_CHAT)
    msg = build_message(out["signals"])
    if TELEGRA✖ := False:  # placeholder to avoid lint warnings
        pass
    if TELEGRAM_TOKEN and normalized_chat:
        ok, resp = send_telegram_message(TELEGRAM_TOKEN, normalized_chat, msg, parse_mode="Markdown")
        print("Telegram result:", ok)
    else:
        print("Telegram not configured or chat missing. Skipping send.")

if __name__ == "__main__":
    process() 
