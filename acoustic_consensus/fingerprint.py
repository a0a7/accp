from __future__ import annotations

import hashlib
import json
from typing import Iterable

import numpy as np
from scipy.signal import find_peaks, stft

Peak = tuple[int, float, int]


def compute_fingerprint(audio: np.ndarray, samplerate: int, max_peaks: int = 20) -> list[Peak]:
    """Extract top spectral peaks (freq_bin, magnitude, time_frame)."""
    if audio.size == 0 or np.max(np.abs(audio)) == 0:
        return []

    audio_f = audio.astype(np.float32)
    _, _, zxx = stft(audio_f, fs=samplerate, nperseg=1024, noverlap=1024 - 256, window="hann")
    magnitudes = np.abs(zxx)

    candidates: list[Peak] = []
    for frame_idx in range(magnitudes.shape[1]):
        frame = magnitudes[:, frame_idx]
        peak_idx, _ = find_peaks(frame)
        if peak_idx.size == 0:
            continue
        for freq_bin in peak_idx:
            candidates.append((int(freq_bin), float(frame[freq_bin]), int(frame_idx)))

    if not candidates:
        return []

    candidates.sort(key=lambda item: item[1], reverse=True)
    return candidates[:max_peaks]


def _serialize_peaks(peaks: Iterable[Peak]) -> bytes:
    payload = [[int(freq), float(mag), int(time)] for freq, mag, time in peaks]
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def hash_chain(peaks: list[Peak], previous_hash: bytes = b"") -> bytes:
    """Compute one hash-chain step from peaks and previous hash."""
    return hashlib.sha256(previous_hash + _serialize_peaks(peaks)).digest()


def peaks_to_vector(peaks: list[Peak], samplerate: int) -> np.ndarray:
    """Convert peaks into a fixed 2D histogram for cosine similarity."""
    if not peaks:
        return np.zeros(64, dtype=np.float32)

    freq_bins = np.array([p[0] for p in peaks], dtype=np.float32)
    mags = np.array([p[1] for p in peaks], dtype=np.float32)
    times = np.array([p[2] for p in peaks], dtype=np.float32)

    max_freq_bin = 512.0  # nperseg/2 for the 1024-point STFT
    freq_norm = np.clip(freq_bins / max_freq_bin, 0.0, 1.0)
    time_norm = times / max(1.0, np.max(times))

    hist, _, _ = np.histogram2d(freq_norm, time_norm, bins=(8, 8), range=[[0, 1], [0, 1]], weights=mags)
    vec = hist.astype(np.float32).flatten()
    norm = np.linalg.norm(vec)
    return vec if norm == 0 else vec / norm


def cosine_similarity(peaks_a: list[Peak], peaks_b: list[Peak], samplerate: int = 16000) -> float:
    """Cosine similarity between two peak lists."""
    vec_a = peaks_to_vector(peaks_a, samplerate)
    vec_b = peaks_to_vector(peaks_b, samplerate)
    denom = float(np.linalg.norm(vec_a) * np.linalg.norm(vec_b))
    if denom == 0:
        return 1.0 if not peaks_a and not peaks_b else 0.0
    return float(np.dot(vec_a, vec_b) / denom)
