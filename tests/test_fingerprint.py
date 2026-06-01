import numpy as np

from acoustic_consensus.fingerprint import compute_fingerprint, cosine_similarity


def tone_mix(freqs, samplerate=16000, duration=1.0):
    t = np.arange(int(samplerate * duration)) / samplerate
    sig = np.zeros_like(t)
    for f in freqs:
        sig += np.sin(2 * np.pi * f * t)
    sig /= max(1, len(freqs))
    return (sig * 32000).astype(np.int16)


def test_identical_audio_same_fingerprint_similarity():
    audio = tone_mix([440, 880])
    peaks_a = compute_fingerprint(audio, 16000)
    peaks_b = compute_fingerprint(audio.copy(), 16000)
    assert peaks_a == peaks_b
    assert cosine_similarity(peaks_a, peaks_b) > 0.99


def test_slightly_different_audio_similarity_above_threshold():
    base = tone_mix([440, 880, 1320])
    altered = tone_mix([440, 900, 1320])
    peaks_a = compute_fingerprint(base, 16000)
    peaks_b = compute_fingerprint(altered, 16000)
    assert cosine_similarity(peaks_a, peaks_b) > 0.7


def test_unrelated_audio_similarity_below_threshold():
    a = tone_mix([220, 330])
    b = tone_mix([2800, 3600])
    peaks_a = compute_fingerprint(a, 16000)
    peaks_b = compute_fingerprint(b, 16000)
    assert cosine_similarity(peaks_a, peaks_b) < 0.3
