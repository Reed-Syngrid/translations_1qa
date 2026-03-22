"""Smoke: CLI runs and CSV has expected accuracy columns (Phase 4 US2)."""

from __future__ import annotations

from pathlib import Path

from src.cli.translation_eval_cli import main


def test_cli_smoke_outputs_accuracy_columns(tmp_path: Path) -> None:
    out = tmp_path / "smoke.csv"
    rc = main(
        [
            "--lang",
            "ru",
            "--limit",
            "1",
            "--inputs-root",
            "tests/fixtures/inputs",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "accuracy_ai_po" in text
    assert "accuracy_human_po" in text
    assert "accuracy_ai_xliff" in text
