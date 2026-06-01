from app.retrieval.interfaces import BM25Retriever, DenseRetriever
from app.retrieval.models import RetrievalHit


def _hit(chunk_id: str, rank: int, source: str) -> RetrievalHit:
    return RetrievalHit(
        chunk_id=chunk_id,
        text=f"Seeded {source} retrieval chunk {chunk_id}",
        score=1 / rank,
        metadata={"source": source, "seeded": True},
    )


SEEDED_DENSE_RESULTS = [
    _hit("chunk-auth-rotate", 1, "dense"),
    _hit("chunk-cache-keys", 2, "dense"),
    _hit("chunk-provider-errors", 3, "dense"),
    _hit("chunk-old-runbook", 4, "dense"),
    _hit("chunk-index-health", 5, "dense"),
    _hit("chunk-eval-rubric", 6, "dense"),
    _hit("chunk-latency-budget", 7, "dense"),
    _hit("chunk-trace-schema", 8, "dense"),
    _hit("chunk-bm25-background", 9, "dense"),
    _hit("chunk-auth-secrets", 10, "dense"),
] + [_hit(f"chunk-dense-extra-{index:02d}", index, "dense") for index in range(11, 31)]

SEEDED_BM25_RESULTS = [
    _hit("chunk-auth-rotate", 1, "bm25"),
    _hit("chunk-rag-debug", 2, "bm25"),
    _hit("chunk-index-health", 3, "bm25"),
    _hit("chunk-provider-errors", 4, "bm25"),
    _hit("chunk-auth-secrets", 5, "bm25"),
    _hit("chunk-cache-keys", 6, "bm25"),
    _hit("chunk-judge-agreement", 7, "bm25"),
    _hit("chunk-trace-search", 8, "bm25"),
    _hit("chunk-dataset-versioning", 9, "bm25"),
    _hit("chunk-eval-rubric", 10, "bm25"),
] + [_hit(f"chunk-bm25-extra-{index:02d}", index, "bm25") for index in range(11, 31)]


class SeededDenseRetriever(DenseRetriever):
    def search(self, query: str, top_k: int = 30) -> list[RetrievalHit]:
        return SEEDED_DENSE_RESULTS[:top_k]


class SeededBM25Retriever(BM25Retriever):
    def search(self, query: str, top_k: int = 30) -> list[RetrievalHit]:
        return SEEDED_BM25_RESULTS[:top_k]
