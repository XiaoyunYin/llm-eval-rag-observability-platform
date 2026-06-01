from app.domain.models import ProviderKind
from app.providers.base import BaseProvider, ProviderRequest, ProviderResponse


class OpenAIProvider(BaseProvider):
    @property
    def kind(self) -> ProviderKind:
        return ProviderKind.OPENAI

    def generate(self, request: ProviderRequest) -> ProviderResponse:
        raise NotImplementedError("OpenAIProvider is a placeholder and is not used by the demo.")
