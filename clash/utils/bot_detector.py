"""
Heuristic bot detector for Clash Royale players.

There is no ground truth in the Supercell API. Every signal here is a
heuristic, calibrated on common bot-account patterns (auto-generated
names, clanless, never donates, single-deck ladder grinding, level
inversions). Weights are rough. The point is transparency, not a verdict:
each signal returns its own fired/not-fired state so a human can argue
with the score.

Score interpretation:
  0  - 24 : unlikely bot
  25 - 49 : suspicious, worth a second look
  50 - 74 : likely bot
  75 - 100: very likely bot
"""

from collections import Counter
from datetime import datetime
import re


_AUTO_NAME_RE = re.compile(r"^(noname|player|user|guest)\W*\d+", re.IGNORECASE)
_DIGIT_HEAVY_RE = re.compile(r"^[^a-zA-Z]*$")  # no ascii letters at all


def _parse_battle_time(ts):
    # API format: "20241026T143005.000Z"
    if not ts:
        return None
    try:
        return datetime.strptime(ts.split(".")[0], "%Y%m%dT%H%M%S")
    except (ValueError, AttributeError):
        return None


class BotDetector:
    def __init__(self, api_client):
        self.api = api_client

    def score_player(self, player_tag):
        profile = self.api.get_player(player_tag)
        if not profile:
            return {"error": f"could not fetch profile for {player_tag}"}
        battles = self.api.get_player_battles(player_tag) or []

        signals = [
            self._sig_clanless(profile),
            self._sig_auto_name(profile),
            self._sig_level_trophy_mismatch(profile),
            self._sig_no_donations(profile),
            self._sig_no_favourite_card(profile),
            self._sig_few_cards_owned(profile),
            self._sig_no_badges(profile),
            self._sig_ladder_only(battles),
            self._sig_deck_monotony(battles),
            self._sig_round_the_clock(battles),
        ]

        score = sum(s["weight"] for s in signals if s["fired"])
        score = min(score, 100)

        if score >= 75:
            verdict = "very likely bot"
        elif score >= 50:
            verdict = "likely bot"
        elif score >= 25:
            verdict = "suspicious"
        else:
            verdict = "unlikely bot"

        return {
            "tag": profile.get("tag"),
            "name": profile.get("name"),
            "exp_level": profile.get("expLevel"),
            "trophies": profile.get("trophies"),
            "best_trophies": profile.get("bestTrophies"),
            "score": score,
            "verdict": verdict,
            "signals": signals,
        }

    def _sig_clanless(self, profile):
        clan = profile.get("clan")
        return {
            "name": "clanless",
            "description": "Player is not in a clan. Most active humans join one for donations.",
            "weight": 10,
            "fired": clan is None or not clan.get("tag"),
            "value": clan.get("name") if clan else None,
        }

    def _sig_auto_name(self, profile):
        name = profile.get("name", "") or ""
        is_auto = bool(_AUTO_NAME_RE.match(name)) or bool(
            _DIGIT_HEAVY_RE.match(name) and any(ch.isdigit() for ch in name)
        )
        return {
            "name": "auto_generated_name",
            "description": "Name looks auto-generated (e.g. 'noname12345', digit-only, no letters).",
            "weight": 15,
            "fired": is_auto,
            "value": name,
        }

    def _sig_level_trophy_mismatch(self, profile):
        # A king-level-20 with 5000 trophies is normal. A king-level-9
        # account with 5000 trophies is climbing impossibly fast, which is
        # either a smurf, a sold account, or a bot.
        lvl = profile.get("expLevel", 0) or 0
        trophies = profile.get("trophies", 0) or 0
        suspicious = lvl <= 30 and trophies >= 4500
        return {
            "name": "level_trophy_mismatch",
            "description": "King level too low for current trophy count (level<=30 with >=4500 trophies).",
            "weight": 15,
            "fired": suspicious,
            "value": f"level {lvl}, {trophies} trophies",
        }

    def _sig_no_donations(self, profile):
        # Donations are a season-bucket counter. Zero across an active
        # season is unusual for a human in a clan; combined with clanless
        # it's near-certain.
        d_given = profile.get("totalDonations", 0) or 0
        return {
            "name": "zero_total_donations",
            "description": "Account has never donated a card (totalDonations == 0).",
            "weight": 10,
            "fired": d_given == 0,
            "value": d_given,
        }

    def _sig_no_favourite_card(self, profile):
        fav = profile.get("currentFavouriteCard")
        return {
            "name": "no_favourite_card",
            "description": "No currentFavouriteCard set. Humans usually have one after a few weeks.",
            "weight": 5,
            "fired": fav is None,
            "value": fav.get("name") if fav else None,
        }

    def _sig_few_cards_owned(self, profile):
        # Real progression unlocks dozens of cards quickly. Bot farm
        # accounts often own only the cards in their grind deck plus a
        # few rares.
        owned = len(profile.get("cards", []) or [])
        return {
            "name": "few_cards_owned",
            "description": "Owns fewer than 30 distinct cards. Indicates a fresh or single-purpose account.",
            "weight": 10,
            "fired": owned < 30,
            "value": owned,
        }

    def _sig_no_badges(self, profile):
        badges = profile.get("badges", []) or []
        any_progress = any((b.get("progress", 0) or 0) > 10 for b in badges)
        return {
            "name": "no_badge_progress",
            "description": "No badge has progress > 10. Bots ignore achievements.",
            "weight": 5,
            "fired": not any_progress,
            "value": len(badges),
        }

    def _sig_ladder_only(self, battles):
        if not battles:
            return {
                "name": "ladder_only",
                "description": "Battle log empty, cannot judge battle-type mix.",
                "weight": 0,
                "fired": False,
                "value": 0,
            }
        modes = [b.get("type", "") for b in battles]
        # 'PvP' is ladder. Tournaments/challenges/friendlies have other types.
        ladder_only = all(t == "PvP" for t in modes)
        return {
            "name": "ladder_only",
            "description": "Every recent battle is ranked ladder. No challenges, friendlies, or tournaments.",
            "weight": 10,
            "fired": ladder_only,
            "value": Counter(modes).most_common(),
        }

    def _sig_deck_monotony(self, battles):
        if not battles:
            return {
                "name": "single_deck_grind",
                "description": "Battle log empty, cannot judge deck variation.",
                "weight": 0,
                "fired": False,
                "value": None,
            }
        decks = []
        for b in battles:
            team = (b.get("team") or [{}])[0]
            cards = tuple(sorted(c.get("name", "") for c in team.get("cards", []) or []))
            if cards:
                decks.append(cards)
        if not decks:
            return {
                "name": "single_deck_grind",
                "description": "No deck data in battle log.",
                "weight": 0,
                "fired": False,
                "value": None,
            }
        unique = len(set(decks))
        # 25 battles with 1 unique deck = certain grind pattern.
        # 25 battles with 2-3 unique decks = still suspicious.
        return {
            "name": "single_deck_grind",
            "description": "Played the same deck for every recent battle. Bots farm with one deck.",
            "weight": 15,
            "fired": unique == 1 and len(decks) >= 10,
            "value": f"{unique} unique deck(s) across {len(decks)} battles",
        }

    def _sig_round_the_clock(self, battles):
        # Humans sleep. A battle log spanning all 24 hours of the day
        # within the most-recent-25 window means the account is on a
        # script. Use a coarse measure: number of distinct hour-of-day
        # buckets touched.
        times = [_parse_battle_time(b.get("battleTime")) for b in battles]
        times = [t for t in times if t]
        if len(times) < 10:
            return {
                "name": "round_the_clock_play",
                "description": "Not enough timestamped battles to judge play pattern.",
                "weight": 0,
                "fired": False,
                "value": len(times),
            }
        hours_touched = len({t.hour for t in times})
        # 25 battles spread across 18+ different hours of day is implausible
        # for a human; even a heavy player clusters in a few sessions.
        return {
            "name": "round_the_clock_play",
            "description": "Recent battles touched 18+ distinct hours of the day. Indicates 24/7 scripted play.",
            "weight": 15,
            "fired": hours_touched >= 18,
            "value": f"{hours_touched} distinct hours across {len(times)} battles",
        }


