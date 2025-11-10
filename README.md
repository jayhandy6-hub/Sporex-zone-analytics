# spore-zone-analytics

Prototype complet pour **SPOREX STATS** — dashboard de prédictions football (7 grands championnats), automation GitHub Actions, intégration Telegram.

## Contenu
- `backend/` : scripts Python pour récupérer les odds (The Odds API), scraper SofaScore prototype, analyser et publier.
- `frontend/` : React app prototype (fichier `src/App.jsx`) utilisant `matches_today.json`.
- `.github/workflows/daily-update.yml` : workflow cron quotidien (09:30 Africa/Douala => 08:30 UTC).
- `matches_today.json` : généré par le script `analyze_and_publish.py`.

## Déploiement rapide
1. Crée un repo GitHub nommé **spore-zone-analytics** et pousse ces fichiers.
2. Crée un bot Telegram via @BotFather et ajoute-le en admin à ton canal SPOREX ZONE.
3. Dans GitHub repo settings -> Secrets, ajoute:
   - THE_ODDS_API_KEY
   - TELEGRAM_BOT_TOKEN
   - TELEGRAM_CHAT_ID
   - GIT_EMAIL
   - GIT_NAME
4. Lance manuellement le workflow `SPOREX Daily Update` dans l'onglet Actions pour tester.
5. Déploie le frontend sur Vercel (ou Netlify) et configure `NEXT_PUBLIC_MATCHES_URL` pointant sur le JSON raw du repo:
   `https://raw.githubusercontent.com/<USER>/spore-zone-analytics/main/matches_today.json`

## Notes importantes
- Le scraper SofaScore est un prototype: respecter `robots.txt` et conditions d'utilisation. Pour production, préférez un flux officiel.
- Le modèle inclus est simplifié; pour meilleure précision, entraîner un modèle ML avec historique.
- Le seuil ≥80% est strict et générera peu de signaux. Ajuster si nécessaire.

## Support
Si tu veux, je peux:
- Te fournir un zip prêt à uploader (inclus).
- T'aider pas-à-pas pour la création du repo et l'ajout des secrets.
- Améliorer le modèle et la couverture des features.
