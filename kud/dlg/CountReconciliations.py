from flask import Request
import pymongo
from config.config import Config
from controller.TotoDelegateDecorator import toto_delegate
from controller.TotoLogger import TotoLogger
from controller.model.UserContext import UserContext
from controller.model.ExecutionContext import ExecutionContext
from kud.model.store import KudStore

@toto_delegate
def count_reconciliations(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """
    This method retrieves the count of reconciliations, for a specific user
    """
    logger: TotoLogger = exec_context.logger
    
    # Extract data 
    user_email = user_context.email

    logger.log(exec_context.cid, f"Counting Reconciliation records for user [{user_email}]")

    with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 
        
        db = client.kud
        
        # Instantiate the kud store
        kud_store = KudStore(db, cid=exec_context.cid)

        # Retrieve the reconciliations
        count = kud_store.count_reconciliations(user_email)

    return {"reconciliationCount": count}