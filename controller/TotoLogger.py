

class TotoLogger: 
    
    def __init__(self, api_name) -> None:
        self.api_name = api_name
    
    def log(self, cid: str, msg: str) -> None: 
        """ Logs in console out a message 

        Args:
            cid (str): the Correlation Id
            msg (str): the message to be logged
        """
        print(f"[{self.api_name}] - [{cid}] - {msg}")