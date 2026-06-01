# AGENTS.md

## Goal

Build a minimal recruiter-facing portfolio implementation of an LLM Evaluation, RAG & Observability Platform.

This is not a production system. Prioritize readable architecture, runnable local demo, tests for core logic, and strong documentation.

## Tech stack

Backend:
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Redis
- Elasticsearch
- pytest

Frontend:
- React
- TypeScript
- Vite

Infra:
- Docker Compose

## Scope

Use mock providers by default so the project runs without OpenAI, Anthropic, or AWS keys.

Optional adapters may support:
- OpenAI
- Anthropic
- vLLM OpenAI-compatible endpoint

Do not hardcode secrets.
Do not invent production claims.
Do not claim live production traffic.
Do not claim production deployment.

## Recruiter scan goal

A recruiter or engineer should understand the project in 60 seconds.

The repo should clearly demonstrate:
- FastAPI evaluation backend
- baseline vs candidate evaluation runs
- hybrid RAG with dense retrieval + BM25 + reciprocal rank fusion
- recall@10 and nDCG@10 calculation
- Redis-style cache-key correctness
- judge scoring and pass/fail aggregation
- provider gateway abstraction
- OpenTelemetry-style trace records
- Elasticsearch-style trace search
- lightweight React dashboard

## Testing expectations

Add tests for:
- RRF ranking
- recall@10
- nDCG@10
- cache key generation
- judge pass/fail aggregation
- provider failure stored as explicit result

## Documentation rules

README must include:
- project summary
- architecture diagram
- local run instructions
- resume claim mapping
- metrics explanation
- limitations and honest scope

Use wording such as:
"minimal portfolio implementation"
"controlled demo workload"
"mock providers by default"
"not production infrastructure"