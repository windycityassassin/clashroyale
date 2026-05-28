# clashroyale

A small Flask app over the official Supercell API. Aggregates top-200 ladder data and exposes a transparent, heuristic bot-likelihood scorer for any player tag. No AI, no scraping, no auto-submission, no Easy Apply.

**Live tour:** [windycityassassin.github.io/clashroyale/](https://windycityassassin.github.io/clashroyale/)

## What it does

- **`/bot_check`** — score one player tag 0-100 on bot-likelihood. Returns every signal that fired (clanless, auto-name, level-trophy mismatch, zero donations, single-deck grind, round-the-clock play, etc.) with its weight and the underlying value. Verdict bucket: unlikely / suspicious / likely / very likely.
- **`/recent_opponents`** — give it *your* tag, it pulls your last 25 battles, runs the bot scorer on every unique opponent, sorts by score. ~50 API calls, ~10s.
- **`/card_usage`** — fetches the top-200 global ladder, pulls each player's current 8-card deck, aggregates usage frequency, ranks cards by % appearance. Renders a real bar table now (was a TODO stub).
- **`/synergy`** — pick a card, returns the 7 cards most often co-occurring with it in top-200 decks, with co-occurrence count and pair rate.
- **`/battle_replay`** — given a player tag, pulls the last 25 battles, extracts crowns, trophy delta, opponent deck, win/loss.

Pipeline is rate-limited to 5 req/s by `utils/api_client.py` (the Supercell ceiling). A top-200 sweep takes ~40 seconds; subsequent synergy queries are cached for the life of the process.

## On the bot detector

There is no ground truth in the Supercell API. Every signal in `utils/bot_detector.py` is a heuristic. Weights are rough. The output exposes each signal so you can argue with the verdict instead of trusting a black box. False positives on smurfs and sold accounts are expected.

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

Personal project, Oct 2024, expanded May 2026 with the bot detector, recent-opponent scan, and card synergy views. All five pages wired and smoke-tested in-process. Live use requires a Supercell developer key with your egress IP whitelisted.

## Not

Not a deck builder. Not a matchmaking predictor. Not an ML project. Not a substitute for RoyaleAPI or Stats Royale — those services exist and do this at scale.
