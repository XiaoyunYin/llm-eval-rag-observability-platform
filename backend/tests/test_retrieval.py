from pytest import approx

from app.retrieval.hybrid import HybridRetriever
from app.retrieval.metrics import ndcg_at_k, recall_at_k
from app.retrieval.models import RetrievalHit
from app.retrieval.rrf import reciprocal_rank_fusion
from app.retrieval.seeded import SeededBM25Retriever, SeededDenseRetriever


def test_rrf_scoring_uses_rank_contributions_from_dense_and_bm25() -> None:
    dense_hits = [
        RetrievalHit("chunk-a", "A", 0.99),
        RetrievalHit("chunk-b", "B", 0.87),
    ]
    bm25_hits = [
        RetrievalHit("chunk-b", "B", 12.0),
        RetrievalHit("chunk-c", "C", 9.5),
    ]

    fused = reciprocal_rank_fusion(dense_hits, bm25_hits, rrf_k=60, output_top_k=10)
    by_chunk = {hit.chunk_id: hit for hit in fused}

    assert by_chunk["chunk-b"].rrf_score == approx((1 / 62) + (1 / 61))
    assert by_chunk["chunk-a"].rrf_score == approx(1 / 61)
    assert [hit.chunk_id for hit in fused] == ["chunk-b", "chunk-a", "chunk-c"]


def test_rrf_deduplicates_duplicate_chunks_and_returns_top_10() -> None:
    dense_hits = [RetrievalHit(f"chunk-{index}", f"Chunk {index}", 1 / index) for index in range(1, 31)]
    bm25_hits = [
        RetrievalHit("chunk-1", "Duplicate chunk 1", 10.0),
        RetrievalHit("chunk-2", "Duplicate chunk 2", 9.0),
        *[
            RetrievalHit(f"bm25-only-{index}", f"BM25 only {index}", 1 / index)
            for index in range(3, 31)
        ],
    ]

    fused = reciprocal_rank_fusion(dense_hits, bm25_hits)

    assert len(fused) == 10
    assert len({hit.chunk_id for hit in fused}) == 10
    assert fused[0].chunk_id == "chunk-1"
    assert fused[0].dense_rank == 1
    assert fused[0].bm25_rank == 1


def test_rrf_ignores_repeated_chunks_from_the_same_source() -> None:
    dense_hits = [
        RetrievalHit("chunk-a", "A", 0.99),
        RetrievalHit("chunk-a", "Duplicate A", 0.98),
    ]
    bm25_hits = [RetrievalHit("chunk-b", "B", 10.0)]

    fused = reciprocal_rank_fusion(dense_hits, bm25_hits)
    by_chunk = {hit.chunk_id: hit for hit in fused}

    assert by_chunk["chunk-a"].rrf_score == approx(1 / 61)


def test_recall_at_10_counts_relevant_documents_in_top_k() -> None:
    retrieved = [f"chunk-{index}" for index in range(1, 11)]
    relevant = {"chunk-1", "chunk-5", "chunk-12", "chunk-20"}

    assert recall_at_k(retrieved, relevant, k=10) == approx(0.5)


def test_ndcg_at_10_rewards_relevant_documents_higher_in_ranking() -> None:
    retrieved = ["doc-c", "doc-x", "doc-a", "doc-y", "doc-b"]
    relevance = {"doc-a": 3, "doc-b": 2, "doc-c": 1}

    score = ndcg_at_k(retrieved, relevance, k=10)

    assert score == approx(0.6874847125494647)


def test_hybrid_retriever_uses_seeded_dense_and_bm25_top_30_with_rrf() -> None:
    retriever = HybridRetriever(SeededDenseRetriever(), SeededBM25Retriever())

    results = retriever.search("How do I debug retrieval quality?", top_k=10)

    assert len(results) == 10
    assert results[0].chunk_id == "chunk-auth-rotate"
    assert results[0].dense_rank == 1
    assert results[0].bm25_rank == 1
    assert "chunk-rag-debug" in {result.chunk_id for result in results}
