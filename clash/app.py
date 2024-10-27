from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from utils.api_client import ClashRoyaleAPI
from utils.card_analyzer import CardAnalyzer
from utils.battle_analyzer import BattleAnalyzer
import os
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Retrieve and clean API key from environment variables
api_key = os.getenv('CLASH_ROYALE_API_KEY', '').strip()
app.logger.info(f"Loaded API Key: {api_key[:10]}...{api_key[-10:]}")

# Initialize API client and analyzers
api_client = ClashRoyaleAPI(api_key=api_key)
card_analyzer = CardAnalyzer(api_client)
battle_analyzer = BattleAnalyzer(api_client)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/card_usage')
def card_usage():
    try:
        card_data = card_analyzer.get_card_usage()
        app.logger.info(f"Card usage data: {card_data}")
        if isinstance(card_data, dict) and "error" in card_data:
            return render_template('card_usage.html', error=card_data["error"])
        return render_template('card_usage.html', data=card_data)
    except Exception as e:
        app.logger.error(f"Error in card_usage route: {str(e)}")
        return render_template('card_usage.html', error=str(e))

@app.route('/api/card_usage')
def api_card_usage():
    try:
        data = card_analyzer.get_card_usage()
        if isinstance(data, dict) and "error" in data:
            return jsonify(data), 404
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error in card usage analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/battle_replay')
def battle_replay():
    return render_template('battle_replay.html')

@app.route('/api/battle_replay', methods=['POST'])
def api_battle_replay():
    try:
        player_tag = request.json['player_tag']
        app.logger.info(f"Received request for player tag: {player_tag}")  # Debug log
        battles = battle_analyzer.analyze_recent_battles(player_tag)
        app.logger.info(f"Battle analysis result: {battles}")  # Debug log
        return jsonify(battles)
    except Exception as e:
        app.logger.error(f"Error in battle replay analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/battle_stats', methods=['POST'])
def api_battle_stats():
    try:
        player_tag = request.json['player_tag']
        data = battle_analyzer.get_battle_stats(player_tag)
        if isinstance(data, dict) and "error" in data:
            return jsonify(data), 404
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error in battle stats analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/most_used_cards', methods=['POST'])
def api_most_used_cards():
    try:
        player_tag = request.json['player_tag']
        data = battle_analyzer.get_most_used_cards(player_tag)
        if isinstance(data, dict) and "error" in data:
            return jsonify(data), 404
        return jsonify(data)
    except Exception as e:
        app.logger.error(f"Error in most used cards analysis: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)