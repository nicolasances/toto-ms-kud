import base64

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

            print(f"Received message data: {message_data}")

            decoded_message = base64.b64decode(message_data).decode('utf-8')
            
            print(f"Received Pub/Sub message: {decoded_message}")
