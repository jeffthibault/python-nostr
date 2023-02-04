from nostr.event import Event, EncryptedDirectMessage
from nostr.key import PrivateKey


def test_eq_true():
    """ __eq__ should return True when PrivateKeys are equal """
    pk1 = PrivateKey()
    pk2 = PrivateKey(pk1.raw_secret)
    assert pk1 == pk2


def test_eq_false():
    """ __eq__ should return False when PrivateKeys are not equal """
    pk1 = PrivateKey()
    pk2 = PrivateKey()
    assert pk1.raw_secret != pk2.raw_secret
    assert pk1 != pk2


def test_from_nsec():
    """ PrivateKey.from_nsec should yield the source's raw_secret """
    pk1 = PrivateKey()
    pk2 = PrivateKey.from_nsec(pk1.bech32())
    assert pk1.raw_secret == pk2.raw_secret



class TestEvent:
    def setup_class(self):
        self.sender_pk = PrivateKey()
        self.sender_pubkey = self.sender_pk.public_key.hex()
    

    def test_sign_event_is_valid(self):
        """ sign should create a signature that can be verified against Event.id """
        event = Event(content="Hello, world!")
        self.sender_pk.sign_event(event)
        assert event.verify()


    def test_sign_event_adds_pubkey(self):
        """ sign should add the sender's pubkey if not already specified """
        event = Event(content="Hello, world!")

        # The event's public_key hasn't been specified yet
        assert event.public_key is None

        self.sender_pk.sign_event(event)

        # PrivateKey.sign() should have populated public_key
        assert event.public_key == self.sender_pubkey



class TestEncryptedDirectMessage:
    def setup_class(self):
        self.sender_pk = PrivateKey()
        self.sender_pubkey = self.sender_pk.public_key.hex()
        self.recipient_pk = PrivateKey()
        self.recipient_pubkey = self.recipient_pk.public_key.hex()


    def test_encrypt_dm(self):
        """ Should encrypt a DM and populate its `content` field with ciphertext that either party can decrypt """
        message = "My secret message!"

        dm = EncryptedDirectMessage(
            recipient_pubkey=self.recipient_pubkey,
            cleartext_content=message,
        )

        # DM's content field should be initially blank
        assert dm.content is None
        self.sender_pk.encrypt_dm(dm)

        # After encrypting, the content field should now be populated
        assert dm.content is not None

        # Sender should be able to decrypt
        decrypted_message = self.sender_pk.decrypt_message(encoded_message=dm.content, public_key_hex=self.recipient_pubkey)
        assert decrypted_message == message

        # Recipient should be able to decrypt by referencing the sender's pubkey
        decrypted_message = self.recipient_pk.decrypt_message(encoded_message=dm.content, public_key_hex=self.sender_pubkey)
        assert decrypted_message == message


    def test_sign_encrypts_dm(self):
        """ `sign` should encrypt a DM that hasn't been encrypted yet """
        dm = EncryptedDirectMessage(
            recipient_pubkey=self.recipient_pubkey,
            cleartext_content="Some DM message",
        )

        assert dm.content is None

        self.sender_pk.sign_event(dm)

        assert dm.content is not None
