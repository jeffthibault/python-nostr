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
            if len(missing_chars) > 0:
                raise ValueError(
                    f"{missing_chars} not in valid list of bech32 chars: ({bech32_chars})"
                    )
    while True:
        sk, vk = _guess_vanity_key()
        if prefix is not None and not vk[5:5+len(prefix)] == prefix:
            continue
        if suffix is not None and not vk[-len(suffix):] == suffix:
            continue
        break

    return sk


def get_hashrate(operation, n_guesses: int = 1e4, **operation_kwargs):
    n_guesses = int(n_guesses)
    def _time_operation():
        start = time.perf_counter()
        operation(**operation_kwargs)
        end = time.perf_counter()
        return end - start
    t = sum([_time_operation() for _ in range(n_guesses)]) / n_guesses
    hashrate = 1 / t
    return hashrate


def expected_time(n_pattern: int, n_options: int, hashrate: float):
    p = 1 / n_options
    expected_guesses = 1 / (p ** n_pattern)
    time_seconds = expected_guesses / hashrate
    return time_seconds


def estimate_event_time(content: str, difficulty: int, public_key: str,
                        kind: int, tags: list=[]) -> float:
    all_tags = [["nonce", "1", str(difficulty)]]
    all_tags.extend(tags)
    hashrate = get_hashrate(_guess_event,
                             content=content,
                             public_key=public_key,
                             kind=kind,
                             tags=all_tags)
    return expected_time(difficulty, 2, hashrate)


def estimate_vanity_time(n_pattern: int):
    hashrate = get_hashrate(_guess_vanity_key)
    return expected_time(n_pattern, len(bech32_chars), hashrate)


def estimate_key_time(difficulty: int) -> float:
    hashrate = get_hashrate(_guess_key)
    return expected_time(difficulty, 2, hashrate)
