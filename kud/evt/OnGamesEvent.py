import base64
import os
import tempfile
import json

from google.cloud import storage
from kud.KudExtract import KudExtract

class GamesEventHandler:

    supported_events = ["kudUploaded"]

    def __init__(self):
        pass

    def process_event(self, request): 
        """
        Process Pub/Sub Game event
        """
        data = request.get_json()

        if "message" in data: 

            message_data = data["message"]["data"]

            print(f"Received message data: {message_data}")

            decoded_message = json.loads(base64.b64decode(message_data).decode('utf-8'))
            
            print(f"Received Pub/Sub message: {decoded_message}")

            # KUD Uploaded Event Handling
            if decoded_message["type"] == "kudUploaded": 

                # Get the data 
                bucket_name = decoded_message["data"]["gcsBucket"]
                bucket_filepath = decoded_message["data"]["gcsFilepath"]
                year = decoded_message["data"]["year"]
                month = decoded_message["data"]["month"]
                user_email = decoded_message["data"]["user"]

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
                dec_separator = '.'
                thousands_separator = ','
                if int(year) > 2020: 
                    dec_separator = ','
                    thousands_separator = '.'
                elif int(year) == 2020 and int(month) >= 9: 
                    dec_separator = ','
                    thousands_separator = '.'

                kud_extract = KudExtract(year, decimal_separator=dec_separator, thousands_separator=thousands_separator)
                kud_data = kud_extract.process_pdf(local_file_path)

                print(kud_data)