import os
import base64
from cffi import FFI
from secp256k1 import PrivateKey, PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from . import bech32

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

def bech32_encode_private_key(private_key: str) -> str:
    converted_bits = bech32.convertbits(bytes.fromhex(private_key), 8, 5)
    return bech32.bech32_encode("nsec", converted_bits, bech32.Encoding.BECH32)

def bech32_decode_private_key(private_key_bech32: str) -> str:
    data = bech32.bech32_decode(private_key_bech32)[1]
    return bytes(bech32.convertbits(data, 5, 8, False)).hex()

def bech32_encode_public_key(public_key: str) -> str:
    converted_bits = bech32.convertbits(bytes.fromhex(public_key), 8, 5)
    return bech32.bech32_encode("npub", converted_bits, bech32.Encoding.BECH32)

def bech32_decode_public_key(public_key_bech32: str) -> str:
    data = bech32.bech32_decode(public_key_bech32)[1]
    return bytes(bech32.convertbits(data, 5, 8, False)).hex()

def tweak_add_private_key(private_key: str, scalar: bytes) -> str:
    sk = PrivateKey(bytes.fromhex(private_key))
    tweaked_secret = sk.tweak_add(scalar)
    new_sk = PrivateKey(tweaked_secret)
    return new_sk.serialize()

def compute_shared_secret(sender_private_key: str, receiver_public_key: str) -> str:
    public_key = PublicKey(bytes.fromhex("02" + receiver_public_key), True)
    return public_key.ecdh(bytes.fromhex(sender_private_key), hashfn=copy_x).hex() 

def encrypt_message(content: str, shared_secret: str) -> str:
    iv = os.urandom(16)

    cipher = Cipher(algorithms.AES(bytes.fromhex(shared_secret)), modes.CBC(iv))
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(content.encode()) + padder.finalize()

    encryptor = cipher.encryptor()
    encrypted_message = encryptor.update(padded_data) + encryptor.finalize()

    return f"{base64.b64encode(encrypted_message).decode()}?iv={base64.b64encode(iv).decode()}"

def decrypt_message(encoded_message: str, shared_secret: str) -> str:
    encoded_data = encoded_message.split('?iv=')
    encoded_content, encoded_iv = encoded_data[0], encoded_data[1]

    encrypted_content = base64.b64decode(encoded_content)
    iv = base64.b64decode(encoded_iv)

    cipher = Cipher(algorithms.AES(bytes.fromhex(shared_secret)), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_message = decryptor.update(encrypted_content) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    unpadded_data = unpadder.update(decrypted_message) + unpadder.finalize()

    return unpadded_data.decode()

def sign_message(hash: str, private_key: str) -> str:
    sk = PrivateKey(bytes.fromhex(private_key))
    sig = sk.schnorr_sign(bytes.fromhex(hash), None, raw=True)
    return sig.hex()

def verify_message(hash: str, sig: str, public_key: str) -> bool:
    pk = PublicKey(bytes.fromhex("02" + public_key), True)
    return pk.schnorr_verify(bytes.fromhex(hash), bytes.fromhex(sig), None, True)

ffi = FFI()
@ffi.callback("int (unsigned char *, const unsigned char *, const unsigned char *, void *)")
def copy_x(output, x32, y32, data):
    ffi.memmove(output, x32, 32)
    return 1
    