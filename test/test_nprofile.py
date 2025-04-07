import pytest
import time

from nostr.bech32 import nprofile_encode, nprofile_decode
from nostr.key import PrivateKey


class TestNProfile:
    def setup_class(self):
        self.pubkey_hex = PrivateKey().public_key.hex()
        self.relays = [
            'wss://relay.example.com',
            'wss://nostr.banana.com',
        ]

    def test_encode_decode_nprofile(self):
        nprofile_string = nprofile_encode(self.pubkey_hex, self.relays)
        pubkey_hex, relays = nprofile_decode(nprofile_string)
        assert pubkey_hex == self.pubkey_hex
        assert relays == self.relays
