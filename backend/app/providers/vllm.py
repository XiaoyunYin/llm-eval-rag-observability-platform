from typing import Any

from app.domain.models import ProviderKind
from app.providers.base import BaseProvider, ProviderRequest, ProviderResponse


class VLLMProvider(BaseProvider):
    @property
    def kind(self) -> ProviderKind:
        return ProviderKind.VLLM

    def build_openai_compatible_payload(self, request: ProviderRequest) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": request.messages,
            "tools": request.tools,
            **request.generation_parameters,
        }

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise NotImplementedError("VLLMProvider is a placeholder for OpenAI-compatible endpoints.")
