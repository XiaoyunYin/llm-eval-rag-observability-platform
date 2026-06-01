import pytest

from app.domain.models import ProviderKind
from app.providers.anthropic import AnthropicProvider
from app.providers.base import ProviderRequest
from app.providers.mock import MockProvider
from app.providers.openai import OpenAIProvider
from app.providers.vllm import VLLMProvider


def test_mock_provider_generates_demo_response_without_external_api() -> None:
    provider = MockProvider(model="mock-hybrid-rag-candidate")
    response = provider.generate(
        ProviderRequest(messages=[{"role": "user", "content": "Explain cache keys."}])
    )

    assert response.provider == ProviderKind.MOCK
    assert response.model == "mock-hybrid-rag-candidate"
    assert "Explain cache keys." in response.text
    assert response.estimated_cost == 0.0
    assert response.token_count > 0


def test_openai_provider_is_placeholder() -> None:
    provider = OpenAIProvider(model="gpt-placeholder")

    with pytest.raises(NotImplementedError, match="placeholder"):
        provider.generate(ProviderRequest(messages=[]))


def test_anthropic_provider_is_placeholder() -> None:
    provider = AnthropicProvider(model="claude-placeholder")

    with pytest.raises(NotImplementedError, match="placeholder"):
        provider.generate(ProviderRequest(messages=[]))


def test_vllm_provider_builds_openai_compatible_payload_but_does_not_call_network() -> None:
    provider = VLLMProvider(model="local-vllm-model", base_url="http://localhost:8001/v1")
    request = ProviderRequest(
        messages=[{"role": "user", "content": "Hello"}],
        generation_parameters={"temperature": 0.2},
        tools=[{"type": "function", "function": {"name": "lookup"}}],
    )

    payload = provider.build_openai_compatible_payload(request)

    assert payload == {
        "model": "local-vllm-model",
        "messages": [{"role": "user", "content": "Hello"}],
        "tools": [{"type": "function", "function": {"name": "lookup"}}],
        "temperature": 0.2,
    }
    with pytest.raises(NotImplementedError, match="OpenAI-compatible"):
        provider.generate(request)
