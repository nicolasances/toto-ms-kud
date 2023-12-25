import tempfile
import pymongo
from pymongo.cursor import Cursor
import os
from config.config import Config
from datetime import datetime
import json
from google.cloud import storage

class Backup: 

    def __init__(self) -> None:
        self.config = Config()

    def backup(self): 
        """
        Backs up all the Kud data that needs backup
        """
        today = datetime.now().strftime("%Y%m%d")

        # Prepare the target file
        tmpdir = tempfile.mkdtemp()

        # Setup the GCS bucket
        client = storage.Client()
        bucket_name = os.environ["BACKUP_BUCKET"]
        bucket = client.bucket(bucket_name)

        # 1. Extract data from the kud collection and store to file
        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 

            # Get the DB
            db = client.kud
            
            # Get the list of collections
            collections_cursor = db.list_collection_names()

            # Iterate over each collection to back it up
            for coll in collections_cursor: 

                print(f"Backing up Collection [{coll}]")

                # Get all the docs in the collection
                cursor = db.get_collection(coll).find()

                # Define the filename
                filename = f"{today}-{coll}.json"

                # Write docs to file
                write_docs_to_file(cursor, os.path.join(tmpdir, filename))

                # Upload the file to GCS
                bucket_filepath = f"kud/{filename}"
        
                kud_blob = bucket.blob(bucket_filepath)

                kud_blob.upload_from_filename(os.path.join(tmpdir, filename))

        return {"ok": True}


def doc_to_json(doc: dict):
    """
    Converts a doc (dictionnary) into a json string
    """
    doc["id"] = str(doc["_id"])
    doc.pop("_id")
                
    return json.dumps(doc)

def write_docs_to_file(cursor: Cursor, filepath: str): 
    """
    Iterates over the provided cursor and saves each document to a file
    The file is written with one line for each document
    """
    # Save each doc to a file
    with open(filepath, "w") as file: 

        for doc in cursor: 

            # Convert the doc to a json string
            json_doc = doc_to_json(doc)

            file.write(f"{json_doc}\n")
