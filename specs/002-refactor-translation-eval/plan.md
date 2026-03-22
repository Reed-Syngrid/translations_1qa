# Implementation Plan: Refactored Translation Evaluator

**Branch**: `002-refactor-translation-eval` | **Date**: 2026-03-22 | **Spec**: [`spec.md`](./spec.md)  
**Input**: Feature specification + clarification (Russian benchmark, local `./inputs/` layout)

## Summary

Refactor the translation evaluation CLI so it:

1. **Loads** all `.po` and `.xliff` files from **`./inputs/{lang}/`** with **UTF-8** I/O, robust decode errors, and **drops entries whose translation is blank/whitespace-only before any join or scoring** (FR-004, FR-014).
2. **Scores** only **Accuracy** (AI via existing `AIClient`) and **Capitalization** (deterministic); **removes** “Variables” / “Naturalness” from the product surface—implemented by **not** including placeholder/variable checks or naturalness in outputs or in **`final_score`** (FR-001). *Implementation detail:* remove `placeholder_score` from `final_score` and CSV, or keep diagnostic-only if needed for debugging—default is **omit from CSV** to match spec.
3. **Optionally** ( **`--use-benchmark`** + `ru` ) loads **`./inputs/ru/benchmark_ru_human_eval.csv`**, joins on **`msgid`**, attaches **`accuracy_human`** per format, and sets **`final_score`** using **human accuracy when present**, else AI accuracy, **combined with capitalization** (same boolean structure as today: both must pass for `final_score == 1` unless product defines otherwise—**default in implementation:** `final_score = 1` iff `capitalization_score == 1` and ( `accuracy_human` if present else `accuracy_ai` ) `== 1`).
4. **Reports** a **terminal summary** after benchmark runs: counts of **stale benchmark msgids**, and **critical discrepancies** where AI vs human accuracy disagree on pass/fail (FR-009, FR-013).
5. **Preserves** prior CSVs under `outputs/` via **timestamped filenames** (already present); never delete old exports (FR-005).

**Branch safety**: All implementation work for this feature is committed on **`002-refactor-translation-eval`** only.

## Technical Context

