from __future__ import annotations

from src.core.models import EvaluationResult
from src.core.summary_report import find_critical_discrepancies


def test_find_critical_discrepancies_ai_vs_human() -> None:
    results = [
        EvaluationResult(
            msgid="a",
            translation_source="po",
            source_en="a",
            translation_text="t",
            language_code="ru",
            ai_context="",
            accuracy_ai=1,
            accuracy_human=0,
            capitalization_score=1,
            final_score=0,
        ),
        EvaluationResult(
            msgid="b",
            translation_source="xliff",
            source_en="b",
            translation_text="t",
            language_code="ru",
            ai_context="",
            accuracy_ai=1,
            accuracy_human=1,
            capitalization_score=1,
            final_score=1,
        ),
    ]
    crit = find_critical_discrepancies(results)
    assert len(crit) == 1
    assert crit[0][0] == "a"
