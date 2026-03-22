from __future__ import annotations

from unittest.mock import MagicMock

from src.core.models import EvaluationResult, TranslationCandidate
from src.core.scoring import evaluate_candidate


def test_final_score_uses_ai_when_no_human() -> None:
    ai = MagicMock()
    ai.score_accuracy.return_value = 1
    c = TranslationCandidate(
        msgid="Hello",
        source_en="Hello",
        translation_source="po",
        translation_text="Привет",
        ai_context="",
        language_code="ru",
    )
    r = evaluate_candidate(c, ai, accuracy_human=None)
    assert isinstance(r, EvaluationResult)
    assert r.accuracy_ai == 1
    assert r.accuracy_human is None
    assert r.capitalization_score in (0, 1)
    assert r.final_score == int(r.accuracy_ai == 1 and r.capitalization_score == 1)


def test_human_overrides_ai_for_final_score() -> None:
    ai = MagicMock()
    ai.score_accuracy.return_value = 1
    c = TranslationCandidate(
        msgid="Hello",
        source_en="Hello",
        translation_source="po",
        translation_text="Привет",
        ai_context="",
        language_code="ru",
    )
    r = evaluate_candidate(c, ai, accuracy_human=0)
    assert r.accuracy_ai == 1
    assert r.accuracy_human == 0
    assert r.final_score == 0
