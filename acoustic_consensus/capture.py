from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


def record_audio(duration: float = 5.0, samplerate: int = 16000) -> tuple[np.ndarray, int]:
    """Record mono audio and return int16 samples with samplerate.

    The sounddevice import is deferred so tests can run without audio hardware.
    """
    import sounddevice as sd

    samples = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype="int16")
    sd.wait()
    return samples.flatten(), samplerate


def save_wav_debug(path: str | Path, samples: np.ndarray, samplerate: int) -> None:
    """Write int16 mono PCM samples to a WAV file for debugging."""
    pcm = np.asarray(samples, dtype=np.int16)
    output = Path(path)
    with wave.open(str(output), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(samplerate)
        wav.writeframes(pcm.tobytes())
