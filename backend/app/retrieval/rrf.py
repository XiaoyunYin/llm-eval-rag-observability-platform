from app.retrieval.models import FusedRetrievalHit, RetrievalHit


def reciprocal_rank_fusion(
    dense_hits: list[RetrievalHit],
    bm25_hits: list[RetrievalHit],
    *,
    rrf_k: int = 60,
    input_top_k: int = 30,
    output_top_k: int = 10,
) -> list[FusedRetrievalHit]:
    """Fuse dense and BM25 rankings with reciprocal rank fusion.

    RRF uses one-indexed ranks and adds 1 / (rrf_k + rank) for each source list.
    Duplicate chunks are merged by chunk_id with scores accumulated across lists.
    """

    fused_by_chunk: dict[str, FusedRetrievalHit] = {}

    for source, hits in (("dense", dense_hits[:input_top_k]), ("bm25", bm25_hits[:input_top_k])):
        seen_in_source: set[str] = set()
        for rank, hit in enumerate(hits, start=1):
            if hit.chunk_id in seen_in_source:
                continue
            seen_in_source.add(hit.chunk_id)

            contribution = 1 / (rrf_k + rank)
            existing = fused_by_chunk.get(hit.chunk_id)

            if existing is None:
                fused_by_chunk[hit.chunk_id] = FusedRetrievalHit(
                    chunk_id=hit.chunk_id,
                    text=hit.text,
                    rrf_score=contribution,
                    dense_rank=rank if source == "dense" else None,
                    bm25_rank=rank if source == "bm25" else None,
                    metadata={**hit.metadata},
                )
                continue

            fused_by_chunk[hit.chunk_id] = FusedRetrievalHit(
                chunk_id=existing.chunk_id,
                text=existing.text,
                rrf_score=existing.rrf_score + contribution,
                dense_rank=existing.dense_rank if source == "bm25" else rank,
                bm25_rank=existing.bm25_rank if source == "dense" else rank,
                metadata={**existing.metadata, **hit.metadata},
            )

    return sorted(
        fused_by_chunk.values(),
        key=lambda hit: (-hit.rrf_score, _min_rank(hit), hit.chunk_id),
    )[:output_top_k]


def _min_rank(hit: FusedRetrievalHit) -> int:
    ranks = [rank for rank in (hit.dense_rank, hit.bm25_rank) if rank is not None]
    return min(ranks) if ranks else 10_000
