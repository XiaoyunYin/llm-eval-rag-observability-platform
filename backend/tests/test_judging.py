import pytest

from app.domain.models import JudgeReviewStatus
from app.judging.scoring import aggregate_two_judges, build_judge_score


def passing_score(id: str = "judge-a"):
    return build_judge_score(
        id=id,
        case_id="case-001",
        correctness=4,
        faithfulness=4,
        citation_quality=3,
        critical_unsupported_claim=False,
        reason="Meets rubric thresholds.",
        judge_model="mock-judge",
    )


def test_score_passes_at_exact_thresholds() -> None:
    score = passing_score()

    assert score.passed is True


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("correctness", 3),
        ("faithfulness", 3),
        ("citation_quality", 2),
    ],
)
def test_score_fails_when_any_numeric_threshold_is_missed(field_name: str, value: int) -> None:
    kwargs = {
        "id": "judge-a",
        "case_id": "case-001",
        "correctness": 4,
        "faithfulness": 4,
        "citation_quality": 3,
        "critical_unsupported_claim": False,
        "reason": "One threshold is below pass criteria.",
        "judge_model": "mock-judge",
    }
    kwargs[field_name] = value

    score = build_judge_score(**kwargs)

    assert score.passed is False


def test_score_fails_on_critical_unsupported_claim() -> None:
    score = build_judge_score(
        id="judge-a",
        case_id="case-001",
        correctness=5,
        faithfulness=5,
        citation_quality=5,
        critical_unsupported_claim=True,
        reason="Contains a critical unsupported claim.",
        judge_model="mock-judge",
    )

    assert score.passed is False


@pytest.mark.parametrize("field_name", ["correctness", "faithfulness", "citation_quality"])
def test_score_rejects_values_outside_one_to_five(field_name: str) -> None:
    kwargs = {
        "id": "judge-a",
        "case_id": "case-001",
        "correctness": 4,
        "faithfulness": 4,
        "citation_quality": 3,
        "critical_unsupported_claim": False,
        "reason": "Invalid score.",
        "judge_model": "mock-judge",
    }
    kwargs[field_name] = 6

    with pytest.raises(ValueError, match="must be between 1 and 5"):
        build_judge_score(**kwargs)


def test_two_judge_agreement_passes_when_both_pass() -> None:
    review = aggregate_two_judges(
        id="review-001",
        case_id="case-001",
        judge_a_score=passing_score("judge-a"),
        judge_b_score=passing_score("judge-b"),
    )

    assert review.judge_a_decision is True
    assert review.judge_b_decision is True
    assert review.agreement is True
    assert review.status == JudgeReviewStatus.PASSED


def test_two_judge_agreement_fails_when_both_fail() -> None:
    failing_a = build_judge_score(
        id="judge-a",
        case_id="case-001",
        correctness=3,
        faithfulness=4,
        citation_quality=3,
        critical_unsupported_claim=False,
        reason="Correctness below pass threshold.",
        judge_model="mock-judge-a",
    )
    failing_b = build_judge_score(
        id="judge-b",
        case_id="case-001",
        correctness=4,
        faithfulness=3,
        citation_quality=3,
        critical_unsupported_claim=False,
        reason="Faithfulness below pass threshold.",
        judge_model="mock-judge-b",
    )

    review = aggregate_two_judges(
        id="review-001",
        case_id="case-001",
        judge_a_score=failing_a,
        judge_b_score=failing_b,
    )

    assert review.agreement is True
    assert review.status == JudgeReviewStatus.FAILED


def test_two_judge_disagreement_routes_to_manual_review() -> None:
    failing = build_judge_score(
        id="judge-b",
        case_id="case-001",
        correctness=4,
        faithfulness=4,
        citation_quality=2,
        critical_unsupported_claim=False,
        reason="Citation quality below pass threshold.",
        judge_model="mock-judge-b",
    )

    review = aggregate_two_judges(
        id="review-001",
        case_id="case-001",
        judge_a_score=passing_score("judge-a"),
        judge_b_score=failing,
    )

    assert review.judge_a_decision is True
    assert review.judge_b_decision is False
    assert review.agreement is False
    assert review.status == JudgeReviewStatus.MANUAL_REVIEW
