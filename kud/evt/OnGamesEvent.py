import base64
import json

from kud.evt.handlers.KudUploadedEH import KudUploadedEH

class GamesEventHandler:

    supported_events = ["kudUploaded"]

    def __init__(self):
        pass

    def process_event(self, request): 
        
        data = request.get_json()

        if "message" in data: 

            message_data = data["message"]["data"]

            print(f"Received message data: {message_data}")

            decoded_message = json.loads(base64.b64decode(message_data).decode('utf-8'))
            
            print(f"Received Pub/Sub message: {decoded_message}")

            # KUD Uploaded Event Handling
            if decoded_message["type"] == "kudUploaded": 

               KudUploadedEH().handle_event(decoded_message)