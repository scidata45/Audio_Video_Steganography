"""Video LSB steganography. Hides bits in pixel colour values of frames.
Output is lossless AVI (FFV1) because lossy compression (MP4) would destroy the bits.
Note: OpenCV does not copy the audio track."""
import cv2
import numpy as np
from lsb import embed, extract


def _read(path):
    cap, frames = cv2.VideoCapture(path), []
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        frames.append(frame)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    cap.release()
    if not frames:
        raise ValueError("Could not read this video file.")
    return frames, fps


def hide(in_path, out_path, payload):
    frames, fps = _read(in_path)
    h, w = frames[0].shape[:2]
    flat = np.concatenate([f.ravel() for f in frames])
    embed(flat, payload)
    writer = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc(*"FFV1"), fps, (w, h))
    if not writer.isOpened():
        raise ValueError("Lossless video encoder (FFV1) is not available on this system.")
    size = h * w * 3
    for i in range(len(frames)):
        writer.write(flat[i * size:(i + 1) * size].reshape(h, w, 3))
    writer.release()


def extract_payload(in_path):
    frames, _ = _read(in_path)
    return extract(np.concatenate([f.ravel() for f in frames]))
