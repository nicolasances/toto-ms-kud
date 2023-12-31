
from flask import Request
import pymongo
from config.config import Config
from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.TotoLogger import TotoLogger
from totoapicontroller.model.ExecutionContext import ExecutionContext
from totoapicontroller.model.UserContext import UserContext
from kud.model.store import KudStore

@toto_delegate(config_class = Config)
def get_kud_transactions(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    logger: TotoLogger = exec_context.logger

    # Extract core data from the request
    user_email = user_context.email
    
    only_payments = request.args.get('paymentsOnly', False)
    max_results = int(request.args.get('maxResults', 0))
    
    logger.log(exec_context.cid, f"Extracting Kud Transactions for user [{user_email}] with parameters [Payments Only: {only_payments}, Max Results: {max_results}]")

    # Get the data from the store
    with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 
        
        db = client.kud
        kud_store = KudStore(db, cid=exec_context.cid)

        payments = kud_store.get_transactions(user_email, payments_only=only_payments, max_results=max_results, non_processed_only=True)

    return {
        "payments": payments
    }

