from __future__ import annotations

import os
import threading
import time
import uuid
from dataclasses import dataclass, field

from .capture import record_audio
from .consensus import derive_context_id
from .fingerprint import compute_fingerprint, hash_chain
from .network import UDPBroadcastChannel
from .transient import ambient_timestamp


@dataclass
class RuntimeState:
    known_hashes: set[bytes] = field(default_factory=set)


def run_once(duration: float = 5.0, rounds: int = 3, round_seconds: float = 2.0) -> int:
    try:
        samples, samplerate = record_audio(duration=duration, samplerate=16000)
    except Exception:
        return 0

    peaks = compute_fingerprint(samples, samplerate)
    if not peaks:
        return 0

    own_hash = hash_chain(peaks)
    timestamp = ambient_timestamp(samples, samplerate)

    device_id = str(uuid.uuid4())
    state = RuntimeState(known_hashes={own_hash})
    # Default loopback binding minimizes exposure; set ACCP_LISTEN_IP=0.0.0.0 for multi-device LAN demos.
    channel = UDPBroadcastChannel(listen_ip=os.getenv("ACCP_LISTEN_IP", "127.0.0.1"))

    stop_event = threading.Event()

    def listener() -> None:
        while not stop_event.is_set():
            message = channel.recv()
            if not message:
                continue
            if message.get("device_id") == device_id:
                continue
            if message.get("type") in {"hash_chain", "hash_set", "final_vote"}:
                data = message.get("data")
                if isinstance(data, bytes):
                    state.known_hashes.add(data)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, bytes):
                            state.known_hashes.add(item)

    listen_thread = threading.Thread(target=listener, daemon=True)
    listen_thread.start()

    try:
        for round_idx in range(rounds):
            if round_idx == 0:
                payload = own_hash
                msg_type = "hash_chain"
            elif round_idx == 1:
                payload = sorted(state.known_hashes)
                msg_type = "hash_set"
            else:
                payload = derive_context_id(state.known_hashes).to_bytes(4, "big")
                msg_type = "final_vote"

            channel.send(
                {
                    "type": msg_type,
                    "data": payload,
                    "timestamp": timestamp,
                    "device_id": device_id,
                }
            )
            time.sleep(round_seconds)
    finally:
        stop_event.set()
        listen_thread.join(timeout=0.5)
        channel.close()

    return derive_context_id(state.known_hashes)


if __name__ == "__main__":
    context_id = run_once()
    print(f"Context ID: {context_id:08x}")
