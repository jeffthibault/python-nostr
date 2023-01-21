from nostr.event import Event
from nostr.key import PrivateKey
import time

def test_event_default_time():
    """ensure created_at default value reflects the time
    at Event object instantiation 
    """
    public_key = PrivateKey().public_key.hex()
    event1 = Event(public_key=public_key, content='test event')
    time.sleep(1.5)
    event2 = Event(public_key=public_key, content='test event')
    assert event1.created_at != event2.created_at
