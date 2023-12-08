from datetime import datetime
from config.config import Config
from kud.model.toto_transaction import TotoTransaction
from bson import ObjectId

F_DATE = "date"
F_TEXT = "text"
F_AMOUNT = "amount"
F_USER = "user"
F_YEAR_MONTH = "yearMonth"
F_KUD_ID = "kudId"
F_KUD_FILEPATH = "kudFilepath"
F_STATUS = "status"                     # The status defines if items have been "reconciled", set as "invalid" or haven't been looked at yet (status is null)

class KudStatus: 
    RECONCILED = "reconciled"
    INVALID = "invalid"
    

class KudTransaction: 
    
    id: str
    date: str
    amount: float
    text: str
    year_month: str
    user: str
    kud_id: str

    def __init__(self, id, date, text, amount, user, year_month, kud_id):
        self.id = id
        self.date = date
        self.amount = amount
        self.text = text
        self.year_month = year_month
        self.user = user
        self.kud_id = kud_id

# These fields are for the Reconciliation collection
RF_KUD_TX_ID = "kudTxId"                # The transaction Id of the Kud
RF_KUD_TX_DATE = "kudTxDate"            # The date as YYYYMMDD
RF_KUD_TX_AMOUNT = "kudTxAmount"        # The amount 
RF_KUD_TX_TEXT = "kudTxText"
RF_KUD_TX_YEARMONTH = "kudTxYearMonth"
RF_KUD_ID = "kudId"
RF_USER = "user"
RF_TOTO_TX_ID = "totoTxId"
RF_TOTO_TX_DATE = "totoTxDate"
RF_TOTO_TX_TEXT = "totoTxText"
RF_TOTO_TX_AMOUNT = "totoTxAmount"
RF_TOTO_TX_YEARMONTH = "totoTxYearMonth"

COLL_RECONCILIATIONS = "reconciliations"
COLL_KUD = "kud"

