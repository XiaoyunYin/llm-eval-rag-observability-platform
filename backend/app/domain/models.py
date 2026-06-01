from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ProviderKind(StrEnum):
    MOCK = "mock"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    VLLM = "vllm"


class TraceStage(StrEnum):
    RETRIEVAL = "retrieval"
    GENERATION = "generation"
    JUDGE = "judge"
    CACHE = "cache"
    API = "api"


class JudgeReviewStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    MANUAL_REVIEW = "manual_review"


@dataclass(frozen=True)
class Dataset:
    id: str
    name: str
    description: str
    version: str
    case_count: int
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class EvaluationCase:
    id: str
    dataset_id: str
    input_text: str
    expected_answer: str
    relevant_document_ids: list[str]
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ProviderConfig:
    id: str
    name: str
    kind: ProviderKind
    model_name: str
    base_url: str | None = None
    uses_mock_responses: bool = True


@dataclass(frozen=True)
class JudgeScore:
    id: str
    case_id: str
    correctness: int
    faithfulness: int
    citation_quality: int
    critical_unsupported_claim: bool
    passed: bool
    reason: str
    judge_model: str


@dataclass(frozen=True)
class JudgeReview:
    id: str
    case_id: str
    judge_a_score: JudgeScore
    judge_b_score: JudgeScore
    judge_a_decision: bool
    judge_b_decision: bool
    agreement: bool
    status: JudgeReviewStatus


@dataclass(frozen=True)
class EvaluationResult:
    id: str
    run_id: str
    case_id: str
    provider_config_id: str
    answer: str
    latency_ms: int
    cache_hit: bool
    judge_score: JudgeScore
    judge_review: JudgeReview
    error: str | None = None


@dataclass(frozen=True)
class TraceRecord:
    id: str
    run_id: str
    case_id: str | None
    stage: TraceStage
    name: str
    started_at: datetime
    duration_ms: int
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EvaluationRun:
    id: str
    name: str
    dataset: Dataset
    baseline_provider: ProviderConfig
    candidate_provider: ProviderConfig
    status: RunStatus
    metrics: dict[str, float | int | str | bool]
    results: list[EvaluationResult]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None
