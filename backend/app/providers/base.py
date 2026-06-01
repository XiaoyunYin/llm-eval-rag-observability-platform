from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.domain.models import ProviderKind


@dataclass(frozen=True)
class ProviderRequest:
    messages: list[dict[str, str]]
    generation_parameters: dict[str, Any] = field(default_factory=dict)
    tools: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ProviderResponse:
    text: str
    model: str
    provider: ProviderKind
    latency_ms: int
    token_count: int
    estimated_cost: float
    raw_response: dict[str, Any] = field(default_factory=dict)


class BaseProvider(ABC):
    def __init__(self, *, model: str, base_url: str | None = None) -> None:
        self.model = model
        self.base_url = base_url

    @property
    @abstractmethod
    def kind(self) -> ProviderKind:
        """Provider family identifier used in traces and cache keys."""

    @abstractmethod
    def generate(self, request: ProviderRequest) -> ProviderResponse:
        """Generate a response for an evaluation request."""
