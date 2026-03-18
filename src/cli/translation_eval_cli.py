from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime

from src.core.ai_client import AIClient
from src.core.config import load_env
from src.core.file_discovery import discover_language_files
from src.core.matching import sample_msgids, shared_msgids
from src.core.models import RunConfig, TranslationCandidate
from src.core.output import write_results_csv
from src.core.po_parser import merge_po_files
from src.core.run_report import build_report
from src.core.scoring import evaluate_candidate
from src.core.xliff_parser import merge_xliff_files


def _default_output(lang: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join("outputs", f"translation_eval_{lang}_{ts}.csv")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate translation quality across .po and .xliff."
    )
    parser.add_argument(
        "--lang",
        "-l",
        required=True,
        help="Language code, e.g. ru, fr, de, zh-CN.",
    )
    parser.add_argument(
        "--limit",
        "-n",
        type=int,
        default=100,
        help="Max number of shared strings.",
    )
    parser.add_argument(
        "--po-root",
        default=r"C:\metabase_translations\metabase_v0_57_15\metabase-0.57.15\locales",
    )
    parser.add_argument("--xliff-root", default=r"C:\metabase_translations\Ai_translations")
    parser.add_argument("--output", default="")
    parser.add_argument("--model", default="gpt-5.4")
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress information while evaluating strings.",
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

    output = args.output or _default_output(args.lang)
    config = RunConfig(
        language_code=args.lang,
        sample_size=args.limit,
        po_root=args.po_root,
        xliff_root=args.xliff_root,
        output_csv_path=output,
        openai_model=args.model,
    )
    started_at = time.time()
    discovery = discover_language_files(
        config.po_root, config.xliff_root, config.language_code
    )
    if args.verbose:
        print(
            f"[discover] language={config.language_code} "
            f"po_candidates={len(discovery.po_debug)} "
            f"xliff_candidates={len(discovery.xliff_debug)}"
            ,
            flush=True,
        )
    if not discovery.po_files:
        print(
            f"Error: no .po files found for language '{config.language_code}' "
            f"in {config.po_root}"
            ,
            flush=True,
        )
        print("Debug: discovered .po candidates and inferred locales:", flush=True)
        for path, code in discovery.po_debug:
            print(f"  {path} -> {code}", flush=True)
        return 3
    if not discovery.xliff_files:
        print(
            f"Error: no .xliff files found for language '{config.language_code}' "
            f"in {config.xliff_root}"
            ,
            flush=True,
        )
        print("Debug: discovered .xliff candidates and inferred locales:", flush=True)
        for path, code in discovery.xliff_debug:
            print(f"  {path} -> {code}", flush=True)
        return 4

    po_map = merge_po_files(discovery.po_files)
    xliff_map = merge_xliff_files(discovery.xliff_files)
    shared = shared_msgids(po_map, xliff_map)
    if not shared:
        print("Error: no shared msgids across .po and .xliff files.", flush=True)
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
            candidate = TranslationCandidate(
                msgid=msgid,
                source_en=msgid,
                translation_source=source,
                translation_text=text,
                ai_context=ai_context,
                language_code=config.language_code,
            )
            results.append(evaluate_candidate(candidate, ai))

    write_results_csv(config.output_csv_path, results)
    report = build_report(results, started_at)
    print(f"Wrote CSV: {config.output_csv_path}", flush=True)
    print(
        f"Rows={report.total_rows}, FailedRows={report.failed_rows}, "
        f"DurationSec={report.duration_seconds:.2f}"
        ,
        flush=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

