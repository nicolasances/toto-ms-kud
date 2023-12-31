from flask import Request
import pymongo
from config.config import Config
from controller.TotoDelegateDecorator import toto_delegate
from controller.model.ExecutionContext import ExecutionContext
from controller.model.UserContext import UserContext
from kud.model.store import KudStore

@toto_delegate
def mark_transaction_invalid(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """
    This method marks a Kud Transaction as INVALID
    """
    kud_tx_id = request.json.get("kudTransactionId")

    with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 
        
        db = client.kud
        
        # Instantiate the kud store
        kud_store = KudStore(db, cid = exec_context.cid)

        # Invalidate the transaction
        kud_store.invalidate_kud_transaction(kud_tx_id)

    return {"updated": True}