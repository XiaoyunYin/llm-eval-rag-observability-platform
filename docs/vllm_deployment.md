# vLLM Deployment Notes

This repository includes a `VLLMProvider` placeholder to show where an OpenAI-compatible vLLM endpoint would fit. The public demo does not start vLLM, does not require GPU access, and does not call a live model endpoint.

## Intended integration shape

vLLM can expose an OpenAI-compatible API. The provider gateway would send chat-completion-shaped payloads containing:

- `model`
- `messages`
- generation parameters such as `temperature` and `max_tokens`
- optional `tools`

The current placeholder builds that payload shape in `backend/app/providers/vllm.py`.

## Example local endpoint

If a future implementation runs vLLM locally, the environment could point at an endpoint such as:

```bash
VLLM_BASE_URL=http://localhost:8001/v1
PROVIDER_MODE=vllm
```

The backend would then instantiate `VLLMProvider` behind the same `BaseProvider` interface used by `MockProvider`.

## Work needed before real use

- Add an HTTP client for the OpenAI-compatible API.
- Add timeout, retry, and cancellation behavior.
- Normalize provider errors into explicit evaluation results.
- Add token and cost accounting.
- Add model availability checks.
- Add integration tests against a local or CI-managed vLLM endpoint.
- Add secure configuration handling for any protected endpoint.

## Honest scope

The current project demonstrates the adapter boundary only. It does not claim a production vLLM deployment, live inference traffic, GPU orchestration, autoscaling, or company deployment.
