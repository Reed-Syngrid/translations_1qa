from __future__ import annotations

from collections.abc import Iterable


def _parse_fallback(content: str) -> dict[str, str]:
    result: dict[str, str] = {}
    current_msgid = None
    for line in content.splitlines():
        line = line.strip()
        if line.startswith('msgid "'):
            current_msgid = line[len('msgid "') : -1]
        elif line.startswith('msgstr "') and current_msgid is not None:
            msgstr = line[len('msgstr "') : -1]
            result[current_msgid] = msgstr
            current_msgid = None
    return result


def parse_po_file(path: str) -> dict[str, str]:
    try:
        import polib  # type: ignore

        po = polib.pofile(path)
        return {entry.msgid: entry.msgstr for entry in po if entry.msgid}
    except Exception:
        with open(path, "r", encoding="utf-8") as f:
            return _parse_fallback(f.read())


def merge_po_files(paths: Iterable[str]) -> dict[str, str]:
    merged: dict[str, str] = {}
    for p in paths:
        merged.update(parse_po_file(p))
    return merged

