# Metrics

## Dashboard values

| Metric | Dense-only | Hybrid (RRF) |
| --- | ---: | ---: |
| `recall@10` | `0.69` | `0.84` |
| `nDCG@10` | `0.62` | `0.79` |

Judge agreement: 84%. Cache hit rate: 40%.

These come from the seeded evaluation data, not live traffic.

## recall@k

Fraction of known relevant chunks that appear in the top `k` retrieved.

```text
recall@k = relevant retrieved in top k / total relevant
```

Returns `0.0` when there are no relevant chunks. Duplicates are counted once (set-based). Implementation: `backend/app/retrieval/metrics.py`.

## nDCG@k

Ranking quality score — rewards placing relevant chunks higher.

```text
DCG@k  = sum(gain_at_rank / log2(rank + 1))
nDCG@k = DCG@k / ideal DCG@k
```

Uses raw relevance gains from the relevance map. Returns `0.0` when ideal DCG is zero.

## Reciprocal rank fusion

Merges dense top-30 and BM25 top-30:

```text
score(doc) = sum(1 / (60 + rank_in_source))
```

Inputs capped at 30 per source, duplicates by `chunk_id` deduplicated, final output is top 10 by fused score.

## Judge pass/fail

Each judge scores on three dimensions plus a boolean flag:

| Field | Range | Pass threshold |
| --- | --- | --- |
| `correctness` | 1–5 | ≥ 4 |
| `faithfulness` | 1–5 | ≥ 4 |
| `citation_quality` | 1–5 | ≥ 3 |
| `critical_unsupported_claim` | bool | must be `false` |

An answer passes only if all four conditions hold. Two judges score independently — if they disagree, the result routes to `manual_review`.

## Cache key generation

SHA-256 over canonical JSON covering: provider, model, prompt version, rendered messages, generation parameters, retrieval config, retrieved context checksum, tool schema hash, and judge rubric version. Same inputs always produce the same key.