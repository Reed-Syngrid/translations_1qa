from __future__ import annotations

from .ai_client import AIClient
from .checks import check_capitalization, check_placeholders
from .models import EvaluationResult, TranslationCandidate


def evaluate_candidate(candidate: TranslationCandidate, ai_client: AIClient) -> EvaluationResult:
    capitalization_score = check_capitalization(candidate.source_en, candidate.translation_text)
    placeholder_score, placeholder_diagnostics = check_placeholders(
        candidate.source_en, candidate.translation_text
    )
    accuracy_score = ai_client.score_accuracy(candidate)
    final_score = int(
        accuracy_score == 1
        and capitalization_score == 1
        and placeholder_score == 1
    )
    return EvaluationResult(
        msgid=candidate.msgid,
        translation_source=candidate.translation_source,
        source_en=candidate.source_en,
        translation_text=candidate.translation_text,
        language_code=candidate.language_code,
        ai_context=candidate.ai_context,
        accuracy_score=accuracy_score,
        capitalization_score=capitalization_score,
        placeholder_score=placeholder_score,
        final_score=final_score,
        placeholder_diagnostics=";".join(placeholder_diagnostics),
    )

