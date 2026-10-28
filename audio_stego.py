"""Audio LSB steganography for PCM WAV (8/16-bit). Uses the low byte of each sample."""
import wave
import numpy as np
from lsb import embed, extract


def _load(path):
    with wave.open(path, "rb") as w:
        params, frames = w.getparams(), w.readframes(w.getnframes())
    if params.sampwidth not in (1, 2):
        raise ValueError("Use an 8-bit or 16-bit PCM WAV file.")
    return params, np.frombuffer(frames, dtype=np.uint8).copy()


def hide(in_path, out_path, payload):
    params, data = _load(in_path)
    embed(data[0::params.sampwidth], payload)  # view: edits 'data' in place
    with wave.open(out_path, "wb") as w:
        w.setparams(params)
        w.writeframes(data.tobytes())


def extract_payload(in_path):
    params, data = _load(in_path)
    return extract(data[0::params.sampwidth])
