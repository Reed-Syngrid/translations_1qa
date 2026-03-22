"""CLI rejects --use-benchmark unless language is Russian."""

from src.cli.translation_eval_cli import main


def test_use_benchmark_requires_ru() -> None:
    rc = main(["--lang", "de", "--limit", "1", "--inputs-root", "tests/fixtures/inputs", "--use-benchmark"])
    assert rc == 2
