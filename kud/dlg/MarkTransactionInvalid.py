import pymongo
from config.config import Config
from kud.model.store import KudStore, KudTransaction
from kud.model.toto_transaction import TotoTransaction

class MarkTransactionInvalid: 

    def __init__(self): 
        self.config = Config()

    def do(self, request): 
        """
        This method marks a Kud Transaction as INVALID
        """
        kud_tx_id = request.json.get("kudTransactionId")

        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 
            
            db = client.kud
            
            # Instantiate the kud store
            kud_store = KudStore(db)

            # Invalidate the transaction
            kud_store.invalidate_kud_transaction(kud_tx_id)

        return {"updated": True}