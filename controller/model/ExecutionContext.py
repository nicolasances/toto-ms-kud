
from config.config import Config
from controller import TotoLogger


class ExecutionContext: 
    
    logger: TotoLogger
    cid: str 
    config: Config
    
    def __init__(self, config: Config, logger: TotoLogger, cid: str) -> None:
        self.config = config
        self.logger = logger
        self.cid = cid