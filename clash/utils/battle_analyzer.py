class BattleAnalyzer:
    def __init__(self, api_client):
        self.api_client = api_client

    def analyze_recent_battles(self, player_tag):
        battles = self.api_client.get_player_battles(player_tag)
        if not battles:
            return {"error": "No battle data available"}

        analyzed_battles = []
        for battle in battles:
            analyzed_battle = self._analyze_single_battle(battle)
            analyzed_battles.append(analyzed_battle)

        return analyzed_battles

    def _analyze_single_battle(self, battle):
        team = battle.get("team", [{}])[0]
        opponent = battle.get("opponent", [{}])[0]

        analyzed_battle = {
            "battleTime": battle.get("battleTime"),
            "gameMode": battle.get("gameMode", {}).get("name", "Unknown"),
            "arena": battle.get("arena", {}).get("name", "Unknown"),
            "result": self._determine_result(team, opponent),
            "crownsEarned": team.get("crowns", 0),
            "crownsLost": opponent.get("crowns", 0),
            "trophyChange": team.get("trophyChange", 0),
            "playerDeck": self._get_deck_info(team.get("cards", [])),
            "opponentDeck": self._get_deck_info(opponent.get("cards", [])),
        }

        return analyzed_battle

    def _determine_result(self, team, opponent):
        team_crowns = team.get("crowns", 0)
        opponent_crowns = opponent.get("crowns", 0)
        if team_crowns > opponent_crowns:
            return "Victory"
        elif team_crowns < opponent_crowns:
            return "Defeat"
        else:
            return "Draw"

    def _get_deck_info(self, cards):
        return [
            {
                "name": card.get("name", "Unknown"),
                "level": card.get("level", 0),
                "maxLevel": card.get("maxLevel", 0),
                "iconUrl": card.get("iconUrls", {}).get("medium", "")
            }
            for card in cards
        ]

    def get_battle_stats(self, player_tag):
        battles = self.analyze_recent_battles(player_tag)
        if isinstance(battles, dict) and "error" in battles:
            return battles

        total_battles = len(battles)
        victories = sum(1 for battle in battles if battle["result"] == "Victory")
        defeats = sum(1 for battle in battles if battle["result"] == "Defeat")
        draws = total_battles - victories - defeats

        return {
            "totalBattles": total_battles,
            "victories": victories,
            "defeats": defeats,
            "draws": draws,
            "winRate": (victories / total_battles) * 100 if total_battles > 0 else 0,
            "averageCrownsEarned": sum(battle["crownsEarned"] for battle in battles) / total_battles if total_battles > 0 else 0,
            "averageCrownsLost": sum(battle["crownsLost"] for battle in battles) / total_battles if total_battles > 0 else 0,
            "totalTrophyChange": sum(battle["trophyChange"] for battle in battles),
        }

    def get_most_used_cards(self, player_tag, top_n=8):
        battles = self.analyze_recent_battles(player_tag)
        if isinstance(battles, dict) and "error" in battles:
            return battles

        card_usage = {}
        for battle in battles:
            for card in battle["playerDeck"]:
                card_name = card["name"]
                if card_name in card_usage:
                    card_usage[card_name] += 1
                else:
                    card_usage[card_name] = 1

        sorted_cards = sorted(card_usage.items(), key=lambda x: x[1], reverse=True)
        return [{"name": card, "usageCount": count} for card, count in sorted_cards[:top_n]]