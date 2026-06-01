from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievalHit:
    chunk_id: str
    text: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class FusedRetrievalHit:
    chunk_id: str
    text: str
    rrf_score: float
    dense_rank: int | None = None
    bm25_rank: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
