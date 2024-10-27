import logging
from collections import Counter

class CardAnalyzer:
    def __init__(self, api_client):
        self.api_client = api_client
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_card_usage(self, num_players=200):
        self.logger.info(f"Fetching top {num_players} players...")
        top_players = self.api_client.get_top_players(limit=num_players)
        
        self.logger.info(f"API Response for top players: {top_players}")
        
        if not top_players or 'items' not in top_players:
            self.logger.warning("No top player data available")
            return {"error": "No top player data available"}

        self.logger.info(f"Found {len(top_players['items'])} top players")

        all_cards = []
        for player in top_players['items']:
            self.logger.info(f"Fetching data for player {player['tag']}")
            player_data = self.api_client.get_player(player['tag'])
            self.logger.info(f"Player data: {player_data}")
            if player_data and 'currentDeck' in player_data:
                deck_cards = [card['name'] for card in player_data['currentDeck']]
                self.logger.info(f"Player {player['tag']} deck: {deck_cards}")
                all_cards.extend(deck_cards)
            else:
                self.logger.warning(f"No deck data for player {player['tag']}")

        if not all_cards:
            self.logger.warning("No card data collected")
            return {"error": "No card data collected"}

        self.logger.info(f"Total cards collected: {len(all_cards)}")

        card_usage = Counter(all_cards)
        total_decks = len(all_cards) / 8  # 8 cards per deck

        card_stats = {
            card: {
                'count': count,
                'usage_rate': (count / total_decks) * 100
            } for card, count in card_usage.items()
        }
        
        sorted_stats = dict(sorted(card_stats.items(), key=lambda x: x[1]['usage_rate'], reverse=True))

        self.logger.info(f"Analyzed {len(sorted_stats)} unique cards")
        return sorted_stats

    def get_popular_decks(self, num_players=200):
        self.logger.info(f"Fetching top {num_players} players for popular decks...")
        top_players = self.api_client.get_top_players(limit=num_players)
        
        if not top_players or 'items' not in top_players:
            self.logger.warning("No top player data available for popular decks")
            return {"error": "No top player data available"}

        decks = []
        for player in top_players['items']:
            self.logger.info(f"Fetching deck for player {player['tag']}")
            player_data = self.api_client.get_player(player['tag'])
            if player_data and 'currentDeck' in player_data:
                deck = tuple(sorted([card['name'] for card in player_data['currentDeck']]))
                decks.append(deck)
            else:
                self.logger.warning(f"No deck data for player {player['tag']}")

        if not decks:
            self.logger.warning("No deck data collected")
            return {"error": "No deck data collected"}

        deck_counter = Counter(decks)
        total_decks = len(decks)

        popular_decks = [
            {
                'cards': list(deck),
                'count': count,
                'usage_rate': (count / total_decks) * 100
            } for deck, count in deck_counter.most_common(10)
        ]

        self.logger.info(f"Analyzed {len(popular_decks)} popular decks")
        return popular_decks

    def get_card_win_rates(self, num_players=200):
        self.logger.info(f"Fetching top {num_players} players for card win rates...")
        top_players = self.api_client.get_top_players(limit=num_players)
        
        if not top_players or 'items' not in top_players:
            self.logger.warning("No top player data available for card win rates")
            return {"error": "No top player data available"}

        card_wins = Counter()
        card_losses = Counter()

        for player in top_players['items']:
            self.logger.info(f"Fetching battle log for player {player['tag']}")
            battles = self.api_client.get_player_battles(player['tag'])
            for battle in battles:
                if 'team' in battle and battle['team']:
                    deck = [card['name'] for card in battle['team'][0].get('cards', [])]
                    if battle['team'][0].get('crowns', 0) > battle['opponent'][0].get('crowns', 0):
                        card_wins.update(deck)
                    else:
                        card_losses.update(deck)

        if not card_wins and not card_losses:
            self.logger.warning("No battle data collected")
            return {"error": "No battle data collected"}

        win_rates = {}
        for card in set(list(card_wins.keys()) + list(card_losses.keys())):
            wins = card_wins[card]
            losses = card_losses[card]
            total_games = wins + losses
            if total_games > 0:
                win_rate = (wins / total_games) * 100
                win_rates[card] = {
                    'win_rate': win_rate,
                    'total_games': total_games
                }

        sorted_win_rates = dict(sorted(win_rates.items(), key=lambda x: x[1]['win_rate'], reverse=True))

        self.logger.info(f"Analyzed win rates for {len(sorted_win_rates)} cards")
        return sorted_win_rates