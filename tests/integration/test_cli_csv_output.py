from pathlib import Path

from src.cli.translation_eval_cli import main


def test_cli_generates_csv(tmp_path: Path) -> None:
    out = tmp_path / "out.csv"
    rc = main(
        [
            "--lang",
            "ru",
            "--limit",
            "2",
            "--po-root",
            "tests/fixtures",
            "--xliff-root",
            "tests/fixtures",
            "--output",
            str(out),
        ]
    )
    assert rc == 0
    assert out.exists()
    content = out.read_text(encoding="utf-8")
    assert "msgid,source_en,ai_context,translation_text_po" in content
    assert "translation_text_xliff" in content

