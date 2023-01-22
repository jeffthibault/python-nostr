import time
from .event import Event
from .key import PrivateKey

def zero_bits(b: int) -> int:
    n = 0

    if b == 0:
        return 8

    while b >> 1:
        b = b >> 1
        n += 1

    return 7 - n

def count_leading_zero_bits(hex_str: str) -> int:
    total = 0
    for i in range(0, len(hex_str) - 2, 2):
        bits = zero_bits(int(hex_str[i:i+2], 16))
        total += bits

        if bits != 8:
            break

    return total

def mine_event(content: str, difficulty: int, public_key: str, kind: int, tags: list=[]) -> Event:
    all_tags = [["nonce", "1", str(difficulty)]]
    all_tags.extend(tags)

    created_at = int(time.time())
    event_id = Event.compute_id(public_key, created_at, kind, all_tags, content)
    num_leading_zero_bits = count_leading_zero_bits(event_id)

    attempts = 1
    while num_leading_zero_bits < difficulty:
        attempts += 1
        all_tags[0][1] = str(attempts)
        created_at = int(time.time())
        event_id = Event.compute_id(public_key, created_at, kind, all_tags, content)
        num_leading_zero_bits = count_leading_zero_bits(event_id)

    return Event(public_key, content, created_at, kind, all_tags, event_id)

def mine_key(difficulty: int) -> PrivateKey:
    sk = PrivateKey()
    num_leading_zero_bits = count_leading_zero_bits(sk.public_key.hex())

    while num_leading_zero_bits < difficulty:
        sk = PrivateKey()
        num_leading_zero_bits = count_leading_zero_bits(sk.public_key.hex())

    return sk


def mine_vanity_key(prefix: str = None, suffix: str = None) -> PrivateKey:
    if prefix is None and suffix is None:
        raise ValueError("Expected at least one of 'prefix' or 'suffix' arguments")

    bech32_chars = '023456789acdefghjklmnpqrstuvwxyz'
    for pattern in [prefix, suffix]:
        if pattern is not None:
            missing_chars = [c for c in pattern if c not in bech32_chars]
            if len(missing_chars):
                raise ValueError(
                    f'{missing_chars} are not valid characters'
                    f'for a bech32 key. Valid characters include ({bech32_chars})')

    while True:
        sk = PrivateKey()
        if prefix is not None and not sk.public_key.bech32()[5:5+len(prefix)] == prefix:
            continue
        if suffix is not None and not sk.public_key.bech32()[-len(suffix):] == suffix:
            continue
        break

    return sk