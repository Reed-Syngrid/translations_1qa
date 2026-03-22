"""
End-of-run summary when --use-benchmark is on (stale rows + AI vs human disagreements).
"""

from __future__ import annotations

from .models import EvaluationResult


def find_critical_discrepancies(
    results: list[EvaluationResult],
) -> list[tuple[str, str, int, int]]:
    """
    Rows where human score exists and pass/fail differs from AI accuracy.
    Returns list of (msgid, translation_source, accuracy_ai, accuracy_human).
    """
    out: list[tuple[str, str, int, int]] = []
    for r in results:
        if r.accuracy_human is None:
            continue
        ai_pass = r.accuracy_ai == 1
        hum_pass = r.accuracy_human == 1
        if ai_pass != hum_pass:
            out.append((r.msgid, r.translation_source, r.accuracy_ai, r.accuracy_human))
    return out


def print_benchmark_summary(
    stale_msgids: list[str],
    critical: list[tuple[str, str, int, int]],
    max_samples: int = 15,
) -> None:
    print("", flush=True)
    print("--- Benchmark summary ---", flush=True)
    print(f"Stale benchmark msgids (no matching input): {len(stale_msgids)}", flush=True)
    if stale_msgids and len(stale_msgids) <= max_samples:
        for m in stale_msgids:
            preview = m if len(m) <= 100 else m[:97] + "..."
            print(f"  stale: {preview!r}", flush=True)
    elif stale_msgids:
        for m in stale_msgids[:max_samples]:
            preview = m if len(m) <= 100 else m[:97] + "..."
            print(f"  stale: {preview!r}", flush=True)
        print(f"  ... and {len(stale_msgids) - max_samples} more", flush=True)

    print(f"Critical discrepancies (AI vs human pass/fail differ): {len(critical)}", flush=True)
    for msgid, src, ai_s, hum_s in critical[:max_samples]:
        preview = msgid if len(msgid) <= 80 else msgid[:77] + "..."
        print(
            f"  {preview!r} [{src}] accuracy_ai={ai_s} accuracy_human={hum_s}",
            flush=True,
        )
    if len(critical) > max_samples:
        print(f"  ... and {len(critical) - max_samples} more", flush=True)
