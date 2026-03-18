from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from collections.abc import Iterable

AI_CONTEXT_RE = re.compile(r"✨ AI Context(?P<context>.*?)✨ 🔚", re.DOTALL)


def _strip_ns(tag: str) -> str:
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _find_child_text(node: ET.Element, target: str) -> str:
    for child in node:
        if _strip_ns(child.tag) == target:
            return (child.text or "").strip()
    return ""


def _extract_ai_context(trans_unit: ET.Element) -> str:
    context_texts: list[str] = []
    for node in trans_unit.iter():
        if _strip_ns(node.tag) == "context":
            text = "".join(node.itertext()).strip()
            if text:
                context_texts.append(text)
    joined = "\n".join(context_texts)
    match = AI_CONTEXT_RE.search(joined)
    if not match:
        return ""
    return match.group("context").strip()


def parse_xliff_file(path: str) -> dict[str, tuple[str, str]]:
    tree = ET.parse(path)
    root = tree.getroot()
    result: dict[str, tuple[str, str]] = {}
    for node in root.iter():
        if _strip_ns(node.tag) != "trans-unit":
            continue
        source = _find_child_text(node, "source")
        target = _find_child_text(node, "target")
        if not source:
            continue
        result[source] = (target, _extract_ai_context(node))
    return result


def merge_xliff_files(paths: Iterable[str]) -> dict[str, tuple[str, str]]:
    merged: dict[str, tuple[str, str]] = {}
    for p in paths:
        merged.update(parse_xliff_file(p))
    return merged

