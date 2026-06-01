from __future__ import annotations

import hashlib
from dataclasses import dataclass, field

from .fingerprint import Peak, cosine_similarity


@dataclass
class ConsensusState:
    device_id: str
    known_hashes: set[bytes] = field(default_factory=set)


def derive_context_id(hashes: set[bytes]) -> int:
    """Deterministically derive a 32-bit context ID from hash set."""
    if not hashes:
        return 0
    digest = hashlib.sha256(b"".join(sorted(hashes))).digest()
    return int.from_bytes(digest[:4], byteorder="big")


def run_three_round_consensus(
    local_hash: bytes,
    received_round_hashes: list[set[bytes]],
) -> int:
    """Apply the three-round gossip merge model and return a context ID."""
    known = {local_hash}
    for round_hashes in received_round_hashes[:3]:
        known.update(round_hashes)
    return derive_context_id(known)


def cluster_hashes_by_similarity(
    fingerprints: dict[bytes, list[Peak]],
    tolerance: float = 0.85,
    samplerate: int = 16000,
) -> list[set[bytes]]:
    """Cluster fingerprint hashes by cosine similarity tolerance."""
    clusters: list[set[bytes]] = []
    hashes = list(fingerprints)

    for current in hashes:
        placed = False
        for cluster in clusters:
            representative = next(iter(cluster))
            sim = cosine_similarity(fingerprints[current], fingerprints[representative], samplerate=samplerate)
            if sim >= tolerance:
                cluster.add(current)
                placed = True
                break
        if not placed:
            clusters.append({current})

    return clusters
