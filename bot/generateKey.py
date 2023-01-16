from nostr.key import PrivateKey
import logging

logging.basicConfig(level=logging.DEBUG)

# Generating a key pair. Only happens once.
private_key = PrivateKey()
public_key = private_key.public_key
print(f"Private key: {private_key.bech32()}")
print(f"Public key: {public_key.bech32()}")

# Is this safe?
logging.info('New key pair generated')  # add more logging info
