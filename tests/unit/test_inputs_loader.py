from __future__ import annotations

from pathlib import Path

import pytest

from src.core.inputs_loader import (
    _strip_blank_po,
    _strip_blank_xliff,
    discover_language_input_files,
    load_language_inputs,
)
from src.core.matching import shared_msgids


def test_strip_blank_po_removes_empty_and_whitespace() -> None:
    raw = {
        "a": "ok",
        "b": "",
        "c": "   ",
        "d": "\t\n",
    }
    assert _strip_blank_po(raw) == {"a": "ok"}


def test_strip_blank_xliff_removes_empty_target() -> None:
    raw = {
        "a": ("ok", "ctx"),
        "b": ("", "ctx"),
        "c": ("  ", "ctx"),
    }
    assert _strip_blank_xliff(raw) == {"a": ("ok", "ctx")}


def test_load_language_inputs_drops_blank_before_shared(tmp_path: Path) -> None:
    """Blank msgstr must not appear in maps so it cannot participate in shared_msgids."""
    lang = tmp_path / "ru"
    lang.mkdir(parents=True)
    (lang / "a.po").write_text(
        'msgid "only"\nmsgstr ""\n\nmsgid "shared"\nmsgstr "x"\n',
        encoding="utf-8",
    )
    (lang / "a.xliff").write_text(
        """<?xml version="1.0" encoding="UTF-8"?>
<xliff version="1.2"><file source-language="en" target-language="ru"><body>
<trans-unit id="1"><source>only</source><target>o</target></trans-unit>
<trans-unit id="2"><source>shared</source><target>x</target></trans-unit>
</body></file></xliff>
""",
        encoding="utf-8",
    )
    loaded = load_language_inputs(tmp_path, "ru")
    assert "only" not in loaded.po_map
    assert "only" in loaded.xliff_map
    shared = shared_msgids(loaded.po_map, loaded.xliff_map)
    assert shared == ["shared"]


def test_discover_language_input_files_missing_dir(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        discover_language_input_files(tmp_path, "missing")


def test_fixture_inputs_layout_runnable() -> None:
    """Integration-style check: fixtures/inputs/ru matches loader expectations."""
    root = Path(__file__).resolve().parent.parent / "fixtures" / "inputs"
    loaded = load_language_inputs(root, "ru")
    assert len(loaded.po_files) >= 1
    assert len(loaded.xliff_files) >= 1
    assert len(loaded.po_map) == 3
    assert len(shared_msgids(loaded.po_map, loaded.xliff_map)) == 3
