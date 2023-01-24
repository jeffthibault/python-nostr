import pytest
import time
from nostr.event import Event, EncryptedDirectMessage
from nostr.key import PrivateKey



class TestEvent:
    def test_event_default_time(self):
        """
            ensure created_at default value reflects the time at Event object instantiation
            see: https://github.com/jeffthibault/python-nostr/issues/23
        """
        public_key = PrivateKey().public_key.hex()
        event1 = Event(public_key=public_key, content='test event')
        time.sleep(1.5)
        event2 = Event(public_key=public_key, content='test event')
        assert event1.created_at < event2.created_at



class TestEncryptedDirectMessage:
    def setup_class(self):
        self.sender_pk = PrivateKey()
        self.sender_pubkey = self.sender_pk.public_key.hex()
        self.recipient_pk = PrivateKey()
        self.recipient_pubkey = self.recipient_pk.public_key.hex()


    def test_content_field_not_allowed(self):
        """ Should not let users instantiate a new DM with `content` field data """
        with pytest.raises(Exception) as e:
            EncryptedDirectMessage(recipient_pubkey=self.recipient_pubkey, content="My message!")
        
        assert "cannot use" in str(e)
    

    def test_recipient_p_tag(self):
        """ Should generate recipient 'p' tag """
        dm = EncryptedDirectMessage(
            recipient_pubkey=self.recipient_pubkey,
            cleartext_content="Secret message!"
        )
        assert ['p', self.recipient_pubkey] in dm.tags
