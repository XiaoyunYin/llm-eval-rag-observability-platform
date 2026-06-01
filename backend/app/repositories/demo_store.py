from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.domain.models import (
    Dataset,
    EvaluationCase,
    EvaluationResult,
    EvaluationRun,
    ProviderConfig,
    ProviderKind,
    RunStatus,
    TraceComponent,
    TraceRecord,
)
from app.judging.scoring import aggregate_two_judges, build_judge_score
from app.providers.base import ProviderRequest
from app.providers.mock import MockProvider
from app.schemas.evaluation import EvaluationRunCreate


DEMO_METRICS = {
    "label": "controlled demo metrics",
    "dense_only_recall_at_10": 0.69,
    "hybrid_recall_at_10": 0.84,
    "dense_only_ndcg_at_10": 0.62,
    "hybrid_ndcg_at_10": 0.79,
    "judge_agreement_percent": 84,
    "cache_hit_rate_percent": 40,
    "is_controlled_demo": True,
}


class DemoEvaluationStore:
    """Seeded in-memory store with a narrow boundary for future SQLAlchemy wiring."""

    def __init__(self) -> None:
        self._datasets: dict[str, Dataset] = {}
        self._cases: dict[str, EvaluationCase] = {}
        self._providers: dict[str, ProviderConfig] = {}
        self._runs: dict[str, EvaluationRun] = {}
        self._traces: dict[str, list[TraceRecord]] = {}
        self._seed()

    def list_runs(self) -> list[EvaluationRun]:
        return sorted(self._runs.values(), key=lambda run: run.created_at, reverse=True)

    def get_run(self, run_id: str) -> EvaluationRun | None:
        return self._runs.get(run_id)

    def list_traces(self, run_id: str) -> list[TraceRecord] | None:
        if run_id not in self._runs:
            return None
        return self._traces.get(run_id, [])

    def create_run(self, payload: EvaluationRunCreate) -> EvaluationRun:
        dataset = self._datasets.get(payload.dataset_id or "demo-dataset-001")
        if dataset is None:
            dataset = next(iter(self._datasets.values()))

        baseline = self._providers.get(payload.baseline_provider_id or "provider-dense-only")
        candidate = self._providers.get(payload.candidate_provider_id or "provider-hybrid-rag")

        if baseline is None:
            baseline = self._providers["provider-dense-only"]
        if candidate is None:
            candidate = self._providers["provider-hybrid-rag"]

        now = datetime.now(timezone.utc)
        run_id = f"run-{uuid4().hex[:12]}"
        results = self._build_results(run_id, candidate.id)
        run = EvaluationRun(
            id=run_id,
            name=payload.name,
            dataset=dataset,
            baseline_provider=baseline,
            candidate_provider=candidate,
            status=RunStatus.COMPLETED,
            metrics=deepcopy(DEMO_METRICS),
            results=results,
            created_at=now,
            completed_at=now + timedelta(seconds=18),
        )

        self._runs[run.id] = run
        self._traces[run.id] = self._build_traces(run.id, now)
        return run

    def _seed(self) -> None:
        created_at = datetime(2026, 5, 31, 20, 0, tzinfo=timezone.utc)
        dataset = Dataset(
            id="demo-dataset-001",
            name="Customer support RAG evaluation set",
            description="Seeded questions and relevance labels for a controlled demo workload.",
            version="2026.05-demo",
            case_count=3,
            created_at=created_at,
        )
        self._datasets[dataset.id] = dataset

        cases = [
            EvaluationCase(
                id="case-001",
                dataset_id=dataset.id,
                input_text="How do I rotate an API key without downtime?",
                expected_answer="Create a second key, deploy it, then revoke the old key after traffic moves.",
                relevant_document_ids=["doc-auth-rotate", "doc-auth-secrets"],
                tags=["security", "runbook"],
            ),
            EvaluationCase(
                id="case-002",
                dataset_id=dataset.id,
                input_text="What should I check when retrieval quality drops?",
                expected_answer="Inspect embeddings, BM25 coverage, document freshness, and fusion weights.",
                relevant_document_ids=["doc-rag-debug", "doc-index-health"],
                tags=["rag", "observability"],
            ),
            EvaluationCase(
                id="case-003",
                dataset_id=dataset.id,
                input_text="How are failed provider calls represented?",
                expected_answer="Store them as explicit failed results with error context and trace links.",
                relevant_document_ids=["doc-provider-errors"],
                tags=["providers", "traces"],
            ),
        ]
        self._cases.update({case.id: case for case in cases})

        dense_provider = ProviderConfig(
            id="provider-dense-only",
            name="Dense-only retriever baseline",
            kind=ProviderKind.MOCK,
            model_name="mock-dense-baseline",
        )
        hybrid_provider = ProviderConfig(
            id="provider-hybrid-rag",
            name="Hybrid RAG candidate",
            kind=ProviderKind.MOCK,
            model_name="mock-hybrid-rag-candidate",
        )
        self._providers[dense_provider.id] = dense_provider
        self._providers[hybrid_provider.id] = hybrid_provider

        run = EvaluationRun(
            id="run-demo-001",
            name="Controlled demo: dense baseline vs hybrid RAG",
            dataset=dataset,
            baseline_provider=dense_provider,
            candidate_provider=hybrid_provider,
            status=RunStatus.COMPLETED,
            metrics=deepcopy(DEMO_METRICS),
            results=self._build_results("run-demo-001", hybrid_provider.id),
            created_at=created_at + timedelta(minutes=5),
            completed_at=created_at + timedelta(minutes=5, seconds=18),
        )
        self._runs[run.id] = run
        self._traces[run.id] = self._build_traces(run.id, run.created_at)

    def _build_results(self, run_id: str, provider_config_id: str) -> list[EvaluationResult]:
        provider = MockProvider(model="mock-hybrid-rag-candidate")
        case_001_judge_a = build_judge_score(
            id=f"{run_id}-judge-a-001",
            case_id="case-001",
            correctness=5,
            faithfulness=5,
            citation_quality=4,
            critical_unsupported_claim=False,
            reason="Answer covers staged rotation and revocation order.",
            judge_model="mock-judge-a-v1",
        )
        case_001_judge_b = build_judge_score(
            id=f"{run_id}-judge-b-001",
            case_id="case-001",
            correctness=5,
            faithfulness=4,
            citation_quality=4,
            critical_unsupported_claim=False,
            reason="Answer is faithful and cites the expected operational order.",
            judge_model="mock-judge-b-v1",
        )
        case_002_judge_a = build_judge_score(
            id=f"{run_id}-judge-a-002",
            case_id="case-002",
            correctness=4,
            faithfulness=4,
            citation_quality=3,
            critical_unsupported_claim=False,
            reason="Answer names the main retrieval diagnostics expected by the rubric.",
            judge_model="mock-judge-a-v1",
        )
        case_002_judge_b = build_judge_score(
            id=f"{run_id}-judge-b-002",
            case_id="case-002",
            correctness=4,
            faithfulness=4,
            citation_quality=3,
            critical_unsupported_claim=False,
            reason="Answer meets the minimum pass thresholds.",
            judge_model="mock-judge-b-v1",
        )
        case_003_judge_a = build_judge_score(
            id=f"{run_id}-judge-a-003",
            case_id="case-003",
            correctness=4,
            faithfulness=4,
            citation_quality=3,
            critical_unsupported_claim=False,
            reason="Answer captures explicit failure storage but omits retry metadata.",
            judge_model="mock-judge-a-v1",
        )
        case_003_judge_b = build_judge_score(
            id=f"{run_id}-judge-b-003",
            case_id="case-003",
            correctness=4,
            faithfulness=4,
            citation_quality=3,
            critical_unsupported_claim=False,
            reason="Answer is acceptable for the controlled demo rubric.",
            judge_model="mock-judge-b-v1",
        )

        return [
            EvaluationResult(
                id=f"{run_id}-result-001",
                run_id=run_id,
                case_id="case-001",
                provider_config_id=provider_config_id,
                answer=self._mock_answer(
                    provider,
                    "How do I rotate an API key without downtime?",
                    fallback="Use a staged key rotation: create, deploy, verify, then revoke the old key.",
                ),
                latency_ms=812,
                cache_hit=True,
                judge_score=case_001_judge_a,
                judge_review=aggregate_two_judges(
                    id=f"{run_id}-judge-review-001",
                    case_id="case-001",
                    judge_a_score=case_001_judge_a,
                    judge_b_score=case_001_judge_b,
                ),
            ),
            EvaluationResult(
                id=f"{run_id}-result-002",
                run_id=run_id,
                case_id="case-002",
                provider_config_id=provider_config_id,
                answer=self._mock_answer(
                    provider,
                    "What should I check when retrieval quality drops?",
                    fallback="Check dense retrieval, BM25 coverage, source freshness, and RRF weighting.",
                ),
                latency_ms=1044,
                cache_hit=False,
                judge_score=case_002_judge_a,
                judge_review=aggregate_two_judges(
                    id=f"{run_id}-judge-review-002",
                    case_id="case-002",
                    judge_a_score=case_002_judge_a,
                    judge_b_score=case_002_judge_b,
                ),
            ),
            EvaluationResult(
                id=f"{run_id}-result-003",
                run_id=run_id,
                case_id="case-003",
                provider_config_id=provider_config_id,
                answer=self._mock_answer(
                    provider,
                    "How are failed provider calls represented?",
                    fallback="Provider failures are persisted as explicit results with error and trace metadata.",
                ),
                latency_ms=677,
                cache_hit=False,
                judge_score=case_003_judge_a,
                judge_review=aggregate_two_judges(
                    id=f"{run_id}-judge-review-003",
                    case_id="case-003",
                    judge_a_score=case_003_judge_a,
                    judge_b_score=case_003_judge_b,
                ),
            ),
        ]

    def _mock_answer(self, provider: MockProvider, question: str, *, fallback: str) -> str:
        response = provider.generate(
            ProviderRequest(
                messages=[
                    {"role": "system", "content": "Answer with concise operational guidance."},
                    {"role": "user", "content": question},
                ],
                generation_parameters={"temperature": 0.0, "max_tokens": 256},
            )
        )
        return response.text or fallback

    def _build_traces(self, run_id: str, base_time: datetime) -> list[TraceRecord]:
        provider = "mock"
        model = "mock-hybrid-rag-candidate"
        return [
            TraceRecord(
                id=f"{run_id}-trace-001",
                run_id=run_id,
                case_id="case-001",
                component=TraceComponent.GATEWAY,
                provider=provider,
                model=model,
                cache_status="not_applicable",
                latency_ms=8,
                token_count=0,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=1),
                attributes={"route": "provider_gateway.generate", "provider_mode": "mock"},
            ),
            TraceRecord(
                id=f"{run_id}-trace-002",
                run_id=run_id,
                case_id="case-001",
                component=TraceComponent.CACHE,
                provider=provider,
                model=model,
                cache_status="hit",
                latency_ms=14,
                token_count=0,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=2),
                attributes={"cache_key_shape": "provider:model:prompt:retrieval:context:tools:judge"},
            ),
            TraceRecord(
                id=f"{run_id}-trace-003",
                run_id=run_id,
                case_id="case-002",
                component=TraceComponent.RETRIEVAL,
                provider=provider,
                model=model,
                cache_status="miss",
                latency_ms=143,
                token_count=0,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=5),
                attributes={"dense_top_k": 30, "bm25_top_k": 30, "fusion": "rrf", "rrf_k": 60},
            ),
            TraceRecord(
                id=f"{run_id}-trace-004",
                run_id=run_id,
                case_id="case-002",
                component=TraceComponent.PROVIDER,
                provider=provider,
                model=model,
                cache_status="miss",
                latency_ms=48,
                token_count=96,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=7),
                attributes={"provider_class": "MockProvider", "default_demo_provider": True},
            ),
            TraceRecord(
                id=f"{run_id}-trace-005",
                run_id=run_id,
                case_id="case-003",
                component=TraceComponent.JUDGE,
                provider=provider,
                model="mock-judge-a-v1",
                cache_status="not_applicable",
                latency_ms=231,
                token_count=128,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=12),
                attributes={"judge_a_decision": True, "judge_b_decision": True, "agreement": True},
            ),
            TraceRecord(
                id=f"{run_id}-trace-006",
                run_id=run_id,
                case_id="case-001",
                component=TraceComponent.TOOL,
                provider=provider,
                model=model,
                cache_status="not_applicable",
                latency_ms=33,
                token_count=0,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=14),
                attributes={"tool_name": "lookup_runbook", "tool_schema_hash": "seeded-demo"},
            ),
            TraceRecord(
                id=f"{run_id}-trace-007",
                run_id=run_id,
                case_id=None,
                component=TraceComponent.STORAGE,
                provider=provider,
                model=model,
                cache_status="not_applicable",
                latency_ms=19,
                token_count=0,
                estimated_cost=0.0,
                error_type=None,
                status="ok",
                started_at=base_time + timedelta(seconds=16),
                attributes={"storage_target": "in_memory_demo_store", "future_target": "postgresql"},
            ),
        ]
