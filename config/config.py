import os 

from google.cloud import secretmanager
from totoapicontroller.model.singleton import singleton
from totoapicontroller.TotoLogger import TotoLogger
from totoapicontroller.model.TotoConfig import TotoConfig

@singleton
class Config(TotoConfig): 
    """
    Configuration Class, responsible to load the configurations for this microservice
    """
    mongo_user: str
    mongo_pswd: str
    mongo_host: str 

    def __init__(self) -> None:
        super().__init__()
        
        self.mongo_user = self.access_secret_version("toto-ms-kud-mongo-user")
        self.mongo_pswd = self.access_secret_version("toto-ms-kud-mongo-pswd")
        self.mongo_host = self.access_secret_version("mongo-host")
        
        self.mongo_connection_string = f"mongodb://{self.mongo_user}:{self.mongo_pswd}@{self.mongo_host}:27017"

        self.logger.log("INIT", "Configuration loaded.")

    def get_api_name(self) -> str:
        return "toto-ms-kud"