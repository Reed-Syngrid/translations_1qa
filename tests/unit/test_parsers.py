from pathlib import Path

from src.core.po_parser import parse_po_file
from src.core.xliff_parser import parse_xliff_file


def test_parse_po_file() -> None:
    data = parse_po_file(str(Path("tests/fixtures/sample.po")))
    assert "Error contents" in data
    assert data["Hello {name}"] == "Привет {name}"


def test_parse_xliff_file() -> None:
    data = parse_xliff_file(str(Path("tests/fixtures/sample.xliff")))
    assert "Error contents" in data
    target, context = data["Error contents"]
    assert target == "Содержимое ошибки"
    assert "filter input placeholder" in context

