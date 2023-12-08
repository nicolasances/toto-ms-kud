import pymongo
from config.config import Config
from kud.model.store import KudStore, KudTransaction
from kud.model.toto_transaction import TotoTransaction

class CountReconciliations: 

    def __init__(self): 
        self.config = Config()

    def do(self, request): 
        """
        This method retrieves the count of reconciliations, for a specific user
        """
        # Extract data from request
        user_email = request.args.get('user')

        print(f"Counting Reconciliation records for user [{user_email}]")

        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 
            
            db = client.kud
            
            # Instantiate the kud store
            kud_store = KudStore(db)

            # Retrieve the reconciliations
            count = kud_store.count_reconciliations(user_email)

        return {"reconciliationCount": count}