**Language/Version**: Python 3.10+ (match repo; align with `pyproject.toml` / CI)  
**Primary Dependencies**: Existing stack — `polib` (PO), `lxml` or `xml.etree` (XLIFF), `openai` client, `python-dotenv`; add **`stdlib csv`** for benchmark loading (no new heavy deps).  
**Storage**: Local filesystem — `./inputs/`, `./outputs/` (or configured output dir).  
**Testing**: `pytest` — unit tests for loaders (encoding, blank skip), benchmark join, scoring precedence, summary builder.  
**Target Platform**: Windows + cross-platform paths (`pathlib`, no hard-coded `C:\` defaults in refactored CLI).  
**Project Type**: Single-package CLI (`python -m src.cli.translation_eval_cli`).  
**Performance Goals**: Same as 001 — ~100–300+ strings per run; parsing O(n); benchmark index O(n) in-memory.  
**Constraints**: UTF-8; fail fast on duplicate `msgid` in benchmark CSV when `--use-benchmark`; optional strictness on malformed benchmark rows.  
**Scale/Scope**: One language per run; optional benchmark only for `ru`.

## Constitution Check

| Principle | How this plan complies |
|-----------|-------------------------|
| **Source of truth** | Read-only reads from `./inputs/`; no mutation of PO/XLIFF/benchmark files. |
| **Completeness & coverage** | Report sample size, shared msgid counts, stale benchmark counts, skipped-blank counts. |
| **Consistency** | Capitalization check remains; placeholder checking **dropped from scored dimensions** per FR-001 (variables out of scope). If product later needs placeholder diagnostics only, add a non-scored debug column. |
| **Review & QA** | Deterministic tests for loaders and join; golden CSV snapshots optional. |
| **Traceability** | Log run id: `lang`, `limit`, `inputs` path, `use_benchmark`, model, timestamped output path. |

No constitution violations anticipated.

## Project Structure

### Documentation (this feature)

```text
specs/002-refactor-translation-eval/
├── spec.md
├── plan.md                 # this file
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── cli-contract.md
└── checklists/
    └── requirements.md
```

### Source Code (repository root) — target layout after refactor

```text
src/
├── cli/
│   └── translation_eval_cli.py       # argparse: --inputs-root, --lang, --use-benchmark, ...
├── core/
│   ├── config.py
│   ├── models.py                     # RunConfig, TranslationCandidate, EvaluationResult (+ benchmark fields)
│   ├── inputs_loader.py              # NEW: discover ./inputs/{lang}/*.po, *.xliff, UTF-8, merge maps
│   ├── benchmark.py                  # NEW: load benchmark CSV, index by msgid, stale detection, human columns
│   ├── file_discovery.py             # DEPRECATE or narrow: replaced by inputs_loader for new path
│   ├── po_parser.py
│   ├── xliff_parser.py
│   ├── matching.py
│   ├── checks.py                     # capitalization only in scoring path; placeholder helpers optional
│   ├── ai_client.py
│   ├── scoring.py                    # REFACTOR: accuracy + cap only; final_score + benchmark precedence
│   ├── output.py                     # REFACTOR: CSV headers (accuracy_ai, accuracy_human, drop placeholder cols)
│   ├── summary_report.py             # NEW: critical discrepancies + stale counts (FR-013)
│   └── run_report.py                 # extend or delegate to summary_report
tests/
├── unit/
│   ├── test_inputs_loader.py
│   ├── test_benchmark.py
│   ├── test_scoring.py
│   └── ...
inputs/                               # tracked in git (FR-007)
└── {lang}/
    ├── *.po
    ├── *.xliff
    └── ru/benchmark_ru_human_eval.csv   # canonical name when using --use-benchmark
outputs/                              # gitignored outputs; never delete old files (FR-005)
```

**Structure Decision**: Add **`inputs_loader`** and **`benchmark`** modules; **`scoring` / `output` / CLI** refactored; keep parsers and **`AIClient`** largely intact. Remove hard-coded Windows paths from CLI defaults in favor of **`./inputs`** relative to repo cwd (or `--inputs-root`).

## Architecture

### 1. Data loading (`inputs_loader.py`)

- **Discovery**: `Path(inputs_root) / lang /` → glob `*.po`, `*.xliff` (case-insensitive).
- **Encoding**: open all text with **`encoding="utf-8"`**; on `UnicodeDecodeError`, surface a **clear error** naming the file (fail fast).
- **Parsing**: Reuse `merge_po_files` / `merge_xliff_files` after resolving paths.
- **Cleaning (FR-014)**: After extracting `(msgid, translation, ...)`, **filter out** entries where `translation.strip() == ""`. Apply **before** intersection, sampling, benchmark join, and `evaluate_candidate`.
- **Maps**: Produce `po_map: dict[msgid, str]`, `xliff_map: dict[msgid, tuple[str, str]]` (translation, context) matching current parsers.

### 2. Benchmark integration (`benchmark.py` + CLI)

- **Flag**: `--use-benchmark` — valid only when **`--lang ru`** (if other lang + flag → error with message). **FR-011**
- **Path**: `inputs_root / "ru" / "benchmark_ru_human_eval.csv"`. **FR-012** if missing when flag set.
- **Parse**: `csv.DictReader`, normalize header names (strip BOM/whitespace). Map columns to:
  - Primary key: **`msgid`** (must match PO/XLIFF msgid string exactly).
  - Human accuracy: from existing sheet columns — e.g. **`accuracy_score_po`** / **`accuracy_score_xliff`** or percentage columns; **normalize to 0/1** or same scale as AI for comparison (document in `research.md`).
- **Integrity**: Duplicate `msgid` rows → **fail fast** with line numbers (per spec edge case).
- **Join**: Build `dict[msgid, BenchmarkRow]` with **per-format** human scores. After evaluation, **stale** = benchmark msgids not in union of post-cleaning PO ∪ XLIFF msgids (or per spec: “no matching input entry after cleaning”). **FR-009**
- **Precedence**: Pass **`accuracy_human`** into scoring or post-process: **`final_score`** uses human for accuracy component when present. **FR-010**

### 3. Scoring engine (`scoring.py`)

- **Remove** naturalness (already not in current `scoring.py` as separate field).
- **Remove variable/placeholder from `final_score`**: `final_score = int(accuracy_component == 1 and capitalization_score == 1)` where `accuracy_component` is human if provided else AI.
- **Rename for clarity in result model**: `accuracy_ai` (from GPT) vs `accuracy_human` (optional float/int from benchmark).
- **Capitalization**: unchanged `check_capitalization`.
- **Do not call** `check_placeholders` in the main scoring path for release builds (or gate behind `--debug-placeholders` if diagnostics needed).

### 4. Output (`output.py`)

- Update **CSV_HEADERS** to reflect:
  - `accuracy_ai_po` / `accuracy_ai_xliff` (or nested naming consistent with one-row-per-msgid layout).
  - `accuracy_human_po` / `accuracy_human_xliff` when benchmark mode (empty when absent).
  - `final_score_po` / `final_score_xliff` using precedence rules.
  - **Drop** placeholder columns from default export per FR-001, or move to `--verbose-csv`.

### 5. Summary reporter (`summary_report.py`)

After CSV write, if **`--use-benchmark`**:

- **Stale benchmark count** + optional cap on listed msgids in log.
- **Critical discrepancies**: e.g. `(accuracy_ai == 1 and accuracy_human == 0)` or `(accuracy_ai == 0 and accuracy_human == 1)` after normalizing both to binary pass/fail; print **count** + **sample msgids** (first N). **FR-013**

### 6. CLI migration

Replace `--po-root` / `--xliff-root` defaults with:

- `--inputs-root` default **`inputs`** (relative to cwd).
- Keep optional override for legacy workflows if needed (behind explicit flag or document migration in `quickstart.md`).

## Phase 0 – Research (see `research.md`)

- Column mapping for `benchmark_ru_human_eval.csv` (exact headers in repo file).
- Confirm `msgid` matching for multiline/quoted CSV fields (stdlib `csv` handles quotes).
- Binary threshold: AI returns 0/1; human columns may be % — conversion rule.

## Phase 1 – Design (see `data-model.md`)

- Extend **`EvaluationResult`** / grouped CSV row with `accuracy_ai`, `accuracy_human`, `final_score`.
- Define **`BenchmarkRow`** dataclass.

## Phase 2 – Implementation sequence

1. `inputs_loader` + tests; wire CLI to `./inputs/{lang}`.
2. Refactor `scoring.py` + `models.py` + `output.py` (two metrics only, new column names).
3. `benchmark.py` + `--use-benchmark` + Russian-only validation.
4. `summary_report.py` + integrate in CLI after `write_results_csv`.
5. Remove hard-coded paths; update README / `quickstart.md`.
6. Manual run on `ru` sample; verify FR-005 (new file doesn’t delete old outputs).

## Phase 3 – Verification

- **Unit**: loader (UTF-8, blank skip), benchmark duplicates fail, join precedence, summary counts.
- **Integration**: one full CLI run with small `--limit` on fixture `inputs/ru`.

## Complexity Tracking

_No violations requiring justification._

## References

- Spec: [`spec.md`](./spec.md)
- CLI contract: [`contracts/cli-contract.md`](./contracts/cli-contract.md)
- Data model: [`data-model.md`](./data-model.md)
