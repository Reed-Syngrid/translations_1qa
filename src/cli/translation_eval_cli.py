from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime

from pathlib import Path

from src.core.ai_client import AIClient
from src.core.benchmark import (
    BenchmarkLoadError,
    human_accuracy_for_source,
    load_benchmark_csv,
    resolve_benchmark_csv_path,
    stale_benchmark_msgids,
)
from src.core.config import load_env
from src.core.file_discovery import normalize_locale
from src.core.inputs_loader import load_language_inputs
from src.core.matching import sample_msgids, shared_msgids
from src.core.models import BenchmarkRow, RunConfig, TranslationCandidate
from src.core.output import write_results_csv
from src.core.run_report import build_report
from src.core.scoring import evaluate_candidate
from src.core.summary_report import find_critical_discrepancies, print_benchmark_summary


def _default_output(lang: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("outputs", f"translation_eval_{lang}_{ts}.csv")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate translation quality across .po and .xliff under inputs/{lang}/."
    )
    parser.add_argument(
        "--lang",
        "-l",
        required=True,
        help="Language code, e.g. ru, fr, de, es-ES, zh-TW.",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=100,
        help="Max number of shared strings.",
    )
    parser.add_argument(
        "--inputs-root",
        default="inputs",
        help="Root folder containing per-language subfolders (default: inputs, relative to cwd).",
    )
    parser.add_argument("--output", default="")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress information while evaluating strings.",
    )
    parser.add_argument(
        "--use-benchmark",
        action="store_true",
        help="Join Russian human benchmark CSV (only with --lang ru).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    load_env()
    if args.verbose:
        try:
            sys.stdout.reconfigure(line_buffering=True)  # type: ignore[attr-defined]
        except Exception:
            pass
    if args.limit <= 0:
        print("Error: --limit must be a positive integer.", flush=True)
        return 2

    if args.use_benchmark and normalize_locale(args.lang) != "ru":
        print(
            "Error: --use-benchmark is only supported for --lang ru (Russian benchmark).",
            flush=True,
        )
        return 2

    output = args.output or _default_output(args.lang)
    if args.output and os.path.isfile(output):
        print(
            "Error: output file already exists. Pick a new path or remove the file "
            "(previous runs are never auto-deleted; FR-005).",
            flush=True,
        )
        return 8

    config = RunConfig(
        language_code=args.lang,
        sample_size=args.limit,
        inputs_root=args.inputs_root,
        output_csv_path=output,
        openai_model=args.model,
        use_benchmark=args.use_benchmark,
    )
    started_at = time.time()

    try:
        loaded = load_language_inputs(config.inputs_root, config.language_code)
    except FileNotFoundError as e:
        print(f"Error: {e}", flush=True)
        return 3
    except OSError as e:
        print(f"Error loading inputs: {e}", flush=True)
        return 3

    if args.verbose:
        print(
            f"[discover] language={config.language_code} "
            f"lang_dir={loaded.lang_dir} "
            f"po_files={len(loaded.po_files)} "
            f"xliff_files={len(loaded.xliff_files)} "
            f"po_entries={len(loaded.po_map)} "
            f"xliff_entries={len(loaded.xliff_map)}",
            flush=True,
        )

    if not loaded.po_files:
        print(
            f"Error: no .po files found under {loaded.lang_dir}",
            flush=True,
        )
        return 3
    if not loaded.xliff_files:
        print(
            f"Error: no .xliff files found under {loaded.lang_dir}",
            flush=True,
        )
        return 4

    po_map = loaded.po_map
    xliff_map = loaded.xliff_map

    benchmark_map: dict[str, BenchmarkRow] | None = None
    stale: list[str] = []
    if config.use_benchmark:
        bench_path = resolve_benchmark_csv_path(Path(config.inputs_root) / "ru")
        try:
            benchmark_map = load_benchmark_csv(bench_path)
        except BenchmarkLoadError as e:
            print(f"Error loading benchmark: {e}", flush=True)
            return 6
        input_union = set(po_map.keys()) | set(xliff_map.keys())
        stale = stale_benchmark_msgids(benchmark_map, input_union)
        if args.verbose:
            print(
                f"[benchmark] path={bench_path} rows={len(benchmark_map)} "
                f"stale_msgids={len(stale)}",
                flush=True,
            )

    shared = shared_msgids(po_map, xliff_map)
    if not shared:
        print(
            "Error: no shared msgids across .po and .xliff after removing blank translations.",
            flush=True,
        )
        return 5
    selected = sample_msgids(shared, config.sample_size)
    if args.verbose:
        print(f"[match] shared_msgids={len(shared)} selected={len(selected)}", flush=True)
    ai = AIClient(model=config.openai_model, debug_prompts=args.verbose)
    results = []
    for idx, msgid in enumerate(selected, start=1):
        po_translation = po_map.get(msgid, "")
        xliff_translation, ai_context = xliff_map.get(msgid, ("", ""))
        if args.verbose:
            print(f"[eval] {idx}/{len(selected)} msgid={msgid!r}", flush=True)
        for source, text in (("po", po_translation), ("xliff", xliff_translation)):
            # FR-014: inputs_loader drops blanks; guard here so we never score empty strings.
            if not str(text).strip():
                continue
            candidate = TranslationCandidate(
                msgid=msgid,
                source_en=msgid,
                translation_source=source,
                translation_text=text,
                ai_context=ai_context,
                language_code=config.language_code,
            )
            b_row = benchmark_map.get(msgid) if benchmark_map else None
            acc_human = human_accuracy_for_source(b_row, source)
            results.append(evaluate_candidate(candidate, ai, accuracy_human=acc_human))

    write_results_csv(config.output_csv_path, results)
    report = build_report(results, started_at)
    print(f"Wrote CSV: {config.output_csv_path}", flush=True)
    print(
        f"Rows={report.total_rows}, FailedRows={report.failed_rows}, "
        f"DurationSec={report.duration_seconds:.2f}",
        flush=True,
    )
    if config.use_benchmark:
        crit = find_critical_discrepancies(results)
        print_benchmark_summary(stale, crit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
