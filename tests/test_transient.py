import numpy as np

from acoustic_consensus.transient import ambient_timestamp


def test_ambient_timestamp_recovers_impulse_intervals():
    samplerate = 16000
    duration_s = 2
    audio = np.zeros(samplerate * duration_s, dtype=np.int16)

    t1 = int(0.2 * samplerate)
    t2 = int(0.8 * samplerate)
    t3 = int(1.4 * samplerate)

    audio[t1] = 30000
    audio[t2] = 28000
    audio[t3] = 32000

    stamp = ambient_timestamp(audio, samplerate)
    packed = int.from_bytes(stamp, "big")
    t12 = (packed >> 24) & 0xFFFFFF
    t23 = packed & 0xFFFFFF

    assert t12 == 600
    assert t23 == 600
