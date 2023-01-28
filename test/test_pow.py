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


def test_time_estimates():
    """ test functions to estimate POW time """
    public_key = PrivateKey().public_key.hex()

    # test successful run of all estimators
    pow.estimate_event_time('test',
                            8,
                            public_key,
                            EventKind.TEXT_NOTE)
    pow.estimate_key_time(8)
    pow.estimate_vanity_time(8)


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
    pattern = '1'
    expected_error = "not in valid list of bech32 chars"
    with pytest.raises(ValueError) as e:
        sk = mine_vanity_key(prefix=pattern)
    assert expected_error in str(e)


def test_expected_pow_times():
    """ sense check expected calculations using known patterns """
    # assume constant hashrate
    hashrate = 10000

    # calculate expected time to get a 32-difficulty bit key
    e1 = pow.expected_time(32, 2, hashrate)

    # caluclate 8 leading 0 hex key, which is equivalent
    e2 = pow.expected_time(8, 16, hashrate)
    assert e1 == e2