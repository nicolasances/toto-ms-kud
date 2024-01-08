
from flask import Request
import pymongo
from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.ExecutionContext import ExecutionContext
from totoapicontroller.model.UserContext import UserContext
from config.config import Config
from kud.model.store import KudStore

@toto_delegate(config_class = Config)
def count_kud_transactions(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """
    This method counts the number of Kud Transactions available for the user
    """
    config = exec_context.config
    
    # Extract core data 
    user_email = user_context.email

    # Get the data from the store
    with pymongo.MongoClient(config.mongo_connection_string) as client: 

        db = client.kud
        
        # Instantiate the store
        kud_store = KudStore(db, cid=exec_context.cid)

        # Count the Kud Transactions
        count = kud_store.count_transactions(user_email)

    return {
        "count": count
    }

