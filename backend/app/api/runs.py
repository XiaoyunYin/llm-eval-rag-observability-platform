from fastapi import APIRouter, HTTPException, status

from app.repositories.demo_store import DemoEvaluationStore
from app.schemas.evaluation import (
    EvaluationRunCreate,
    EvaluationRunDetail,
    EvaluationRunSummary,
    TraceRecordSchema,
)

router = APIRouter(prefix="/api/runs", tags=["evaluation runs"])
store = DemoEvaluationStore()


@router.post("", response_model=EvaluationRunDetail, status_code=status.HTTP_201_CREATED)
def create_run(payload: EvaluationRunCreate) -> EvaluationRunDetail:
    """Create a completed demo run using seeded data and controlled demo metrics."""

    return EvaluationRunDetail.model_validate(store.create_run(payload))


@router.get("", response_model=list[EvaluationRunSummary])
def list_runs() -> list[EvaluationRunSummary]:
    """List seeded and user-created demo evaluation runs."""

    return [EvaluationRunSummary.model_validate(run) for run in store.list_runs()]


@router.get("/{run_id}", response_model=EvaluationRunDetail)
def get_run(run_id: str) -> EvaluationRunDetail:
    """Fetch a run with result rows and judge scores."""

    run = store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return EvaluationRunDetail.model_validate(run)


@router.get("/{run_id}/traces", response_model=list[TraceRecordSchema])
def list_run_traces(run_id: str) -> list[TraceRecordSchema]:
    """Fetch OpenTelemetry-style trace records for a demo run."""

    traces = store.list_traces(run_id)
    if traces is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Run not found")
    return [TraceRecordSchema.model_validate(trace) for trace in traces]
