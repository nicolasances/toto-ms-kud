from flask import Request
import pymongo
from config.config import Config
from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.ExecutionContext import ExecutionContext
from totoapicontroller.model.UserContext import UserContext
from kud.model.store import KudStore, KudTransaction
from kud.model.toto_transaction import TotoTransaction

@toto_delegate(config_class = Config)
def post_transaction_reconciliation(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """
    This method reconciles the provided kud transaction with the corresponding (provided) Toto transaction.

    To do that, it will: 
    1. Create a record that keeps the match of the two transactions. This could be used, for example, to train a model
    2. Mark the kud transaction as "reconciled" (status)
    """
    # Build the Kud Transaction from the request
    kud_transaction = KudTransaction(
        request.json.get('kudTransaction')["id"], 
        request.json.get('kudTransaction')["date"], 
        request.json.get('kudTransaction')["text"], 
        request.json.get('kudTransaction')["amount"], 
        request.json.get('kudTransaction')["user"], 
        request.json.get('kudTransaction')["yearMonth"], 
        request.json.get('kudTransaction')["kudId"]
    )

    # Build the Toto Transaction from the request
    toto_transaction = TotoTransaction(
        request.json.get('totoTransaction')["id"], 
        request.json.get('totoTransaction')["date"], 
        request.json.get('totoTransaction')["description"], 
        request.json.get('totoTransaction')["amount"], 
        request.json.get('totoTransaction')["yearMonth"]            
    )

    with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 
        
        db = client.kud
        
        # Instantiate the kud store
        kud_store = KudStore(db, cid = exec_context.cid)

        # 1. Create the reconciliation record
        kud_store.record_reconciliation(kud_transaction, toto_transaction)

    return {"inserted": True}