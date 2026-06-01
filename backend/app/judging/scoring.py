from app.domain.models import JudgeReview, JudgeReviewStatus, JudgeScore


def build_judge_score(
    *,
    id: str,
    case_id: str,
    correctness: int,
    faithfulness: int,
    citation_quality: int,
    critical_unsupported_claim: bool,
    reason: str,
    judge_model: str,
) -> JudgeScore:
    _validate_score("correctness", correctness)
    _validate_score("faithfulness", faithfulness)
    _validate_score("citation_quality", citation_quality)

    passed = (
        correctness >= 4
        and faithfulness >= 4
        and citation_quality >= 3
        and not critical_unsupported_claim
    )

    return JudgeScore(
        id=id,
        case_id=case_id,
        correctness=correctness,
        faithfulness=faithfulness,
        citation_quality=citation_quality,
        critical_unsupported_claim=critical_unsupported_claim,
        passed=passed,
        reason=reason,
        judge_model=judge_model,
    )


def aggregate_two_judges(
    *,
    id: str,
    case_id: str,
    judge_a_score: JudgeScore,
    judge_b_score: JudgeScore,
) -> JudgeReview:
    judge_a_decision = judge_a_score.passed
    judge_b_decision = judge_b_score.passed
    agreement = judge_a_decision == judge_b_decision

    if not agreement:
        status = JudgeReviewStatus.MANUAL_REVIEW
    elif judge_a_decision:
        status = JudgeReviewStatus.PASSED
    else:
        status = JudgeReviewStatus.FAILED

    return JudgeReview(
        id=id,
        case_id=case_id,
        judge_a_score=judge_a_score,
        judge_b_score=judge_b_score,
        judge_a_decision=judge_a_decision,
        judge_b_decision=judge_b_decision,
        agreement=agreement,
        status=status,
    )


def _validate_score(name: str, value: int) -> None:
    if value < 1 or value > 5:
        raise ValueError(f"{name} must be between 1 and 5")
