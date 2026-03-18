from __future__ import annotations

import csv
import os
from collections.abc import Iterable

from .models import EvaluationResult

CSV_HEADERS = [
    "msgid",
    "source_en",
    "ai_context",
    "translation_text_po",
    "accuracy_score_po",
    "capitalization_score_po",
    "placeholder_score_po",
    "final_score_po",
    "translation_text_xliff",
    "accuracy_score_xliff",
    "capitalization_score_xliff",
    "placeholder_score_xliff",
    "final_score_xliff",
    "placeholder_diagnostics",
    "error_reason",
]


def write_results_csv(path: str, results: Iterable[EvaluationResult]) -> None:
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
            # If either side is missing, we still emit a row with what we have.
            source_en = (po or xliff).source_en if (po or xliff) else ""
            ai_context = (po or xliff).ai_context if (po or xliff) else ""

            def _vals(prefix: str, res: EvaluationResult | None) -> dict[str, str | int]:
                if res is None:
                    return {
                        f"translation_text_{prefix}": "",
                        f"accuracy_score_{prefix}": 0,
                        f"capitalization_score_{prefix}": 0,
                        f"placeholder_score_{prefix}": 0,
                        f"final_score_{prefix}": 0,
                    }
                return {
                    f"translation_text_{prefix}": res.translation_text,
                    f"accuracy_score_{prefix}": res.accuracy_score,
                    f"capitalization_score_{prefix}": res.capitalization_score,
                    f"placeholder_score_{prefix}": res.placeholder_score,
                    f"final_score_{prefix}": res.final_score,
                }

            row_dict: dict[str, str | int] = {
                "msgid": msgid,
                "source_en": source_en,
                "ai_context": ai_context,
            }
            row_dict.update(_vals("po", po))
            row_dict.update(_vals("xliff", xliff))
            # Combine diagnostics and errors from both sources, if present.
            diag_parts = []
            err_parts = []
            for label, res in (("po", po), ("xliff", xliff)):
                if res is None:
                    continue
                if res.placeholder_diagnostics:
                    diag_parts.append(f"{label}:{res.placeholder_diagnostics}")
                if res.error_reason:
                    err_parts.append(f"{label}:{res.error_reason}")
            row_dict["placeholder_diagnostics"] = ";".join(diag_parts)
            row_dict["error_reason"] = ";".join(err_parts)
            writer.writerow(row_dict)

