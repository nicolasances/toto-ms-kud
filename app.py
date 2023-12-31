from flask import Flask, request
from flask_cors import CORS
from kud.dlg.CountKudTransactions import count_kud_transactions
from kud.evt.OnGamesEvent import GamesEventHandler
from kud.dlg.GetKudTransactions import get_kud_transactions
from kud.dlg.PostTransactionReconciliation import post_transaction_reconciliation
from kud.dlg.CountReconciliations import count_reconciliations
from kud.dlg.GetReconciliations import get_reconciliations
from kud.dlg.backup.Backup import backup
from kud.dlg.backup.Restore import restore
from kud.dlg.MarkTransactionInvalid import mark_transaction_invalid

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/', methods=['GET'])
def smoke():
    return {"api": "toto-ms-kud", "running": True}

@app.route('/transactions', methods=["GET"])
def get_transactions():
    return get_kud_transactions(request)

@app.route('/transactions/invalidate', methods=["POST"])
def invalidate_tx():
    return mark_transaction_invalid(request)

@app.route('/transactions/count', methods=["GET"])
def count_transactions():
    return count_kud_transactions(request)

@app.route('/reconciliations', methods=["POST"])
def post_reconciliation(): 
    return post_transaction_reconciliation(request)

@app.route('/reconciliations/count', methods=["GET"])
def get_reconciliations_count(): 
    return count_reconciliations(request)

@app.route('/reconciliations', methods=["GET"])
def retrieve_reconciliations(): 
    return get_reconciliations(request)

@app.route('/backup', methods=["POST"])
def post_backup(): 
    return backup(request)

@app.route('/restore', methods=["POST"])
def post_restore(): 
    return restore(request)

@app.route('/events/games', methods=["POST"])
def on_game_event():
    GamesEventHandler().process_event(request)
    return {"status": "processed"}

if __name__ == '__main__':
    app.run()
