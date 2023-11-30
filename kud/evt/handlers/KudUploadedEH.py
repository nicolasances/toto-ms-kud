import os
import tempfile
import pymongo

from google.cloud import storage
from kud.KudExtract import KudExtract
from kud.util.kudutil import get_separators
from config.config import Config
from kud.model.kudmodel import KudStore
from kud.evt.publisher.KudEventPublisher import KudEventPublisher, KudEvent

class KudUploadedEH:

    def __init__(self): 
        self.config = Config()
    
    def handle_event(self, event): 
        """
        Process Pub/Sub Game "kudUploaded" event: 
        1. Downloads the Kud PDF file stored in GCS by toto-ms-games
        2. Parse it and extract the expenses and incomes
        3. Saves the data to DB
        4. Publishes a "kudProcessed" event on the "kud" topic
        """

        data = event["data"]

        # 1. Extract the data from the event
        bucket_name = data["gcsBucket"]
        bucket_filepath = data["gcsFilepath"]
        year = data["year"]
        month = data["month"]
        user_email = data["user"]

        # 2. Download the file from GCS bucket and store it locally
        local_filepath = download_kud(year, month, bucket_name, bucket_filepath)

        # 3. Trigger the Kud Extract
        dec_separator, thousands_separator = get_separators(year, month)

        kud_extract = KudExtract(year, decimal_separator=dec_separator, thousands_separator=thousands_separator)
        
        kud_data = kud_extract.process_pdf(local_filepath)

        # 4. Save to Kud GCS Bucket
        client = storage.Client()
        
        kud_bucket_name = os.environ["KUD_BUCKET"]
        kud_bucket_filepath = f"kuds/{user_email}/kud-{year}.{month}.pdf"

        kud_bucket = client.bucket(kud_bucket_name)
        
        kud_blob = kud_bucket.blob(kud_bucket_filepath)

        kud_blob.upload_from_filename(local_filepath)

        # 5. Save data to DB
        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 
            db = client.kud
            kud_store = KudStore(db)
            kud_id = kud_store.build_kud_id(year, month)

            # 5.1. Delete all rows that have 
            kud_store.delete_kud_data(kud_id)

            # 5.1 Convert to POs
            save_result = kud_store.save_kud_data(kud_data, user_email, kud_bucket_filepath, year, month)

        # 6. Publish the event on Pub Sub
        KudEventPublisher().publish_event(None, kud_id, KudEvent.kud_processed, f"Kud [{kud_id}] successfully processed", {'userEmail': user_email, 'year': year, 'month': month, 'kudId': kud_id, 'nElements': save_result["n_inserted"]})

        return {'msg': f"Kud [{kud_id}] processed", 'items': save_result["n_inserted"]}


def download_kud(year, month, bucket_name, bucket_filepath): 
    """
    Downloads the Kud from the GCS bucket where it was stored

    Parameters:
    - year (str): year of the Kud doc
    - month (str): last month covered by the Kud doc (e.g. 03 for March)
    - bucket_name: name of the GCS bucket where the Kud is stored
    - bucket_filepath: filepath in the GCS bucket where the kud is stored

    Returns: 
    - (str) the filepath where the downloaded kud can be read, in the local FS
    """
    client = storage.Client()
    
    filename = f"kud-{year}.{month}.pdf"
    tmpdir = tempfile.mkdtemp()

    print(f"Downloading Kud file to dir [{tmpdir}] with filename [{filename}]")

    bucket = client.bucket(bucket_name)

    local_file_path = os.path.join(tmpdir, filename)

    blob = bucket.blob(bucket_filepath)
    blob.download_to_filename(local_file_path)

    return local_file_path