class KudStore: 

    def __init__(self, db): 
        self.db = db

    def save_kud_data(self, kud_items, user_email, kud_gcs_filepath, year, month):
        """
        Creates an insert for a list of PO for the provided list of kud expenses and incomes

        Parameters: 
        - kud_items (list): a list of kud items (expenses or incomes)
        - user_email (str): the email of the user that owns the account
        - kud_gcs_filepath (str): the filepath in the GCS bucket where this file will be stored permanently. 
        Note that this is not the "Games" GCS bucket but the KUD GCS bucket
        - year (str): the year of this kud
        - month (str): the last month covered by the kud
        """
        pos = []

        kud_id = self.build_kud_id(year, month)

        for item in kud_items: 
            po = {}
            po[F_DATE] = datetime.strptime(item["date"], "%d.%m.%Y").strftime("%Y%m%d")
            po[F_TEXT] = item["text"]
            po[F_AMOUNT] = item["amount"]
            po[F_USER] = user_email
            po[F_YEAR_MONTH] = datetime.strptime(item["date"], "%d.%m.%Y").strftime("%Y%m")
            po[F_KUD_FILEPATH] = kud_gcs_filepath
            po[F_KUD_ID] = kud_id

            pos.append(po)

        self.db.kud.insert_many(pos)

        print(f"Inserted [{len(pos)}] Kud items for Kud Id [{kud_id}]")

        return {'n_inserted': len(pos)}

    
    def delete_kud_data(self, kud_id):
        """
        Deletes all the items of a specific kud (identified by the kud id)

        Parameters: 
        - kud_id (str): the id of the kud for which all data needs to be deleted
        Kud Ids have the format "kud-YEARMONTH". 
        An example is "kud-202311
        """
        delete_filter = {}
        delete_filter[F_KUD_ID] = kud_id

        delete_result = self.db.kud.delete_many(delete_filter)

        print(f"Deleted [{delete_result.deleted_count}] items with Kud Id [{kud_id}]")

    def build_kud_id(self, year, month): 
        """
        Utility method to build a Kud Id based on a year and month
        """
        return f"kud-{year}-{month}"
    
    def get_transactions(self, user_email, payments_only = False, max_results = None, non_processed_only = False): 
        """
        This method retrieves the transactions from the database

        Parameters
        - user_email (str): the user email
        - payments_only (bool): default False, pass True if you want to filter only payments (leaving incomes aside)
        - max_results (int): default None (unlimited), pass a number if you want to limit the number of returned results 
        - non_processed_only (bool): default False, pass True if you only want to extract transactions that have not been processed

        Returns: 
        - list: a list of transactions
        """

        query = {}
        query[F_USER] = user_email
        
        # If the user only wants payments
        if payments_only: 
            query[F_AMOUNT] = {"$lt": 0}

        # If the user only wants "non processed" items
        if non_processed_only: 
            null_filter = {}
            null_filter[F_STATUS] = {"$eq": None}

            exist_filter = {}
            exist_filter[F_STATUS] = {"$exists": False}

            query["$or"] = [null_filter, exist_filter]

        # Run the query
        cursor = self.db.kud.find(query).limit(max_results)

        # Return the data
        docs = []

        for doc in cursor: 
            to = {}
            to["id"] = str(doc["_id"])
            to[F_DATE] = doc[F_DATE]
            to[F_TEXT] = doc[F_TEXT]
            to[F_AMOUNT] = doc[F_AMOUNT]
            to[F_USER] = doc[F_USER]
            to[F_YEAR_MONTH] = doc[F_YEAR_MONTH]
            to[F_KUD_ID] = doc[F_KUD_ID]

            docs.append(to)

        return docs
    
    def record_reconciliation(self, kud_transaction: KudTransaction, toto_transaction: TotoTransaction):
        """
        Records a reconciliation (made by a user) between a given Kud Transaction and 
        a corresponding Toto Transaction.

        This is done in a specific collection that will only track the reconciliations.

        This method also updates the kud transaction, setting its status to reconciled
        """
        # Delete any previous reconciliation of the specified Kud Transaction
        # Define the filter for the delete
        del_filter = {}
        del_filter[RF_KUD_TX_ID] = kud_transaction.id

        # Delete all reconciliations for that Kud Transaction Id
        print(f"Deleting any existing reconciliation entry for Kud Transaction Id [{kud_transaction.id}]")

        self.db[COLL_RECONCILIATIONS].delete_many(del_filter)

        ## Create the new reconciliation
        recon = {}
        recon[RF_KUD_ID] = kud_transaction.kud_id
        recon[RF_KUD_TX_AMOUNT] = kud_transaction.amount
        recon[RF_KUD_TX_DATE] = str(kud_transaction.date)
        recon[RF_KUD_TX_ID] = kud_transaction.id
        recon[RF_KUD_TX_TEXT] = kud_transaction.text
        recon[RF_KUD_TX_YEARMONTH] = kud_transaction.year_month
        recon[RF_TOTO_TX_AMOUNT] = toto_transaction.amount
        recon[RF_TOTO_TX_DATE] = str(toto_transaction.date)
        recon[RF_TOTO_TX_ID] = toto_transaction.id
        recon[RF_TOTO_TX_TEXT] = toto_transaction.description
        recon[RF_TOTO_TX_YEARMONTH] = toto_transaction.year_month
        recon[RF_USER] = kud_transaction.user

        print(f"Saving new reconciliation record: {recon}")

        # Insert the reconciliation
        self.db[COLL_RECONCILIATIONS].insert_one(recon)

        # Update the Kud transaction and set its state to "reconciled"
        print(f"Setting Kud Transaction [{kud_transaction.id}] as [{KudStatus.RECONCILED}]")
        
        self.db[COLL_KUD].update_one({"_id": ObjectId(kud_transaction.id)}, {"$set": {F_STATUS: KudStatus.RECONCILED}})

    def count_reconciliations(self, user_email: str): 
        """
        Retrieves the count of reconciliation records for the specified user. 

        Parameters 
        - user_email (str): the user email

        Returns:
        - int: the count of reconciliation records
        """
        return self.db[COLL_RECONCILIATIONS].count_documents({RF_USER: user_email})
        

