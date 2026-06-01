from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import JudgeReviewStatus, ProviderKind, RunStatus, TraceStage


class DatasetSchema(BaseModel):
    id: str
    name: str
    description: str
    version: str
    case_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EvaluationCaseSchema(BaseModel):
    id: str
    dataset_id: str
    input_text: str
    expected_answer: str
    relevant_document_ids: list[str]
    tags: list[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ProviderConfigSchema(BaseModel):
    id: str
    name: str
    kind: ProviderKind
    model_name: str
    base_url: str | None = None
    uses_mock_responses: bool = True

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class JudgeScoreSchema(BaseModel):
    id: str
    case_id: str
    correctness: int = Field(ge=1, le=5)
    faithfulness: int = Field(ge=1, le=5)
    citation_quality: int = Field(ge=1, le=5)
    critical_unsupported_claim: bool
    passed: bool
    reason: str
    judge_model: str

    model_config = ConfigDict(from_attributes=True)


class JudgeReviewSchema(BaseModel):
    id: str
    case_id: str
    judge_a_score: JudgeScoreSchema
    judge_b_score: JudgeScoreSchema
    judge_a_decision: bool
    judge_b_decision: bool
    agreement: bool
    status: JudgeReviewStatus

    model_config = ConfigDict(from_attributes=True)


class EvaluationResultSchema(BaseModel):
    id: str
    run_id: str
    case_id: str
    provider_config_id: str
    answer: str
    latency_ms: int
    cache_hit: bool
    judge_score: JudgeScoreSchema
    judge_review: JudgeReviewSchema
    error: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EvaluationMetricsSchema(BaseModel):
    label: str = "controlled demo metrics"
    dense_only_recall_at_10: float
    hybrid_recall_at_10: float
    dense_only_ndcg_at_10: float
    hybrid_ndcg_at_10: float
    judge_agreement_percent: int
    cache_hit_rate_percent: int
    is_controlled_demo: bool = True


class EvaluationRunCreate(BaseModel):
    name: str = Field(default="Ad hoc demo evaluation run", min_length=1, max_length=120)
    dataset_id: str | None = Field(
        default=None,
        description="Optional dataset identifier. Demo storage currently seeds one default dataset.",
    )
    baseline_provider_id: str | None = None
    candidate_provider_id: str | None = None


class EvaluationRunSummary(BaseModel):
    id: str
    name: str
    status: RunStatus
    dataset: DatasetSchema
    baseline_provider: ProviderConfigSchema
    candidate_provider: ProviderConfigSchema
    metrics: EvaluationMetricsSchema
    created_at: datetime
    completed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class EvaluationRunDetail(EvaluationRunSummary):
    results: list[EvaluationResultSchema]


class TraceRecordSchema(BaseModel):
    id: str
    run_id: str
    case_id: str | None
    stage: TraceStage
    name: str
    started_at: datetime
    duration_ms: int
    attributes: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)
