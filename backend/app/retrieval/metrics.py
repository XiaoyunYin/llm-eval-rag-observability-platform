from math import log2


def recall_at_k(retrieved_chunk_ids: list[str], relevant_chunk_ids: set[str], k: int = 10) -> float:
    if not relevant_chunk_ids:
        return 0.0

    retrieved_at_k = set(retrieved_chunk_ids[:k])
    return len(retrieved_at_k & relevant_chunk_ids) / len(relevant_chunk_ids)


def ndcg_at_k(
    retrieved_chunk_ids: list[str],
    relevance_by_chunk_id: dict[str, int | float],
    k: int = 10,
) -> float:
    if not relevance_by_chunk_id:
        return 0.0

    gains = [float(relevance_by_chunk_id.get(chunk_id, 0)) for chunk_id in retrieved_chunk_ids[:k]]
    dcg = _discounted_cumulative_gain(gains)

    ideal_gains = sorted((float(gain) for gain in relevance_by_chunk_id.values()), reverse=True)[:k]
    ideal_dcg = _discounted_cumulative_gain(ideal_gains)

    if ideal_dcg == 0:
        return 0.0
    return dcg / ideal_dcg


def _discounted_cumulative_gain(gains: list[float]) -> float:
    return sum(gain / log2(index + 2) for index, gain in enumerate(gains))
