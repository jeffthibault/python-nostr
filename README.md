# python-nostr
A Python library for making [Nostr](https://github.com/nostr-protocol/nostr) clients

## Usage
**Generate a key**
```python
from nostr.key import PrivateKey

private_key = PrivateKey()
public_key = private_key.public_key
print(f"Private key: {private_key.bech32()}")
print(f"Public key: {public_key.bech32()}")
```
**Connect to relays**
```python
import json
import ssl
import time
from nostr.relay_manager import RelayManager

relay_manager = RelayManager()
relay_manager.add_relay("wss://nostr-pub.wellorder.net")
relay_manager.add_relay("wss://relay.damus.io")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
time.sleep(1.25) # allow the connections to open

while relay_manager.message_pool.has_notices():
  notice_msg = relay_manager.message_pool.get_notice()
  print(notice_msg.content)
  
relay_manager.close_connections()
```
**Publish to relays**
```python
import json 
import ssl
import time
from nostr.event import Event
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.key import PrivateKey

relay_manager = RelayManager()
relay_manager.add_relay("wss://nostr-pub.wellorder.net")
relay_manager.add_relay("wss://relay.damus.io")
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
time.sleep(1.25) # allow the connections to open

private_key = PrivateKey()

event = Event(private_key.public_key.hex(), "Hello Nostr")
event.sign(private_key.hex())

message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
relay_manager.publish_message(message)
time.sleep(1) # allow the messages to send

relay_manager.close_connections()
```
**Receive events from relays**
```python
import json
import ssl
import time
from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType

filters = Filters([Filter(authors=[<a nostr pubkey in hex>], kinds=[EventKind.TEXT_NOTE])])
subscription_id = <a string to identify a subscription>
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())

relay_manager = RelayManager()
relay_manager.add_relay("wss://nostr-pub.wellorder.net")
relay_manager.add_relay("wss://relay.damus.io")
relay_manager.add_subscription(subscription_id, filters)
relay_manager.open_connections({"cert_reqs": ssl.CERT_NONE}) # NOTE: This disables ssl certificate verification
time.sleep(1.25) # allow the connections to open

message = json.dumps(request)
relay_manager.publish_message(message)
time.sleep(1) # allow the messages to send

while relay_manager.message_pool.has_events():
  event_msg = relay_manager.message_pool.get_event()
  print(event_msg.event.content)
  
relay_manager.close_connections()
```

## Installation
1. Clone repository
```bash
git clone https://github.com/jeffthibault/python-nostr.git
```
2. Install dependencies in repo
```bash
python -m venv venv
venv/bin/python -m pip install -r requirements.txt
```

Note: If the pip install fails, you might need to install ```wheel```. Try the following:
```bash
pip install wheel
pip install -r requirements.txt
```

## Dependencies
- [websocket-client](https://github.com/websocket-client/websocket-client) for websocket operations
- [secp256k1](https://github.com/rustyrussell/secp256k1-py) for key generation, signing, and verifying
- [cryptography](https://github.com/pyca/cryptography) for encrypting and decrypting direct messages

Note: I wrote this with Python 3.9.5.

## Test Suite
See the [Test Suite README](test/README.md)

## Disclaimer
- This library is in very early development and still a WIP.
- It might have some bugs.
- I need to add more tests.
- I will try to publish this as a [PyPI](https://pypi.org/) package at some point.

Please feel free to add issues, add PRs, or provide any feedback!
