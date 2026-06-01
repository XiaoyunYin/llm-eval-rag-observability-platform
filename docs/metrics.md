# Metrics

This document explains the retrieval, cache, and judge metrics used by the demo. The dashboard values are controlled demo metrics from seeded data, not production measurements.

## Seeded dashboard metrics

| Metric | Dense-only | Hybrid RAG |
| --- | ---: | ---: |
| `recall@10` | `0.69` | `0.84` |
| `nDCG@10` | `0.62` | `0.79` |

Additional seeded values:

- Judge agreement: `84%`
- Cache hit rate: `40%`

The cache hit rate is a controlled aggregate demo metric. It is not derived from production Redis traffic.

## recall@k

`recall@k` measures how many known relevant chunks appear in the first `k` retrieved chunks.

```text
recall@k = relevant retrieved in top k / total relevant
```

In code, this lives in `backend/app/retrieval/metrics.py`.

Edge cases:

- If there are no relevant chunks, the demo returns `0.0`.
- Duplicate retrieved IDs are counted once because recall is set-based for the top `k`.

## nDCG@k

`nDCG@k` measures ranking quality by discounting relevant chunks that appear lower in the ranking.

```text
DCG@k = sum(gain_at_rank / log2(rank + 1))
nDCG@k = DCG@k / ideal DCG@k
```

The implementation uses raw relevance gains from the seeded relevance map. If the ideal score is `0`, the demo returns `0.0`.

## Reciprocal rank fusion

Hybrid retrieval merges dense top 30 and BM25 top 30 with reciprocal rank fusion:

```text
score(document) = sum(1 / (60 + rank_in_source))
```

Rules:

- Dense input is capped at top 30.
- BM25 input is capped at top 30.
- Duplicate `chunk_id` values are deduplicated.
- Final output is top 10 by fused score.

## Judge pass/fail

Each judge score contains:

- `correctness`: 1 to 5
- `faithfulness`: 1 to 5
- `citation_quality`: 1 to 5
- `critical_unsupported_claim`: boolean

An answer passes only if all conditions are true:

- `correctness >= 4`
- `faithfulness >= 4`
- `citation_quality >= 3`
- `critical_unsupported_claim == false`

Two judges produce independent pass/fail decisions. If the decisions differ, the result is routed to `manual_review`.

## Cache key correctness

The cache-key generator creates deterministic SHA-256 keys from canonical JSON. The key includes provider, model, prompt version, rendered messages, generation parameters, retrieval configuration, retrieved context checksum, tool schema hash, and optional judge rubric version.
