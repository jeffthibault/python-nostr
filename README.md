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

relay_manager.publish_event(event)
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

**NIP-26 delegation**
```python
from nostr.delegation import Delegation
from nostr.event import EventKind, Event
from nostr.key import PrivateKey

# Load your "identity" PK that you'd like to keep safely offline
identity_pk = PrivateKey.from_nsec("nsec1...")

# Create a new, disposable PK as the "delegatee" that can be "hot" in a Nostr client
delegatee_pk = PrivateKey()

# the "identity" PK will authorize "delegatee" to sign TEXT_NOTEs on its behalf for the next month
delegation = Delegation(
    delegator_pubkey=identity_pk.public_key.hex(),
    delegatee_pubkey=delegatee_pk.public_key.hex(),
    event_kind=EventKind.TEXT_NOTE,
    duration_secs=30*24*60*60
)

identity_pk.sign_delegation(delegation)

event = Event(
    delegatee_pk.public_key.hex(),
    "Hello, NIP-26!",
    tags=[delegation.get_tag()],
)
event.sign(delegatee_pk.hex())

# ...normal broadcast steps...
```

The resulting delegation tag can be stored as plaintext and reused as-is by the "delegatee" PK until the delegation token expires. There is no way to revoke a signed delegation, so current best practice is to keep the expiration time relatively short.

Hopefully clients will include an optional field to store the delegation tag. That would allow the "delegatee" PK to seamlessly post messages on the "identity" key's behalf, while the "identity" key stays safely offline in cold storage.


## Installation
```bash
pip install nostr
```

Note: I wrote this with Python 3.9.5.

## Test Suite
See the [Test Suite README](test/README.md)

## Disclaimer
- This library is in very early development.
- It might have some bugs.
- I need to add more tests.

Please feel free to add issues, add PRs, or provide any feedback!
