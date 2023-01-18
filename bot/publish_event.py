import json
import ssl
import time
from nostr.event import Event
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.key import PrivateKey

import logging

logging.basicConfig(level=logging.INFO)


def publish():
    relay_manager = RelayManager()
    relay_manager.add_relay("wss://nostr.zebedee.cloud")
    relay_manager.add_relay("wss://nostr.bitcoiner.social")
    relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})  # NOTE: This disables ssl certificate verification
    logging.info(f"Connections opened: ")  # add more logging info
    time.sleep(1.25)  # allow the connections to open

    private_key = PrivateKey()

    event = Event(private_key.public_key.hex(), "Hello Nostr")
    event.sign(private_key.hex())
    logging.info(f"Event singed: {event}")  # add more logging info

    message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
    relay_manager.publish_message(message)
    logging.info(f"Message published: {message}")  # add more logging info
    time.sleep(1)  # allow the messages to send

    relay_manager.close_connections()
    logging.info("Connections Closed..")


if __name__ == "__main__":
    key()
    publish()
