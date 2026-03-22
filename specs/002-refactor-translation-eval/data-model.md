# Data Model: Refactored Translation Evaluator

**Branch**: `002-refactor-translation-eval` | **Date**: 2026-03-22

## Core types (Python)

### `RunConfig` (extend)

| Field | Type | Description |
|-------|------|-------------|
| `language_code` | `str` | BCP 47 style, e.g. `ru`, `es-ES`. |
| `sample_size` | `int` | Max msgids to evaluate after matching. |
| `inputs_root` | `str` | Default `inputs`; base for `./inputs/{lang}/`. |
| `output_csv_path` | `str` | Timestamped path under `outputs/`. |
| `openai_model` | `str` | Model id for AI accuracy. |
| `use_benchmark` | `bool` | If true, load Russian benchmark (only valid for `ru`). |

### `TranslationCandidate` (unchanged conceptually)

| Field | Description |
|-------|-------------|
| `msgid` | Source key / English source string identifier. |
| `source_en` | Same as msgid for display, or explicit source column if later split. |
| `translation_source` | `"po"` \| `"xliff"`. |
| `translation_text` | Target string (non-blank at evaluation time). |
| `ai_context` | From XLIFF context (may be empty for PO-only context). |
| `language_code` | Locale code. |

### `BenchmarkRow` (new)

| Field | Type | Description |
|-------|------|-------------|
| `msgid` | `str` | Join key. |
| `accuracy_human_po` | `int \| None` | 0/1 when present. |
| `accuracy_human_xliff` | `int \| None` | 0/1 when present. |

*Populate from CSV columns; `None` if column missing or unparsable for that row.*

### `EvaluationResult` (extend)

| Field | Type | Description |
|-------|------|-------------|
| `msgid` | `str` | |
| `translation_source` | `str` | `po` / `xliff`. |
| `source_en` | `str` | |
| `translation_text` | `str` | |
| `language_code` | `str` | |
| `ai_context` | `str` | |
| `accuracy_ai` | `int` | GPT accuracy (0/1). |
| `accuracy_human` | `int \| None` | From benchmark when joined. |
| `capitalization_score` | `int` | 0/1. |
| `final_score` | `int` | 0/1: `cap_ok and (human_acc if present else ai_acc)`. |
| `error_reason` | `str` | Optional API failure, etc. |

**Deprecated / removed from scoring surface:** `placeholder_score`, `placeholder_diagnostics` — drop from `final_score` and default CSV (per FR-001).

## CSV aggregate row (one row per `msgid`)

Logical columns (names to match `output.py`):

- Identifiers: `msgid`, `source_en`, `ai_context`
- PO: `translation_text_po`, `accuracy_ai_po`, `accuracy_human_po`, `capitalization_score_po`, `final_score_po`
- XLIFF: `translation_text_xliff`, `accuracy_ai_xliff`, `accuracy_human_xliff`, `capitalization_score_xliff`, `final_score_xliff`
- Optional: `error_reason`

## Summary object (new)

| Field | Description |
|-------|-------------|
| `stale_benchmark_msgids` | `list[str]` or count-only |
| `critical_discrepancy_count` | `int` |
| `critical_discrepancy_samples` | `list[str]` (msgids, capped) |
| `duration_seconds` | `float` |
