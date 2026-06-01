from dataclasses import replace

from app.cache.evaluation_keys import EvaluationCacheKeyInput, generate_evaluation_cache_key


def base_cache_input() -> EvaluationCacheKeyInput:
    return EvaluationCacheKeyInput(
        provider="mock",
        model="mock-hybrid-rag-candidate",
        prompt_version="support-answer-v1",
        rendered_messages=[
            {"role": "system", "content": "Answer with citations."},
            {"role": "user", "content": "How do I rotate an API key?"},
        ],
        generation_parameters={"temperature": 0.1, "max_tokens": 400},
        retrieval_configuration={"mode": "hybrid", "dense_top_k": 30, "bm25_top_k": 30, "rrf_k": 60},
        retrieved_context=[
            {"chunk_id": "chunk-auth-rotate", "text": "Create the new key before revoking the old key."},
            {"chunk_id": "chunk-auth-secrets", "text": "Store secrets in the configured vault."},
        ],
        tool_schema={
            "name": "lookup_runbook",
            "parameters": {"type": "object", "properties": {"runbook_id": {"type": "string"}}},
        },
        judge_rubric_version="rag-helpfulness-v1",
    )


def cache_key(cache_input: EvaluationCacheKeyInput) -> str:
    return generate_evaluation_cache_key(cache_input).key


def test_cache_key_is_deterministic_for_equivalent_inputs() -> None:
    first = generate_evaluation_cache_key(base_cache_input())
    second = generate_evaluation_cache_key(base_cache_input())

    assert first.key == second.key
    assert first.retrieved_context_checksum == second.retrieved_context_checksum
    assert first.tool_schema_hash == second.tool_schema_hash


def test_cache_key_is_stable_when_dict_key_order_changes() -> None:
    original = base_cache_input()
    reordered = replace(
        original,
        generation_parameters={"max_tokens": 400, "temperature": 0.1},
        retrieval_configuration={"rrf_k": 60, "bm25_top_k": 30, "dense_top_k": 30, "mode": "hybrid"},
    )

    assert cache_key(original) == cache_key(reordered)


def test_cache_key_changes_when_prompt_version_changes() -> None:
    original = base_cache_input()
    changed = replace(original, prompt_version="support-answer-v2")

    assert cache_key(original) != cache_key(changed)


def test_cache_key_changes_when_model_changes() -> None:
    original = base_cache_input()
    changed = replace(original, model="mock-hybrid-rag-candidate-v2")

    assert cache_key(original) != cache_key(changed)


def test_cache_key_changes_when_generation_params_change() -> None:
    original = base_cache_input()
    changed = replace(original, generation_parameters={"temperature": 0.7, "max_tokens": 400})

    assert cache_key(original) != cache_key(changed)


def test_cache_key_changes_when_retrieved_context_changes() -> None:
    original = base_cache_input()
    changed = replace(
        original,
        retrieved_context=[
            {"chunk_id": "chunk-auth-rotate", "text": "Create the new key before revoking the old key."},
            {"chunk_id": "chunk-auth-secrets", "text": "Updated secret storage guidance."},
        ],
    )

    original_key = generate_evaluation_cache_key(original)
    changed_key = generate_evaluation_cache_key(changed)

    assert original_key.key != changed_key.key
    assert original_key.retrieved_context_checksum != changed_key.retrieved_context_checksum


def test_cache_key_changes_when_tool_schema_changes() -> None:
    original = base_cache_input()
    changed = replace(
        original,
        tool_schema={
            "name": "lookup_runbook",
            "parameters": {
                "type": "object",
                "properties": {
                    "runbook_id": {"type": "string"},
                    "include_archived": {"type": "boolean"},
                },
            },
        },
    )

    original_key = generate_evaluation_cache_key(original)
    changed_key = generate_evaluation_cache_key(changed)

    assert original_key.key != changed_key.key
    assert original_key.tool_schema_hash != changed_key.tool_schema_hash


def test_cache_key_changes_when_judge_rubric_version_changes() -> None:
    original = base_cache_input()
    changed = replace(original, judge_rubric_version="rag-helpfulness-v2")

    assert cache_key(original) != cache_key(changed)
