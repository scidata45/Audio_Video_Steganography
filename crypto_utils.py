"""AES-256-GCM encryption with a scrypt password-derived key."""
import os
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

MAGIC = b"ST1"  # marks our data format


def _key(password, salt):
    return Scrypt(salt=salt, length=32, n=2**15, r=8, p=1).derive(password.encode())


def encrypt(message, password):
    """Returns MAGIC + salt(16) + nonce(12) + ciphertext+tag."""
    salt, nonce = os.urandom(16), os.urandom(12)
    ct = AESGCM(_key(password, salt)).encrypt(nonce, message.encode(), MAGIC)
    return MAGIC + salt + nonce + ct


def decrypt(blob, password):
    if len(blob) < 47 or blob[:3] != MAGIC:
        raise ValueError("No hidden message found in this file.")
    salt, nonce, ct = blob[3:19], blob[19:31], blob[31:]
    try:
        return AESGCM(_key(password, salt)).decrypt(nonce, ct, MAGIC).decode()
    except InvalidTag:
        raise ValueError("Wrong password, or the file was modified.")
