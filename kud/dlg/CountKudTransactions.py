
import pymongo
from config.config import Config
from kud.model.store import KudStore

class CountKudTransactions: 

    def __init__(self): 
        self.config = Config()

    def do(self, request): 
        """
        This method counts the number of Kud Transactions available for the user

        Paramters
        - request.args.user should countain the user email
        """
        # Extract core data from the request
        user_email = request.args.get('user')

        # Get the data from the store
        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 

            db = client.kud
            
            # Instantiate the store
            kud_store = KudStore(db)

            # Count the Kud Transactions
            count = kud_store.count_transactions(user_email)

        return {
            "count": count
        }

