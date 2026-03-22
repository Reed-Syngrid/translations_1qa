# Phase 0 Research: Refactored Translation Evaluator

**Branch**: `002-refactor-translation-eval` | **Date**: 2026-03-22

## 1. Benchmark CSV schema (Russian)

Observed export: `inputs/ru/Benchmark_ru_human_eval - Sheet1.csv` (rename to **`benchmark_ru_human_eval.csv`** for canonical path).

Header (row 1):

`msgid`, `source_en`, `ai_context`, `translation_text_po`, `accuracy_score_po`, `Accurancy` (PO human / %), `translation_text_xliff`, `accuracy_score_xliff`, second `Accurancy` (XLIFF human / %).

**Decisions for implementation:**

| Field | Use |
|-------|-----|
| `msgid` | **Primary join key** to PO/XLIFF entries (strict string equality after cleaning). |
| `accuracy_score_po` / `accuracy_score_xliff` | Binary-ish scores in sample rows (0/1); treat as **human accuracy** for that format. |
| Columns named `Accurancy` | Likely **percentage** strings (e.g. `77.32%`); **not** used for `final_score` if numeric 0/1 columns exist. If only % present, derive binary via threshold (e.g. ≥50% → pass) — **document chosen rule in code comments** and align with product. Prefer **numeric columns** when both exist. |

**Integrity:** Duplicate `msgid` → **fail fast** in benchmark mode.

## 2. UTF-8 and encoding

- Read all PO/XLIFF/benchmark files as **UTF-8**.
- On decode failure: raise user-visible error with **file path** (no silent fallback) to satisfy constitution “documented encoding”.

## 3. Blank / whitespace-only translations

- Normalize: `if not translation.strip(): skip entry` at loader layer **before** shared-msgid intersection and benchmark join (**FR-014**).

## 4. `msgid` equality

- PO and XLIFF parsers already key by `msgid` string; benchmark CSV `msgid` column may include quotes and commas — use Python **`csv` module** so first column matches parser keys exactly.

## 5. Critical discrepancy definition (default)

- Normalize AI and human to **pass/fail** bits (0/1).
- **Critical**: `(ai_pass != human_pass)` for the same row/format.
- Optional **severity**: “AI pass & human fail” vs “AI fail & human pass” sub-counts in summary.

## 6. Open questions resolved in plan

- **final_score**: Uses **human** accuracy bit when present, else **AI**; **and** `capitalization_score == 1` for overall pass unless product defines accuracy-only gate (current tool combines both — keep combined unless spec amended).
