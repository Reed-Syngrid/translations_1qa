from src.core.file_discovery import normalize_locale


def test_normalize_locale_basic() -> None:
    assert normalize_locale("ru") == "ru"
    assert normalize_locale("zh-cn") == "zh-CN"
    assert normalize_locale("pt_BR") == "pt-BR"

