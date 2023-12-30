import tempfile
import pymongo
from pymongo.cursor import Cursor
import os
from config.config import Config
from datetime import datetime
import json
from google.cloud import storage
from bson import ObjectId

class Restore: 

    def __init__(self) -> None:
        self.config = Config()

    def restore(self, request): 
        """
        Backs up all the Kud data that needs backup
        """
        date = request.json.get("date")

        # Setup the GCS bucket
        client = storage.Client()
        bucket_name = os.environ["BACKUP_BUCKET"]
        bucket = client.bucket(bucket_name)

        print(f"Starting Kud Restore. Restoring date {date}")

        # For each collection, clear the data and restore the one in the backup file
        with pymongo.MongoClient(self.config.mongo_connection_string) as client: 

            # Get the DB
            db = client.kud
            
            # Get the list of collections
            collections_cursor = db.list_collection_names()

            # Iterate over each collection to restore the data of each collection
            for coll in collections_cursor: 

                print(f"Restoring collection [{coll}]")

                # Delete all the data in the collection
                db.get_collection(coll).delete_many({})

                # Get the GCS filename
                filename = f"{date}-{coll}.json"

                # Read the data from the file and insert it into the collection
                # Download the file
                blob = bucket.blob(f"kud/{filename}")
                
                local_temp_file = tempfile.NamedTemporaryFile()
                
                blob.download_to_filename(local_temp_file.name)

                # Read the file line by line and save the data
                with open(local_temp_file.name, 'r', newline = "\n") as file:

                    batch = []
                    count = 0

                    for line in file:

                        count += 1

                        try: 
                            doc = json.loads(line)
                            doc["_id"] = ObjectId(doc["id"])
                            doc.pop("id")

                            batch.append(doc)
                            
                        except Exception as e: 
                            print(f"Error processing line: [{line}]")
                            print(f"Resulting object: {doc}")
                            print(e)

                        if count % 100 == 0: 

                            # Insert the batch of documents
                            db.get_collection(coll).insert_many(batch)

                            # Clear the batch
                            batch = []

                            print(f"Restored {count} documents to collection {coll}")
                            
                    # Insert the remaining docs
                    db.get_collection(coll).insert_many(batch)

                    print(f"Restored {count} documents to collection {coll}")
                
                print(f"Restore of collection [{coll}] completed.")



        return {"restore": "done", "date": date}


def doc_to_json(doc: dict):
    """
    Converts a doc (dictionnary) into a json string
    """
    doc["id"] = str(doc["_id"])
    doc.pop("_id")
                
    return json.dumps(doc)

