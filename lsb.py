"""Shared LSB logic. 'carrier' is a 1-D uint8 numpy array (modified in place)."""
import numpy as np


def embed(carrier, payload):
    data = len(payload).to_bytes(4, "big") + payload  # 4-byte length header
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    if len(bits) > carrier.size:
        raise ValueError("Message is too large for this file. Use a bigger file or a shorter message.")
    carrier[:len(bits)] = (carrier[:len(bits)] & 0xFE) | bits


def extract(carrier):
    if carrier.size < 32:
        raise ValueError("No hidden message found in this file.")
    n = int.from_bytes(np.packbits(carrier[:32] & 1).tobytes(), "big")
    if n <= 0 or 32 + n * 8 > carrier.size:
        raise ValueError("No hidden message found in this file.")
    return np.packbits(carrier[32:32 + n * 8] & 1).tobytes()