class RecentOpponentScanner:
    """Scan the opponents from your own last N battles and bot-score each."""

    def __init__(self, api_client):
        self.api = api_client
        self.detector = BotDetector(api_client)

    def scan(self, your_tag, limit=25):
        battles = self.api.get_player_battles(your_tag)
        if not battles:
            return {"error": f"no battle log for {your_tag}"}

        results = []
        seen_tags = set()
        for b in battles[:limit]:
            opp = (b.get("opponent") or [{}])[0]
            tag = opp.get("tag")
            if not tag or tag in seen_tags:
                continue
            seen_tags.add(tag)
            scored = self.detector.score_player(tag)
            if "error" in scored:
                continue
            scored["your_result"] = self._result(b)
            scored["battle_time"] = b.get("battleTime")
            results.append(scored)

        results.sort(key=lambda r: r["score"], reverse=True)
        return {
            "your_tag": your_tag,
            "scanned": len(results),
            "opponents": results,
        }

    @staticmethod
    def _result(battle):
        team = (battle.get("team") or [{}])[0]
        opp = (battle.get("opponent") or [{}])[0]
        tc = team.get("crowns", 0) or 0
        oc = opp.get("crowns", 0) or 0
        if tc > oc:
            return "win"
        if oc > tc:
            return "loss"
        return "draw"
