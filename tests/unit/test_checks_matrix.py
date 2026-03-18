from src.core.checks import check_capitalization, check_placeholders


def test_placeholder_matrix_cases() -> None:
    assert check_placeholders("Value: %s", "Значение: %s")[0] == 1
    assert check_placeholders("Value: %1$s", "Значение: %1$s")[0] == 1
    assert check_placeholders("Value: ${name}", "Значение: ${name}")[0] == 1


def test_capitalization_matrix_cases() -> None:
    assert check_capitalization("Server Error", "Ошибка сервера") == 1
    assert check_capitalization("Server Error", "ошибка сервера") == 0

