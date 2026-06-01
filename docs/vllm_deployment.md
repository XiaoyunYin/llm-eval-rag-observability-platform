# vLLM Deployment Notes

`VLLMProvider` in `backend/app/providers/vllm.py` implements the same `BaseProvider` interface as `MockProvider`, but targets an OpenAI-compatible vLLM endpoint. It builds chat-completion payloads (`model`, `messages`, `temperature`, `max_tokens`, optional `tools`) without actually calling out — the adapter boundary is defined, the HTTP client isn't wired up yet.

## Local setup (when ready)

Point the backend at a running vLLM instance:

```bash
VLLM_BASE_URL=http://localhost:8001/v1
PROVIDER_MODE=vllm
```

The gateway picks up `VLLMProvider` behind the same interface everything else uses.

## What's missing to make it real

- HTTP client for the OpenAI-compatible API
- Timeout, retry, and cancellation
- Provider errors normalized into evaluation results
- Token and cost accounting
- Model availability checks
- Integration tests against a local or CI-managed vLLM endpoint
- Secure config handling for protected endpoints