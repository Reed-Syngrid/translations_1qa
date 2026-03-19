from src.core.file_discovery import discover_language_files, normalize_locale


def test_normalize_locale_basic() -> None:
    assert normalize_locale("ru") == "ru"
    assert normalize_locale("zh-cn") == "zh-CN"
    assert normalize_locale("pt_BR") == "pt-BR"


def test_discover_language_files_fallback_to_base(tmp_path) -> None:
    # Requested: es-ES, but only es.po is present in po_root.
    # XLIFF has metabase_es-ES.xliff and should be discovered as es-ES.
    po_root = tmp_path / "locales"
    xliff_root = tmp_path / "xliff"
    po_root.mkdir(parents=True, exist_ok=True)
    xliff_root.mkdir(parents=True, exist_ok=True)

    (po_root / "es.po").write_text("msgid \"x\"\nmsgstr \"y\"\n", encoding="utf-8")
    (xliff_root / "metabase_es-ES.xliff").write_text(
        "<xliff><file><body><trans-unit><source>x</source><target>y</target></trans-unit></body></file></xliff>",
        encoding="utf-8",
    )

    res = discover_language_files(str(po_root), str(xliff_root), "es-ES")
    assert any(p.endswith("es.po") for p in res.po_files)
    assert any(p.endswith("metabase_es-ES.xliff") for p in res.xliff_files)

