from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from utils.api_client import ClashRoyaleAPI
from utils.card_analyzer import CardAnalyzer
from utils.battle_analyzer import BattleAnalyzer
from utils.bot_detector import BotDetector, RecentOpponentScanner
from utils.synergy import SynergyAnalyzer
import os
import logging

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

api_key = os.getenv('CLASH_ROYALE_API_KEY', '').strip()
if not api_key:
    # Fall back to mykey.txt for local dev (gitignored, same as .env)
    keyfile = os.path.join(os.path.dirname(__file__), 'mykey.txt')
    if os.path.exists(keyfile):
        with open(keyfile) as f:
            api_key = f.read().strip()
app.logger.info(f"Loaded API Key: {api_key[:10]}...{api_key[-10:] if len(api_key) > 20 else ''}")

api_client = ClashRoyaleAPI(api_key=api_key)
card_analyzer = CardAnalyzer(api_client)
battle_analyzer = BattleAnalyzer(api_client)
bot_detector = BotDetector(api_client)
opponent_scanner = RecentOpponentScanner(api_client)
synergy_analyzer = SynergyAnalyzer(api_client)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/card_usage')
def card_usage():
    try:
        card_data = card_analyzer.get_card_usage()
        if isinstance(card_data, dict) and "error" in card_data:
            return render_template('card_usage.html', error=card_data["error"])
        return render_template('card_usage.html', data=card_data)
    except Exception as e:
        app.logger.error(f"Error in card_usage route: {e}")
        return render_template('card_usage.html', error=str(e))


@app.route('/api/card_usage')
def api_card_usage():
    try:
        data = card_analyzer.get_card_usage()
        if isinstance(data, dict) and "error" in data:
            return jsonify(data), 404
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/battle_replay')
def battle_replay():
    return render_template('battle_replay.html')


@app.route('/api/battle_replay', methods=['POST'])
def api_battle_replay():
    try:
        player_tag = request.json['player_tag']
        battles = battle_analyzer.analyze_recent_battles(player_tag)
        return jsonify(battles)
    except Exception as e:
        app.logger.error(f"Error in battle replay analysis: {e}")
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
        return jsonify({"error": str(e)}), 500


# --- bot detection ---------------------------------------------------------

@app.route('/bot_check')
def bot_check():
    return render_template('bot_check.html', default_tag=os.getenv('PLAYER_TAG', '').strip())


@app.route('/api/bot_check', methods=['POST'])
def api_bot_check():
    try:
        tag = (request.json.get('player_tag') or '').strip()
        if not tag:
            return jsonify({"error": "player_tag required"}), 400
        if not tag.startswith('#'):
            tag = '#' + tag
        result = bot_detector.score_player(tag.upper())
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in bot_check: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/recent_opponents')
def recent_opponents():
    return render_template('recent_opponents.html', default_tag=os.getenv('PLAYER_TAG', '').strip())


@app.route('/api/recent_opponents', methods=['POST'])
def api_recent_opponents():
    try:
        tag = (request.json.get('player_tag') or '').strip()
        if not tag:
            return jsonify({"error": "player_tag required"}), 400
        if not tag.startswith('#'):
            tag = '#' + tag
        result = opponent_scanner.scan(tag.upper())
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in recent_opponents: {e}")
        return jsonify({"error": str(e)}), 500


# --- card synergy ----------------------------------------------------------

@app.route('/synergy')
def synergy():
    return render_template('synergy.html')


@app.route('/api/synergy', methods=['POST'])
def api_synergy():
    try:
        card = (request.json.get('card') or '').strip()
        if not card:
            return jsonify({"error": "card name required"}), 400
        result = synergy_analyzer.partners_for(card)
        if isinstance(result, dict) and "error" in result:
            return jsonify(result), 404
        return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in synergy: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
