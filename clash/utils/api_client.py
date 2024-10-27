import os
import requests
import time
import logging
from functools import wraps

class ClashRoyaleAPI:
    BASE_URL = "https://api.clashroyale.com/v1"
    
    # Rate limit: 5 requests per second
    CALLS_PER_SECOND = 5
    PERIOD = 1

    def __init__(self, api_key=None):
        self.api_key = api_key.strip() if api_key else os.getenv('CLASH_ROYALE_API_KEY', '').strip()
        print(f"ClashRoyaleAPI initialized with key: {self.api_key[:10]}...{self.api_key[-10:]}")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        self._last_request_time = 0
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)

    def rate_limited(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            current_time = time.time()
            time_passed = current_time - self._last_request_time
            if time_passed < self.PERIOD / self.CALLS_PER_SECOND:
                time.sleep((self.PERIOD / self.CALLS_PER_SECOND) - time_passed)
            self._last_request_time = time.time()
            return func(self, *args, **kwargs)
        return wrapper

    @rate_limited
    def _make_request(self, endpoint):
        url = f"{self.BASE_URL}{endpoint}"
        self.logger.info(f"Request URL: {url}")
        self.logger.info(f"Request Headers: {self.headers}")
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()  # This will raise an exception for HTTP errors
            data = response.json()
            self.logger.info(f"API Response: {data}")
            return data
        except requests.exceptions.RequestException as e:
            self.logger.error(f"API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                self.logger.error(f"Response content: {e.response.content}")
            return None

    def get_player(self, player_tag):
        encoded_tag = requests.utils.quote(player_tag)
        return self._make_request(f"/players/{encoded_tag}")

    def get_player_battles(self, player_tag):
        encoded_tag = requests.utils.quote(player_tag)
        return self._make_request(f"/players/{encoded_tag}/battlelog")

    def get_top_players(self, locationId='global', limit=200):
        return self._make_request(f"/locations/{locationId}/rankings/players?limit={limit}")

    def get_clan_info(self, clan_tag):
        encoded_tag = requests.utils.quote(clan_tag)
        return self._make_request(f"/clans/{encoded_tag}")

    def get_current_river_race(self, clan_tag):
        encoded_tag = requests.utils.quote(clan_tag)
        return self._make_request(f"/clans/{encoded_tag}/currentriverrace")

    def get_cards(self):
        return self._make_request("/cards")