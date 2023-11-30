import os
import json
from google.cloud import pubsub_v1
from datetime import datetime
from enum import Enum
    
class KudEvent(Enum): 
    kud_processed = "kudProcessed"

class KudEventPublisher:

    def __init__(self) -> None:
        pass

    def publish_event(self, cid: str, id: str, event_type: KudEvent, msg: str, data: dict): 

        # GCP Project Id
        project_id = os.environ["GCP_PID"]
        
        # Topic to which to publish
        topic_id = "kuds"

        # Create a Pub/Sub publisher client
        publisher = pubsub_v1.PublisherClient()

        # Create the full topic path
        topic_path = f"projects/{project_id}/topics/{topic_id}"

        # Define the message payload
        message_data = {
            "timestamp": datetime.now().strftime("%Y.%m.%d %H:%M:%S"),
            "cid": cid,
            "id": id,
            "type": event_type.value,
            "msg": msg,
            "data": data
        }

        print(f"About to publish event {event_type.value} with data {json.dumps(message_data)} on Pub/Sub")

        # Encode the message
        message_bytes = json.dumps(message_data).encode("utf-8")

        # Publish the message to the topic
        future = publisher.publish(topic_path, data=message_bytes)

        if future.exception():
            exception_message = f"Error publishing message: {future.exception()}"
            print(exception_message)

        # Future is async: wait for it to finish
        publishing_result = future.result()

        print(f"Event {event_type.value} published on Pub/Sub")

        return publishing_result
