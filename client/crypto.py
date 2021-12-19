from Crypto.Cipher import AES
from Crypto.Protocol.KDF import scrypt
from Crypto.Random import get_random_bytes


def encrypt(data: bytes, key: bytes):
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest(data)
    return (cipher.nonce, ciphertext, tag)


def decrypt(data: bytes, key: bytes):
    nonce, ciphertext, tag = data
    cipher = AES.new(key, AES.MODE_GCM, nonce)
    return cipher.decrypt_and_verify(ciphertext, tag)


def generate_key(password: str, salt: bytes = None, key_length: int = 32, cost_factor: int = 2**14, block_size: int = 8, parallelization: int = 1) -> tuple[bytes, bytes]:
    if salt is None:
        salt = get_random_bytes(32)
    key = scrypt(password, salt, key_length, cost_factor, block_size, parallelization)
    return (salt, key)
