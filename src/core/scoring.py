from __future__ import annotations

from .ai_client import AIClient
from .checks import check_capitalization
from .models import EvaluationResult, TranslationCandidate


def evaluate_candidate(
    candidate: TranslationCandidate,
    ai_client: AIClient,
    *,
    accuracy_human: int | None = None,
) -> EvaluationResult:
    """
    Only **Accuracy** (AI or optional human) and **Capitalization** (FR-001).
    No naturalness, variables, or placeholder scoring.
    If `accuracy_human` is set (benchmark), it is the source of truth for the accuracy term.
    `final_score` is 1 iff both capitalization passes and that accuracy term is 1.
    """
    capitalization_score = check_capitalization(candidate.source_en, candidate.translation_text)
    accuracy_ai = ai_client.score_accuracy(candidate)
    accuracy_component = accuracy_human if accuracy_human is not None else accuracy_ai
    final_score = int(accuracy_component == 1 and capitalization_score == 1)
    return EvaluationResult(
        msgid=candidate.msgid,
        translation_source=candidate.translation_source,
        source_en=candidate.source_en,
        translation_text=candidate.translation_text,
        language_code=candidate.language_code,
        ai_context=candidate.ai_context,
        accuracy_ai=accuracy_ai,
        accuracy_human=accuracy_human,
        capitalization_score=capitalization_score,
        final_score=final_score,
    )
