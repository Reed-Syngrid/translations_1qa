from pathlib import Path

import pytest

from src.core.xliff_parser import parse_xliff_file


def test_malformed_xliff_raises_parse_error() -> None:
    with pytest.raises(Exception):
        parse_xliff_file(str(Path("tests/fixtures/malformed/broken.xliff")))

