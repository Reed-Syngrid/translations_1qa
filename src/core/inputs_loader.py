from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .file_discovery import normalize_locale
from .po_parser import merge_po_files
from .xliff_parser import merge_xliff_files


@dataclass(frozen=True)
class LanguageInputs:
    """Loaded translation maps for one language under ``inputs_root / language_code``."""

    language_code: str
    inputs_root: Path
    lang_dir: Path
    po_files: tuple[Path, ...]
    xliff_files: tuple[Path, ...]
    po_map: dict[str, str]
    xliff_map: dict[str, tuple[str, str]]


def _strip_blank_po(po_map: dict[str, str]) -> dict[str, str]:
    """Drop entries whose translation is empty or whitespace-only (FR-004 / FR-014)."""
    out: dict[str, str] = {}
    for msgid, msgstr in po_map.items():
        if msgstr is None:
            continue
        if str(msgstr).strip() == "":
            continue
        out[msgid] = msgstr
    return out


def _strip_blank_xliff(
    xliff_map: dict[str, tuple[str, str]],
) -> dict[str, tuple[str, str]]:
    """Drop trans-units whose target text is empty or whitespace-only."""
    out: dict[str, tuple[str, str]] = {}
    for source_key, (target, ctx) in xliff_map.items():
        if target is None:
            continue
        if str(target).strip() == "":
            continue
        out[source_key] = (target, ctx or "")
    return out


def discover_language_input_files(inputs_root: Path | str, language_code: str) -> tuple[list[Path], list[Path]]:
    """
    Find ``*.po`` and ``*.xliff`` files under ``inputs_root / {lang}/`` (case-insensitive suffix).
    ``language_code`` is normalized for display consistency; directory name should match repo layout (e.g. ``es-ES``).
    """
    root = Path(inputs_root)
    lang = normalize_locale(language_code)
    lang_dir = root / lang
    if not lang_dir.is_dir():
        raise FileNotFoundError(
            f"Language input directory does not exist: {lang_dir} "
            f"(resolved from inputs_root={root!s}, language_code={language_code!r})"
        )

    po_files: list[Path] = []
    xliff_files: list[Path] = []
    for path in sorted(lang_dir.iterdir()):
        if not path.is_file():
            continue
        lower = path.suffix.lower()
        if lower == ".po":
            po_files.append(path)
        elif lower == ".xliff":
            xliff_files.append(path)

    return po_files, xliff_files


def load_language_inputs(inputs_root: Path | str, language_code: str) -> LanguageInputs:
    """
    Load merged PO and XLIFF maps for ``language_code``, using UTF-8 in parsers.

    Blank translations (empty or whitespace-only) are removed **before** maps are returned,
    so downstream matching, sampling, and benchmark joins never see them.
    """
    root = Path(inputs_root)
    lang = normalize_locale(language_code)
    lang_dir = root / lang

    po_paths, xliff_paths = discover_language_input_files(root, language_code)

    po_str_paths = [str(p) for p in po_paths]
    xliff_str_paths = [str(p) for p in xliff_paths]

    raw_po = merge_po_files(po_str_paths) if po_str_paths else {}
    raw_xliff = merge_xliff_files(xliff_str_paths) if xliff_str_paths else {}

    po_map = _strip_blank_po(raw_po)
    xliff_map = _strip_blank_xliff(raw_xliff)

    return LanguageInputs(
        language_code=lang,
        inputs_root=root.resolve(),
        lang_dir=lang_dir.resolve(),
        po_files=tuple(po_paths),
        xliff_files=tuple(xliff_paths),
        po_map=po_map,
        xliff_map=xliff_map,
    )
