"""Acoustic Context Consensus Protocol prototype."""

from .capture import record_audio
from .fingerprint import compute_fingerprint, hash_chain, cosine_similarity
from .transient import ambient_timestamp
from .consensus import derive_context_id

__all__ = [
    "record_audio",
    "compute_fingerprint",
    "hash_chain",
    "cosine_similarity",
    "ambient_timestamp",
    "derive_context_id",
]
