from flask import Request
import pymongo
from config.config import Config
from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.TotoLogger import TotoLogger
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext
from kud.model.store import KudStore

@toto_delegate(config_class = Config)
def count_reconciliations(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """
    This method retrieves the count of reconciliations, for a specific user
    """
    logger: TotoLogger = exec_context.logger
    
    # Extract data 
    user_email = user_context.email
    
    tx_type = request.args.get("transactionType", "any")

    logger.log(exec_context.cid, f"Counting Reconciliation records for user [{user_email}] and transaction type [{tx_type}]")

    with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 
        
        db = client.kud
        
        # Instantiate the kud store
        kud_store = KudStore(db, cid=exec_context.cid)

        # Retrieve the reconciliations
        count = kud_store.count_reconciliations(user_email, tx_type)

    return {"reconciliationCount": count}