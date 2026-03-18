from src.core.checks import check_capitalization, check_placeholders


def test_check_capitalization() -> None:
    assert check_capitalization("Hello world", "Привет мир") == 1
    assert check_capitalization("Hello world", "привет мир") == 0


def test_check_placeholders() -> None:
    ok, diag = check_placeholders("Hello {name}", "Привет {name}")
    assert ok == 1
    assert diag == []

    ok2, diag2 = check_placeholders("Hello {name}", "Привет")
    assert ok2 == 0
    assert any("missing" in d for d in diag2)

