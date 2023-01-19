from nostr.event import Event
from nostr.key import PrivateKey
import time

def test_event_default_time():
    time.sleep(1.5)
    public_key = PrivateKey().public_key.hex()
    event = Event(public_key=public_key, content='test event')
    assert (event.created_at - time.time()) < 1
