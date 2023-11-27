
class GamesEventHandler:

    def __init__(self):
        pass

    def process_event(self, request): 
        """
        Process Pub/Sub Game event
        """
        data = request.get_json()

        if "message" in data: 
            message_data = data["message"]["data"]
            decoded_message = message_data.decode("base64")
            
            print(f"Received Pub/Sub message: {decoded_message}")
