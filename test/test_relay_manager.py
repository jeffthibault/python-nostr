import pytest
from nostr.event import Event
from nostr.key import PrivateKey
from nostr.relay_manager import RelayManager, RelayException


def test_only_relay_valid_events():
    """ publish_event raise a RelayException if an Event fails verification """
    pk = PrivateKey()
    event = Event(
        public_key=pk.public_key.hex(),
        content="Hello, world!",
    )
    
    relay_manager = RelayManager()

    # Deliberately forget to sign the Event
    with pytest.raises(RelayException) as e:
        relay_manager.publish_event(event)
    assert "must be signed" in str(e)

    # Attempt to relay with a nonsense signature
    event.signature = '0' * 32
    with pytest.raises(RelayException) as e:
        relay_manager.publish_event(event)
    assert "failed to verify" in str(e)

    # Properly signed Event can be relayed
    pk.sign_event(event)
    relay_manager.publish_event(event)
