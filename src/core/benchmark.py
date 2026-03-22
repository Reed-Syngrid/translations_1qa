"""
Load human benchmark CSV keyed by msgid. Duplicate msgids cause immediate failure.
"""

from __future__ import annotations

import csv
from pathlib import Path

from .models import BenchmarkRow

# Expected export shape (see inputs/ru/... benchmark file).
# Duplicate column name "Accurancy" breaks DictReader — use fixed indices.
COL_MSGID = 0
COL_ACCURACY_SCORE_PO = 4
COL_ACCURACY_SCORE_XLIFF = 7


class BenchmarkLoadError(Exception):
    """Raised when the benchmark file is invalid."""


def _parse_score_cell(cell: str) -> int | None:
    """Return 0/1 from the score column, or None if empty / unparsable."""
    s = (cell or "").strip()
    if s == "":
        return None
    try:
        v = int(float(s))
        if v in (0, 1):
            return v
    except ValueError:
        pass
    return None


def resolve_benchmark_csv_path(lang_dir: Path) -> Path:
    """Prefer canonical name; fall back to legacy export filename in repo."""
    canonical = lang_dir / "benchmark_ru_human_eval.csv"
    if canonical.is_file():
        return canonical
    legacy = lang_dir / "Benchmark_ru_human_eval - Sheet1.csv"
    if legacy.is_file():
        return legacy
    return canonical


def load_benchmark_csv(path: Path) -> dict[str, BenchmarkRow]:
    """
    Load benchmark rows keyed by msgid.
    Fails fast if the same msgid appears twice.
    """
    if not path.is_file():
        raise BenchmarkLoadError(f"Benchmark file not found: {path}")

    out: dict[str, BenchmarkRow] = {}
    first_line: dict[str, int] = {}

    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        try:
            next(reader)
        except StopIteration:
            raise BenchmarkLoadError(f"Benchmark file is empty: {path}")

        row_num = 2
        for row in reader:
            if not row:
                row_num += 1
                continue
            if len(row) <= max(COL_ACCURACY_SCORE_PO, COL_ACCURACY_SCORE_XLIFF):
                row_num += 1
                continue
            msgid = row[COL_MSGID]
            if msgid in out:
                raise BenchmarkLoadError(
                    f"Duplicate msgid in benchmark (fail fast): {msgid!r} "
                    f"first at line {first_line[msgid]}, duplicate at line {row_num}"
                )
            acc_po = _parse_score_cell(row[COL_ACCURACY_SCORE_PO])
            acc_xliff = _parse_score_cell(row[COL_ACCURACY_SCORE_XLIFF])
            out[msgid] = BenchmarkRow(
                msgid=msgid,
                accuracy_human_po=acc_po,
                accuracy_human_xliff=acc_xliff,
            )
            first_line[msgid] = row_num
            row_num += 1

    return out


def human_accuracy_for_source(row: BenchmarkRow | None, translation_source: str) -> int | None:
    """Pick PO or XLIFF human score from a benchmark row."""
    if row is None:
        return None
    if translation_source == "po":
        return row.accuracy_human_po
    if translation_source == "xliff":
        return row.accuracy_human_xliff
    return None


def stale_benchmark_msgids(
    benchmark: dict[str, BenchmarkRow],
    input_msgids: set[str],
) -> list[str]:
    """Benchmark msgids that do not appear in current inputs (after cleaning)."""
    return sorted(m for m in benchmark if m not in input_msgids)
