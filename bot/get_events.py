import json
import ssl
import time
from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
import logging

logging.basicConfig(level=logging.DEBUG)


filters = Filters([Filter(authors=[ < a nostr pubkey in hex >], kinds=[EventKind.TEXT_NOTE])])
subscription_id = <a string to identify a subscription >
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())

relay_manager = RelayManager()
relay_manager.add_relay("")
relay_manager.add_relay("")
relay_manager.add_subscription(subscription_id, filters)
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})  # NOTE: This disables ssl certificate verification
logging.info(f"Connections opened: ")  # add more logging info
time.sleep(1.25)  # allow the connections to open

message = json.dumps(request)
relay_manager.publish_message(message)
logging.info(f"Messages published: {message}")  # add more logging info
time.sleep(1)  # allow the messages to send

while relay_manager.message_pool.has_events():
    event_msg = relay_manager.message_pool.get_event()
    print(event_msg.event.content)

relay_manager.close_connections()