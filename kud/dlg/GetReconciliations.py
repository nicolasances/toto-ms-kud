from flask import Request
import pymongo
from controller.TotoDelegateDecorator import toto_delegate
from controller.TotoLogger import TotoLogger
from controller.model.ExecutionContext import ExecutionContext
from controller.model.UserContext import UserContext
from kud.model.store import KudStore

@toto_delegate
def get_reconciliations(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """
    This method retrieves the list of reconciliations, for a specific user and yearMonth
    """
    logger: TotoLogger = exec_context.logger
    
    # Extract data 
    user_email = user_context.email
    year_month = request.args.get('yearMonth')

    logger.log(exec_context.cid, f"Retrieving Reconciliation records for user [{user_email}] and yearMonth [{year_month}]")

    with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 
        
        db = client.kud
        
        # Instantiate the kud store
        kud_store = KudStore(db, cid = exec_context.cid)

        # Retrieve the reconciliations
        reconciliations = kud_store.get_reconciliations(user_email, year_month)

    return {"reconciliations": reconciliations}