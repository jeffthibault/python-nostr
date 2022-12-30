from nostr.key import PrivateKey, PublicKey


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

def test_from_npub():
    """ PublicKey.from_npub should yield the source's raw_bytes """
    pk1 = PrivateKey()
    pk2 = PublicKey.from_npub(pk1.public_key.bech32())
    assert pk1.public_key.raw_bytes == pk2.raw_bytes
