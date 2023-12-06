from flask import Flask, jsonify, request
from flask_cors import CORS
from kud.evt.OnGamesEvent import GamesEventHandler
from kud.dlg.GetKudTransactions import GetKudTransactions
from kud.dlg.PostTransactionReconciliation import PostTransactionReconciliation

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/', methods=['GET'])
def smoke():
    print("GET /")
    return {"api": "toto-ms-kud", "running": True}

@app.route('/events/games', methods=["POST"])
def on_game_event():
    print("POST /events/games")
    GamesEventHandler().process_event(request)
    return {"status": "processed"}

@app.route('/transactions', methods=["GET"])
def get_transactions():
    print("GET /transactions")
    return GetKudTransactions().do(request)

@app.route('/reconciliations', methods=["POST"])
def post_reconciliation(): 
    print("POST /reconciliations")
    return PostTransactionReconciliation().do(request)


if __name__ == '__main__':
    app.run()
