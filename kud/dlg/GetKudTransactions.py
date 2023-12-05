
import pymongo
from config.config import Config
from kud.model.kudmodel import KudStore

class GetKudTransactions: 

    def __init__(self): 
        self.config = Config()

    def do(self, request): 

        # Extract core data from the request
        user_email = request.args.get('user')
        only_payments = request.args.get('paymentsOnly', False)
        max_results = int(request.args.get('maxResults', 0))

        # Get the data from the store
        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 
            db = client.kud
            kud_store = KudStore(db)

            payments = kud_store.get_transactions(user_email, payments_only=only_payments, max_results=max_results, non_processed_only=True)

        return {
            "payments": payments
        }

