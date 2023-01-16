import json
import ssl
import time
from nostr.relay_manager import RelayManager
import logging

logging.basicConfig(level=logging.DEBUG)

relay_manager = RelayManager()
relay_manager.add_relay("")
relay_manager.add_relay("")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE})  # This disable SSL
logging.info('Connections opened')  # add more logging info
time.sleep(1.25)  # allow the connections to open

while relay_manager.message_pool.has_notices():
    notice_msg = relay_manager.message_pool.get_notice()
    print(notice_msg.content)
    logging.info(f"New message: {notice_msg.content}")  # add more to logging message

relay_manager.close_connections()
