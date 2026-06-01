from typing import Protocol

from app.retrieval.models import RetrievalHit


class DenseRetriever(Protocol):
    def search(self, query: str, top_k: int = 30) -> list[RetrievalHit]:
        """Return dense vector retrieval hits ordered from best to worst."""


class BM25Retriever(Protocol):
    def search(self, query: str, top_k: int = 30) -> list[RetrievalHit]:
        """Return BM25 lexical retrieval hits ordered from best to worst."""
