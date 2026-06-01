from app.domain.models import ProviderKind
from app.providers.base import BaseProvider, ProviderRequest, ProviderResponse


class AnthropicProvider(BaseProvider):
    @property
    def kind(self) -> ProviderKind:
        return ProviderKind.ANTHROPIC

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise NotImplementedError("AnthropicProvider is a placeholder and is not used by the demo.")
