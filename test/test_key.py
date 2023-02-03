import pytest
import secrets
from embit import bip39
from nostr.event import Event
from nostr.key import Bip39PrivateKey, PrivateKey



class TestPrivateKey:
    def test_eq_true(self):
        """ __eq__ should return True when PrivateKeys are equal """
        pk1 = PrivateKey()
        pk2 = PrivateKey(pk1.raw_secret)
        assert pk1 == pk2


    def test_eq_false(self):
        """ __eq__ should return False when PrivateKeys are not equal """
        pk1 = PrivateKey()
        pk2 = PrivateKey()
        assert pk1.raw_secret != pk2.raw_secret
        assert pk1 != pk2


    def test_from_nsec(self):
        """ PrivateKey.from_nsec should yield the source's raw_secret """
        pk1 = PrivateKey()
        pk2 = PrivateKey.from_nsec(pk1.bech32())
        assert pk1.raw_secret == pk2.raw_secret



class TestBip39PrivateKey:
    def test_create_random_mnemonic(self):
        """ Should create a new random BIP-39 mnemonic for each new PK """
        pk1 = Bip39PrivateKey()
        pk2 = Bip39PrivateKey()

        assert pk1.mnemonic != pk2.mnemonic
        assert pk1.raw_secret != pk2.raw_secret


    def test_rejects_invalid_mnemonic(self):
        """ Should reject mnemonics that fail checksum word verification """
        pk = Bip39PrivateKey()

        # Change the first word in the mnemonic that isn't "satoshi" to "satoshi"
        for i in range(0, 23):
            if pk.mnemonic[i] != "satoshi":
                pk.mnemonic[i] = "satoshi"
                break

        # Now if we try to load this modified mnemonic, it should fail validation
        with pytest.raises(ValueError) as e:
            Bip39PrivateKey(pk.mnemonic)
        assert "Checksum verification failed" in str(e)


    def test_24word_mnemonic_generates_pk(self):
        """ Should deterministically derive the associated Nostr PK from a 24-word BIP-39 mnemonic """
        entropy = secrets.token_bytes(32)
        mnemonic = bip39.mnemonic_from_bytes(entropy).split()
        assert len(mnemonic) == 24

        pk1 = Bip39PrivateKey(mnemonic)

        # The BIP-39 entropy to create the mnemonic is not the same as the final Nostr PK secret
        assert entropy != pk1.raw_secret

        # Nostr key derivation is deterministic; same result each time
        pk2 = Bip39PrivateKey(mnemonic)
        assert pk1.raw_secret == pk2.raw_secret


    def test_12word_mnemonic_generates_pk(self):
        """ Should deterministically derive the associated Nostr PK from a 12-word BIP-39 mnemonic """
        entropy = secrets.token_bytes(16)
        mnemonic = bip39.mnemonic_from_bytes(entropy).split()
        assert len(mnemonic) == 12

        pk1 = Bip39PrivateKey(mnemonic)

        # The BIP-39 entropy to create the mnemonic is not the same as the final Nostr PK secret
        assert entropy != pk1.raw_secret

        # Nostr key derivation is deterministic; same result each time
        pk2 = Bip39PrivateKey(mnemonic)
        assert pk1.raw_secret == pk2.raw_secret


    def test_bip39_passphrase_changes_pk(self):
        """ Should generate a different Nostr PK if an optional BIP-39 passphrase is provided """
        entropy = secrets.token_bytes(32)
        mnemonic = bip39.mnemonic_from_bytes(entropy).split()
        pk1 = Bip39PrivateKey(mnemonic)
        pk2 = Bip39PrivateKey(mnemonic, passphrase="somethingsomethingprofit!")
        pk3 = Bip39PrivateKey(mnemonic, passphrase="otherpassphrase")

        assert pk1.raw_secret != pk2.raw_secret
        assert pk2.raw_secret != pk3.raw_secret
    

    def test_with_mnemonic_length(self):
        """ Should create a new PK using a new randomly-generated mnemonic of the specified length """
        pk12 = Bip39PrivateKey.with_mnemonic_length(12)
        assert len(pk12.mnemonic) == 12

        pk24 = Bip39PrivateKey.with_mnemonic_length(24)
        assert len(pk24.mnemonic) == 24

        with pytest.raises(Exception) as e:
            Bip39PrivateKey.with_mnemonic_length(99)
        assert "12 or 24" in str(e)
    

    def test_pk_signs_event(self):
        """ Should still be able to sign Events like any other Nostr PK """
        pk = Bip39PrivateKey()
        event = Event(public_key=pk.public_key.hex(), content="Hello, world!")
        pk.sign_event(event)
        assert event.verify()
