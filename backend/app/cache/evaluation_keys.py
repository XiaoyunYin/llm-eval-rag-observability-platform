from dataclasses import dataclass, field
from hashlib import sha256
import json
from typing import Any


JsonValue = dict[str, Any] | list[Any] | str | int | float | bool | None


@dataclass(frozen=True)
class EvaluationCacheKeyInput:
    provider: str
    model: str
    prompt_version: str
    rendered_messages: list[dict[str, str]]
    generation_parameters: dict[str, JsonValue]
    retrieval_configuration: dict[str, JsonValue]
    retrieved_context: list[dict[str, JsonValue]]
    tool_schema: dict[str, JsonValue] | list[JsonValue] | None = None
    judge_rubric_version: str | None = None
    namespace: str = "eval-cache"


@dataclass(frozen=True)
class EvaluationCacheKey:
    key: str
    payload_hash: str
    retrieved_context_checksum: str
    tool_schema_hash: str
    canonical_payload: dict[str, JsonValue] = field(repr=False)


def generate_evaluation_cache_key(cache_input: EvaluationCacheKeyInput) -> EvaluationCacheKey:
    retrieved_context_checksum = stable_hash(cache_input.retrieved_context)
    tool_schema_hash = stable_hash(cache_input.tool_schema or {})
    payload: dict[str, JsonValue] = {
        "provider": cache_input.provider,
        "model": cache_input.model,
        "prompt_version": cache_input.prompt_version,
        "rendered_messages": cache_input.rendered_messages,
        "generation_parameters": cache_input.generation_parameters,
        "retrieval_configuration": cache_input.retrieval_configuration,
        "retrieved_context_checksum": retrieved_context_checksum,
        "tool_schema_hash": tool_schema_hash,
        "judge_rubric_version": cache_input.judge_rubric_version,
    }
    payload_hash = stable_hash(payload)

    return EvaluationCacheKey(
        key=f"{cache_input.namespace}:{payload_hash}",
        payload_hash=payload_hash,
        retrieved_context_checksum=retrieved_context_checksum,
        tool_schema_hash=tool_schema_hash,
        canonical_payload=payload,
    )


def stable_hash(value: JsonValue) -> str:
    canonical_json = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return sha256(canonical_json.encode("utf-8")).hexdigest()
