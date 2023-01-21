import pytest
from nostr.key import PrivateKey, mine_vanity_key


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


def test_mine_vanity_key():
    """ test vanity key mining """
    pattern = '23'

    # mine a valid pattern as prefix
    sk = mine_vanity_key(prefix=pattern)
    sk.public_key.bech32()
    assert sk.public_key.bech32().startswith(f'npub1{pattern}')

    # mine a valid pattern as suffix
    sk = mine_vanity_key(suffix=pattern)
    assert sk.public_key.bech32().endswith(pattern)

    # mine an invalid pattern
    with pytest.raises(ValueError) as e:
        mine_vanity_key(prefix='1')
