"""
Card synergy from co-occurrence in top-200 ladder decks.

Given a card name, returns the seven cards that most often share a deck
with it among current top-ladder players. Pure aggregation, no ML, no
hardcoded archetype knowledge. The signal is direct: 'top players who
run X also tend to run Y'.
"""

from collections import Counter


class SynergyAnalyzer:
    def __init__(self, api_client):
        self.api = api_client
        self._decks_cache = None

    def _load_decks(self, num_players=200):
        if self._decks_cache is not None:
            return self._decks_cache
        top = self.api.get_top_players(limit=num_players)
        if not top or "items" not in top:
            return []
        decks = []
        for p in top["items"]:
            pdata = self.api.get_player(p["tag"])
            if pdata and "currentDeck" in pdata:
                decks.append([c["name"] for c in pdata["currentDeck"]])
        self._decks_cache = decks
        return decks

    def partners_for(self, card_name, top_k=7):
        decks = self._load_decks()
        if not decks:
            return {"error": "no deck data"}

        decks_with_card = [d for d in decks if card_name in d]
        n_with = len(decks_with_card)
        if n_with == 0:
            return {
                "card": card_name,
                "decks_with_card": 0,
                "total_decks": len(decks),
                "partners": [],
                "note": "no top-200 deck currently contains this card",
            }

        partner_counts = Counter()
        for d in decks_with_card:
            for c in d:
                if c != card_name:
                    partner_counts[c] += 1

        partners = [
            {
                "name": name,
                "co_occurrences": count,
                "pair_rate": round((count / n_with) * 100, 1),
            }
            for name, count in partner_counts.most_common(top_k)
        ]
        return {
            "card": card_name,
            "decks_with_card": n_with,
            "total_decks": len(decks),
            "card_pick_rate": round((n_with / len(decks)) * 100, 1),
            "partners": partners,
        }
