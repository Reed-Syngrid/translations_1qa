from __future__ import annotations

import random


def shared_msgids(po_map: dict[str, str], xliff_map: dict[str, tuple[str, str]]) -> list[str]:
    shared = sorted(set(po_map.keys()).intersection(set(xliff_map.keys())))
    return shared


def sample_msgids(msgids: list[str], limit: int, seed: int = 42) -> list[str]:
    if limit <= 0 or len(msgids) <= limit:
        return msgids
    rng = random.Random(seed)
    copied = list(msgids)
    rng.shuffle(copied)
    selected = sorted(copied[:limit])
    return selected

