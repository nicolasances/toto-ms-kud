
from flask import Request
import pymongo
from config.config import Config
from controller.TotoAPIController import TotoDelegate
from controller.model.ExecutionContext import ExecutionContext
from controller.model.UserContext import UserContext
from kud.model.store import KudStore

class CountKudTransactions(TotoDelegate): 

    def do(self, request: Request, user_context: UserContext, exec_context: ExecutionContext): 
        """
        This method counts the number of Kud Transactions available for the user
        """
        # Extract core data 
        user_email = user_context.email

        # Get the data from the store
        with pymongo.MongoClient(exec_context.config.mongo_connection_string) as client: 

            db = client.kud
            
            # Instantiate the store
            kud_store = KudStore(db)

            # Count the Kud Transactions
            count = kud_store.count_transactions(user_email)

        return {
            "count": count
        }

