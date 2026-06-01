from __future__ import annotations

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks


def _energy_envelope(audio: np.ndarray, samplerate: int) -> np.ndarray:
    energy = np.square(audio.astype(np.float32))
    nyquist = samplerate / 2
    cutoff = min(200.0, nyquist * 0.9)
    b, a = butter(2, cutoff / nyquist, btype="low")
    return filtfilt(b, a, energy)


def ambient_timestamp(audio: np.ndarray, samplerate: int) -> bytes:
    """Return 6-byte ambient timestamp (24-bit t12_ms + 24-bit t23_ms)."""
    if audio.size == 0:
        return b"\x00" * 6

    envelope = _energy_envelope(audio, samplerate)
    median = float(np.median(envelope)) if envelope.size else 0.0
    prominence = max(median * 5.0, np.max(envelope) * 0.05)

    peaks, _ = find_peaks(envelope, prominence=prominence, distance=max(1, samplerate // 20))
    if peaks.size < 3:
        return b"\x00" * 6

    sorted_by_amp = sorted(peaks, key=lambda idx: envelope[idx], reverse=True)[:3]
    sorted_by_time = np.array(sorted(sorted_by_amp), dtype=np.int64)

    t12_ms = int(max(0, (sorted_by_time[1] - sorted_by_time[0]) * 1000 // samplerate)) & 0xFFFFFF
    t23_ms = int(max(0, (sorted_by_time[2] - sorted_by_time[1]) * 1000 // samplerate)) & 0xFFFFFF
    packed = (t12_ms << 24) | t23_ms
    return packed.to_bytes(6, byteorder="big")
