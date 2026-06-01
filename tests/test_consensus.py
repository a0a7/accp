from acoustic_consensus.consensus import cluster_hashes_by_similarity, derive_context_id, run_three_round_consensus
from acoustic_consensus.fingerprint import hash_chain


def test_identical_devices_converge_to_same_context_id():
    peaks = [(1, 0.9, 1), (4, 0.6, 2), (10, 0.5, 3)]
    h1 = hash_chain(peaks)
    h2 = hash_chain(peaks)
    c1 = run_three_round_consensus(h1, [{h2}, {h1, h2}, set()])
    c2 = run_three_round_consensus(h2, [{h1}, {h1, h2}, set()])
    assert c1 == c2


def test_different_audio_can_result_in_different_ids():
    h1 = hash_chain([(1, 0.9, 1)])
    h2 = hash_chain([(50, 0.9, 5)])
    c1 = derive_context_id({h1})
    c2 = derive_context_id({h2})
    assert c1 != c2


def test_similarity_clustering_groups_similar_fingerprints():
    p1 = [(4, 1.0, 1), (10, 0.8, 2)]
    p2 = [(4, 0.95, 1), (10, 0.75, 2)]
    p3 = [(120, 1.0, 8), (140, 0.7, 9)]
    h1, h2, h3 = hash_chain(p1), hash_chain(p2), hash_chain(p3)

    clusters = cluster_hashes_by_similarity({h1: p1, h2: p2, h3: p3}, tolerance=0.85)
    sizes = sorted(len(c) for c in clusters)
    assert sizes == [1, 2]
    paired_cluster = next(cluster for cluster in clusters if h1 in cluster)
    assert h2 in paired_cluster
    isolated_cluster = next(cluster for cluster in clusters if h3 in cluster)
    assert isolated_cluster == {h3}
