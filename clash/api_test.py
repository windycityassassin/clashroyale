import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment variable and strip any whitespace/newlines
api_key = os.getenv('CLASH_ROYALE_API_KEY', '').strip()

# Check if API key is loaded
if not api_key:
    print("API Key not found. Please check your .env file.")
else:
    print(f"Loaded API Key: {api_key[:10]}...{api_key[-10:]}")

# Base URL for Clash Royale API
base_url = "https://api.clashroyale.com/v1"

# Headers for the request
headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "application/json"
}

# Test player tag (you can replace this with any valid player tag)
player_tag = "#9LRYU982G"  # Example player tag, replace with a real one if needed

# Encode the player tag
encoded_tag = requests.utils.quote(player_tag)

# Endpoint URL
url = f"{base_url}/players/{encoded_tag}"

def test_api():
    try:
        print(f"Making request to URL: {url}")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            print("API Key is valid and IP is whitelisted!")
            print("Player data:", response.json())
            return True
        elif response.status_code == 403:
            print("Error 403: Forbidden. This could mean:")
            print("1. Your API key is invalid")
            print("2. Your IP address is not whitelisted")
            print("Response content:", response.text)
            return False
        else:
            print(f"Unexpected status code: {response.status_code}")
            print("Response content:", response.text)
            return False
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    test_api()