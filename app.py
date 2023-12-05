from flask import Flask, jsonify, request
from flask_cors import CORS
from kud.evt.OnGamesEvent import GamesEventHandler
from config.config import Config

Config()

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/', methods=['GET'])
def smoke():
    print("GET /")
    return {"api": "toto-ms-kud", "running": True}

@app.route('/events/games', methods=["POST"])
def on_game_event():
    print("POST /events/games")
    return GamesEventHandler().process_event(request)

if __name__ == '__main__':
    app.run()