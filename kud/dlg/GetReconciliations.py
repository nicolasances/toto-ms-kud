import pymongo
from config.config import Config
from kud.model.store import KudStore, KudTransaction
from kud.model.toto_transaction import TotoTransaction

class GetReconciliations: 

    def __init__(self): 
        self.config = Config()

    def do(self, request): 
        """
        This method retrieves the list of reconciliations, for a specific user and yearMonth
        """
        # Extract data from request
        user_email = request.args.get('user')
        year_month = request.args.get('yearMonth')

        print(f"Retrieving Reconciliation records for user [{user_email}] and yearMonth [{year_month}]")

        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 
            
            db = client.kud
            
            # Instantiate the kud store
            kud_store = KudStore(db)

            # Retrieve the reconciliations
            reconciliations = kud_store.get_reconciliations(user_email, year_month)

        return {"reconciliations": reconciliations}