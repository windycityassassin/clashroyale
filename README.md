# clashroyale

A small Flask app that aggregates deck composition and battle outcomes for the top 200 globally-ranked Clash Royale players via the official Supercell API. Two pages, no AI, no scraping — just rate-limited calls and aggregation.

**Live tour:** [windycityassassin.github.io/clashroyale/](https://windycityassassin.github.io/clashroyale/)

## What it does

- **`/card_usage`** — fetches the top-200 global ladder, pulls each player's current 8-card deck, aggregates usage frequency, ranks cards by % appearance.
- **`/battle_replay`** — given a player tag, pulls the last 25 battles, extracts crowns, trophy delta, opponent deck, win/loss.

Pipeline is rate-limited to 5 req/s by `utils/api_client.py` (the Supercell ceiling). A top-200 sweep takes ~40 seconds.

## Run it

```bash
# 1. register an app at developer.clashroyale.com, get a key,
#    whitelist your egress IP in the key's allowed-IPs list
# 2. drop the key in .env
echo "CLASH_ROYALE_API_KEY=ey..." > .env

cd clash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
# open http://localhost:5000/card_usage
```

The API key is IP-whitelisted on the Supercell side. For local dev that's your home IP; for any hosted version it's a fixed egress IP. This is why the live demo on the tour page is a UI layout rather than a real query — GitHub Pages has no backend, and a free PaaS would need its own whitelist entry.

## Stack

Flask 2.0 · requests + bespoke throttle · Jinja2 · vanilla JS · python-dotenv · Supercell Clash Royale API

## Status

Personal project, Oct 2024. Card-usage view is fully wired. Battle-replay view is fully wired. The `card_usage.js` chart-rendering layer is a TODO stub — the underlying `/api/card_usage` endpoint returns the data, but the front-end currently logs to console rather than rendering a chart.

## Not

Not a deck builder. Not a matchmaking predictor. Not an ML project. Not a substitute for RoyaleAPI or Stats Royale — those services exist and do this at scale.
