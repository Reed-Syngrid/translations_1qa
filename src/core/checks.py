from __future__ import annotations

import re

PLACEHOLDER_PATTERNS = [
    r"%\d+\$[sdif]",
    r"%[sdif]",
    r"\{[a-zA-Z0-9_]+\}",
    r"\$\{[a-zA-Z0-9_]+\}",
]


def _first_alpha_char(text: str) -> str:
    for ch in text:
        if ch.isalpha():
            return ch
    return ""


def check_capitalization(source_en: str, translation_text: str) -> int:
    source_char = _first_alpha_char(source_en)
    target_char = _first_alpha_char(translation_text)
    if not source_char or not target_char:
        return 1
    return int(source_char.isupper() == target_char.isupper())


def _extract_placeholders(text: str) -> set[str]:
    placeholders: set[str] = set()
    for pattern in PLACEHOLDER_PATTERNS:
        placeholders.update(re.findall(pattern, text))
    return placeholders


def check_placeholders(source_en: str, translation_text: str) -> tuple[int, list[str]]:
    source_set = _extract_placeholders(source_en)
    target_set = _extract_placeholders(translation_text)
    missing = sorted(source_set - target_set)
    extra = sorted(target_set - source_set)
    diagnostics: list[str] = []
    if missing:
        diagnostics.append(f"missing={','.join(missing)}")
    if extra:
        diagnostics.append(f"extra={','.join(extra)}")
    return int(source_set == target_set), diagnostics

