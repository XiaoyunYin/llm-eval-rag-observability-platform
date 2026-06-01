from app.retrieval.interfaces import BM25Retriever, DenseRetriever
from app.retrieval.models import FusedRetrievalHit
from app.retrieval.rrf import reciprocal_rank_fusion


class HybridRetriever:
    def __init__(
        self,
        dense_retriever: DenseRetriever,
        bm25_retriever: BM25Retriever,
        *,
        rrf_k: int = 60,
    ) -> None:
        self._dense_retriever = dense_retriever
        self._bm25_retriever = bm25_retriever
        self._rrf_k = rrf_k

    def search(self, query: str, top_k: int = 10) -> list[FusedRetrievalHit]:
        dense_hits = self._dense_retriever.search(query, top_k=30)
        bm25_hits = self._bm25_retriever.search(query, top_k=30)
        return reciprocal_rank_fusion(
            dense_hits,
            bm25_hits,
            rrf_k=self._rrf_k,
            input_top_k=30,
            output_top_k=top_k,
        )
