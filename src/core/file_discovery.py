import os
import re
from dataclasses import dataclass

LANG_CANDIDATE_RE = re.compile(r"([a-z]{2,3}(?:[-_][A-Za-z]{2,4})?)")


@dataclass
class DiscoveryResult:
    po_files: list[str]
    xliff_files: list[str]
    po_debug: list[tuple[str, str]]
    xliff_debug: list[tuple[str, str]]


def normalize_locale(locale: str) -> str:
    raw = locale.replace("_", "-")
    parts = raw.split("-")
    if len(parts) == 1:
        return parts[0].lower()
    return f"{parts[0].lower()}-{parts[1].upper()}"


def _extract_lang_from_filename(path: str) -> str:
    name_no_ext = os.path.splitext(os.path.basename(path))[0]
    # Prefer suffix after last underscore, which matches Metabase patterns
    # like metabase_ru, metabase_es-ES, etc.
    token = name_no_ext.split("_")[-1]
    if not token:
        return ""
    return normalize_locale(token)


def _collect_files(root: str, extension: str) -> list[str]:
    out: list[str] = []
    for cur, _, files in os.walk(root):
        for file_name in files:
            if file_name.lower().endswith(extension):
                out.append(os.path.join(cur, file_name))
    return out


def discover_language_files(po_root: str, xliff_root: str, language_code: str) -> DiscoveryResult:
    target = normalize_locale(language_code)
    po_candidates = _collect_files(po_root, ".po")
    xliff_candidates = _collect_files(xliff_root, ".xliff")
    po_debug = [(p, _extract_lang_from_filename(p) or "<none>") for p in po_candidates]
    xliff_debug = [(p, _extract_lang_from_filename(p) or "<none>") for p in xliff_candidates]
    po_files = [p for p, code in po_debug if code == target]
    xliff_files = [p for p, code in xliff_debug if code == target]
    return DiscoveryResult(
        po_files=sorted(po_files),
        xliff_files=sorted(xliff_files),
        po_debug=po_debug,
        xliff_debug=xliff_debug,
    )

