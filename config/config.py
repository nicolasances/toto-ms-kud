import os 
import pymongo

from google.cloud import secretmanager
from config.util.singleton import singleton
from controller.TotoLogger import TotoLogger


@singleton
class Config: 
    """
    Configuration Class, responsible to load the configurations for this microservice
    """
    api_name: str
    mongo_user: str
    mongo_pswd: str
    mongo_host: str 
    jwt_key: str

    def __init__(self): 
        
        self.api_name = "toto-ms-kud"
        
        logger = TotoLogger(self.api_name)
        
        logger.log("INIT", "Loading Configuration..")

        self.mongo_user = access_secret_version("toto-ms-kud-mongo-user")
        self.mongo_pswd = access_secret_version("toto-ms-kud-mongo-pswd")
        self.mongo_host = access_secret_version("mongo-host")
        self.jwt_key = access_secret_version("jwt-signing-key")
        
        self.mongo_connection_string = f"mongodb://{self.mongo_user}:{self.mongo_pswd}@{self.mongo_host}:27017"

        logger.log("INIT", "Configuration loaded.")



def access_secret_version(secret_id, version_id="latest"):
    """
    Retrieves a Secret on GCP Secret Manager
    """

    project_id = os.environ["GCP_PID"]

    # Create the Secret Manager client
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version
    response = client.access_secret_version(name=name)

    # Extract the secret payload
    payload = response.payload.data.decode("UTF-8")

    return payload
