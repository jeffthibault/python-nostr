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


def _guess_event(content: str, public_key: str, kind: int, tags: list=[]) -> Event:
    event = Event(public_key, content, kind, tags)
    num_leading_zero_bits = count_leading_zero_bits(event.id)
    return num_leading_zero_bits, event


def mine_event(content: str, difficulty: int, public_key: str, kind: int, tags: list=[]) -> Event:
    all_tags = [["nonce", "1", str(difficulty)]]
    all_tags.extend(tags)

    num_leading_zero_bits, event = _guess_event(content, public_key, kind, all_tags)

    attempts = 1
    while num_leading_zero_bits < difficulty:
        attempts += 1
        all_tags[0][1] = str(attempts)
        num_leading_zero_bits, event = _guess_event(content, public_key, kind, all_tags)
        num_leading_zero_bits = count_leading_zero_bits(event.id)

    return event


def _guess_key():
    sk = PrivateKey()
    num_leading_zero_bits = count_leading_zero_bits(sk.public_key.hex())
    return num_leading_zero_bits, sk


def mine_key(difficulty: int) -> PrivateKey:
    num_leading_zero_bits, sk = _guess_key()

    while num_leading_zero_bits < difficulty:
        num_leading_zero_bits, sk = _guess_key()

    return sk


bech32_chars = '023456789acdefghjklmnpqrstuvwxyz'


def _guess_vanity_key():
    sk = PrivateKey()
    vk = sk.public_key.bech32()
    return sk, vk


def mine_vanity_key(prefix: str = None, suffix: str = None) -> PrivateKey:
    if prefix is None and suffix is None:
        raise ValueError("Expected at least one of 'prefix' or 'suffix' arguments")
    for pattern in [prefix, suffix]:
        if pattern is not None:
            missing_chars = [c for c in pattern if c not in bech32_chars]
            if len(missing_chars):
                raise ValueError(
                    f'{missing_chars} are not valid characters'
                    f'for a bech32 key. Valid characters include ({bech32_chars})')
    while True:
        sk, vk = _guess_vanity_key()
        if prefix is not None and not vk[5:5+len(prefix)] == prefix:
            continue
        if suffix is not None and not vk[-len(suffix):] == suffix:
            continue
        break

    return sk