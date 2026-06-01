from app.domain.models import ProviderKind
from app.providers.base import BaseProvider, ProviderRequest, ProviderResponse


class MockProvider(BaseProvider):
    @property
    def kind(self) -> ProviderKind:
        return ProviderKind.MOCK

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        user_message = next(
            (message["content"] for message in reversed(request.messages) if message.get("role") == "user"),
            "No user question provided.",
        )
        return ProviderResponse(
            text=f"Mock answer for controlled demo request: {user_message}",
            model=self.model,
            provider=self.kind,
            latency_ms=48,
            token_count=96,
            estimated_cost=0.0,
            raw_response={"provider_mode": "mock", "tool_count": len(request.tools)},
        )
