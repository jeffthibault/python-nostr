from secp256k1 import PrivateKey

def generate_private_key() -> str:
    private_key = PrivateKey()
    public_key = private_key.pubkey.serialize().hex()
    while not public_key.startswith("02"):
        private_key = PrivateKey()
        public_key = private_key.pubkey.serialize().hex()
    return private_key.serialize()

def get_public_key(secret: str) -> str:
    private_key = PrivateKey(bytes.fromhex(secret))
    public_key = private_key.pubkey.serialize().hex()
    return public_key[2:] # chop off sign byte

def get_key_pair() -> tuple:
    private_key = PrivateKey()
    public_key = private_key.pubkey.serialize().hex()
    return (private_key.serialize(), public_key[2:])
    