from __future__ import annotations

import csv
from pathlib import Path

import pytest

from src.core.benchmark import (
    BenchmarkLoadError,
    human_accuracy_for_source,
    load_benchmark_csv,
    stale_benchmark_msgids,
)
from src.core.models import BenchmarkRow


def test_load_benchmark_duplicate_msgid_fails(tmp_path: Path) -> None:
    p = tmp_path / "b.csv"
    header = [
        "msgid",
        "source_en",
        "ai_context",
        "translation_text_po",
        "accuracy_score_po",
        "Accurancy",
        "translation_text_xliff",
        "accuracy_score_xliff",
        "Accurancy",
    ]
    with open(p, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerow(["dup", "s", "", "t", "1", "", "t", "1", ""])
        w.writerow(["dup", "s", "", "t", "0", "", "t", "0", ""])
    with pytest.raises(BenchmarkLoadError, match="Duplicate msgid"):
        load_benchmark_csv(p)


def test_human_accuracy_for_source() -> None:
    row = BenchmarkRow(
        msgid="x",
        accuracy_human_po=1,
        accuracy_human_xliff=0,
    )
    assert human_accuracy_for_source(row, "po") == 1
    assert human_accuracy_for_source(row, "xliff") == 0
    assert human_accuracy_for_source(None, "po") is None


def test_stale_benchmark_msgids() -> None:
    b = {
        "a": BenchmarkRow("a", 1, 1),
        "orphan": BenchmarkRow("orphan", 0, 0),
    }
    stale = stale_benchmark_msgids(b, {"a"})
    assert stale == ["orphan"]
