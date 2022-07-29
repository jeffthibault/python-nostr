import os
import base64
from cffi import FFI
from secp256k1 import PrivateKey, PublicKey
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding

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

def compute_shared_secret(sender_private_key: str, receiver_public_key: str) -> str:
    public_key = PublicKey(bytes.fromhex("02" + receiver_public_key), True)
    return public_key.ecdh(bytes.fromhex(sender_private_key), copy_x).hex() 

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

ffi = FFI()
@ffi.callback("int (unsigned char *, const unsigned char *, const unsigned char *, void *)")
def copy_x(output, x32, y32, data):
    ffi.memmove(output, x32, 32)
    return 1
    