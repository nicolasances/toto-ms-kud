import os
import tempfile
import pymongo  

from google.cloud import storage
from kud.KudExtract import KudExtract
from kud.util.kudutil import get_separators
from config.config import Config

class KudUploadedEH:

    def __init__(self): 
        pass
    
    def handle_event(self, event): 
        """
        Process Pub/Sub Game "kudUploaded" event: 
        1. Downloads the Kud PDF file stored in GCS by toto-ms-games
        2. Parse it and extract the expenses and incomes
        3. Saves the data to DB
        4. Publishes a "kudProcessed" event on the "kud" topic
        """

        # 1. Extract the data from the event
        bucket_name = event["data"]["gcsBucket"]
        bucket_filepath = event["data"]["gcsFilepath"]
        year = event["data"]["year"]
        month = event["data"]["month"]
        user_email = event["data"]["user"]

        client = storage.Client()

        # 1. Download the file from GCS bucket
        filename = f"kud-{year}.{month}.pdf"
        tmpdir = tempfile.mkdtemp()

        print(f"Downloading Kud file to dir [{tmpdir}] with filename [{filename}]")

        bucket = client.bucket(bucket_name)

        local_file_path = os.path.join(tmpdir, filename)

        blob = bucket.blob(bucket_filepath)
        blob.download_to_filename(local_file_path)

        # 2. Trigger the Kud Extract
        dec_separator, thousands_separator = get_separators(year, month)

        kud_extract = KudExtract(year, decimal_separator=dec_separator, thousands_separator=thousands_separator)
        kud_data = kud_extract.process_pdf(local_file_path)

        # 3. Save data to DB
        config = Config()
        client = config.mongo_client
        db = client.kud

        db.kud.insert_many(kud_data)
