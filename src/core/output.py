from __future__ import annotations

"""
CSV export: one row per msgid with PO vs XLIFF columns.
`accuracy_ai_*` and `accuracy_human_*` side-by-side; `final_score_*` reflects human-over-AI rule.
This module only writes the given path; it never deletes other files (FR-005).
"""

import csv
import os
from collections.abc import Iterable

from .models import EvaluationResult

CSV_HEADERS = [
    "msgid",
    "source_en",
    "ai_context",
    "translation_text_po",
    "accuracy_ai_po",
    "accuracy_human_po",
    "capitalization_score_po",
    "final_score_po",
    "translation_text_xliff",
    "accuracy_ai_xliff",
    "accuracy_human_xliff",
    "capitalization_score_xliff",
    "final_score_xliff",
    "error_reason",
]


def write_results_csv(path: str, results: Iterable[EvaluationResult]) -> None:
    """Write results to ``path`` only; does not remove or truncate other CSVs in ``outputs/``."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    grouped: dict[str, dict[str, EvaluationResult]] = {}
    for row in results:
        grouped.setdefault(row.msgid, {})[row.translation_source] = row

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for msgid, per_source in grouped.items():
            po = per_source.get("po")
            xliff = per_source.get("xliff")
            source_en = (po or xliff).source_en if (po or xliff) else ""
            ai_context = (po or xliff).ai_context if (po or xliff) else ""

            def _vals(prefix: str, res: EvaluationResult | None) -> dict[str, str | int]:
                if res is None:
                    return {
                        f"translation_text_{prefix}": "",
                        f"accuracy_ai_{prefix}": 0,
                        f"accuracy_human_{prefix}": "",
                        f"capitalization_score_{prefix}": 0,
                        f"final_score_{prefix}": 0,
                    }
                human = res.accuracy_human
                human_cell: str | int = "" if human is None else human
                return {
                    f"translation_text_{prefix}": res.translation_text,
                    f"accuracy_ai_{prefix}": res.accuracy_ai,
                    f"accuracy_human_{prefix}": human_cell,
                    f"capitalization_score_{prefix}": res.capitalization_score,
                    f"final_score_{prefix}": res.final_score,
                }

            row_dict: dict[str, str | int] = {
                "msgid": msgid,
                "source_en": source_en,
                "ai_context": ai_context,
            }
            row_dict.update(_vals("po", po))
            row_dict.update(_vals("xliff", xliff))
            err_parts = []
            for label, res in (("po", po), ("xliff", xliff)):
                if res is None:
                    continue
                if res.error_reason:
                    err_parts.append(f"{label}:{res.error_reason}")
            row_dict["error_reason"] = ";".join(err_parts)
            writer.writerow(row_dict)
