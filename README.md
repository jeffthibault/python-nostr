# python-nostr
A Python library for making [Nostr](https://github.com/nostr-protocol/nostr) clients

## Usage
**Generate a key**
```python
from nostr.key import generate_private_key, get_public_key

private_key = generate_private_key()
public_key = get_public_key(private_key)
```
**Connect to relays**
```python
from nostr.relay_manager import RelayManager

relay_manager = RelayManager()
relay_manager.add_relay("wss://nostr-pub.wellorder.net", True, True)
relay_manager.add_relay("wss://relay.damus.io", True, True)
relay_manager.open_connection()

while relay_manager.message_pool.has_notices():
  notice_msg = relay_manager.message_pool.get_notice()
  print(notice_msg.content)
```
**Publish to relays**
```python
from nostr.event import Event
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.key import generate_private_key, get_public_key

relay_manager = RelayManager()
relay_manager.add_relay("wss://nostr-pub.wellorder.net", True, True)
relay_manager.add_relay("wss://relay.damus.io", True, True)
relay_manager.open_connection()

private_key = generate_private_key()
public_key = get_public_key(private_key)

event = Event(public_key, "Hello Nostr")
event.sign(private_key)

message = json.dumps([ClientMessageType.EVENT, event.to_json_object()])
relay_manager.publish_message(message)
```
**Receive events from relays**
```python
from nostr.filter import Filter, Filters
from nostr.event import Event, EventKind
from nostr.relay_manager import RelayManager
from nostr.message_type import ClientMessageType
from nostr.key import generate_private_key, get_public_key

filters = Filters([Filter(authors=["<a nostr pubkey in hex>"], kinds=[EventKind.TEXT_NOTE])])
subscription_id = "<a string to represent subscription id>"
request = [ClientMessageType.REQUEST, subscription_id]
request.extend(filters.to_json_array())

relay_manager = RelayManager()
relay_manager.add_relay("wss://nostr-pub.wellorder.net", True, True)
relay_manager.add_relay("wss://relay.damus.io", True, True)
relay_manager.add_subscription(subscription_id, filters)
relay_manager.open_connection()

message = json.dumps(request)
relay_manager.publish_message(message)

while relay_manager.message_pool.has_events():
  event_msg = relay_manager.message_pool.get_event()
  print(event_msg.event.content)
```

## Installation
1. Clone repository \
```git clone https://github.com/jeffthibault/python-nostr.git```
2. Install dependencies in repo \
```python -m venv venv``` \
```pip install -r requirements.txt```

Note: If the pip install fails, you might need to install wheel. Try ```pip install wheel``` then ```pip install -r requirements.txt```

## Dependencies
- [websocket-client](https://github.com/websocket-client/websocket-client) for websocket operations
- [secp256k1](https://github.com/rustyrussell/secp256k1-py) for key generation, signing, and verifying
- [cryptography](https://github.com/pyca/cryptography) for encrypting and decrypting direct messages

Note: I wrote this with Python 3.9.5.

## Disclaimer
- This library is in very early development and still a WIP.
- It might have some bugs.
- I need to add tests.
- I will try to publish this as a [PyPI](https://pypi.org/) package at some point.

Please feel free to add issues, add PRs, or provide any feedback!
