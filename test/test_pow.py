import pytest
from nostr.key import PrivateKey
from nostr.event import EventKind
from nostr import pow
from nostr.pow import mine_event, mine_key, mine_vanity_key

def test_mine_event():
    """ test mining an event with specific difficulty """
    public_key = PrivateKey().public_key.hex()
    difficulty = 8
    event = mine_event(content='test',difficulty=difficulty,
                       public_key=public_key, kind=EventKind.TEXT_NOTE)
    assert pow.count_leading_zero_bits(event.id) >= difficulty


def test_mine_key():
    """ test mining a public key with specific difficulty """
    difficulty = 8
    sk = mine_key(difficulty)
    assert pow.count_leading_zero_bits(sk.public_key.hex()) >= difficulty


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
