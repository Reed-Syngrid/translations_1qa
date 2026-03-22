# Tasks: Refactored Translation Evaluator (002)

**Input**: [`plan.md`](./plan.md), [`spec.md`](./spec.md), [`data-model.md`](./data-model.md), [`contracts/cli-contract.md`](./contracts/cli-contract.md)  
**Branch**: `002-refactor-translation-eval`  
**Prerequisites**: plan.md ✅ spec.md ✅

**Format**: `[ID] [P?] [Story] Description` — Story = US1 (P1 local eval), US2 (PO vs XLIFF), US3 (benchmark)

---

## Phase 1: Setup (minimal)

**Purpose**: Align repo with planned module layout; no blocking “framework” work.

- [ ] **T001** Create empty module files `src/core/inputs_loader.py` and `src/core/benchmark.py` and `src/core/summary_report.py` (placeholders or docstrings only) so imports can be wired incrementally.
- [ ] **T002** [P] Confirm `inputs/` and `outputs/` expectations in root `README.md` or `specs/002-refactor-translation-eval/quickstart.md` match implementation (relative `./inputs`, timestamped `./outputs`).

---

## Phase 2: Foundational (blocking)

**Purpose**: Data model + loader + cleaning pipeline. **No user story is complete until blank-skipping and UTF-8 behavior exist.**

**⚠️** Scoring/output/CLI refactors should assume these contracts.

- [ ] **T003** [US1] Extend `src/core/models.py`: add `inputs_root: str`, `use_benchmark: bool` to `RunConfig`; add `BenchmarkRow` dataclass; extend `EvaluationResult` with `accuracy_ai`, `accuracy_human: int | None`, remove reliance on `placeholder_score` for `final_score` (keep fields optional/deprecated until T014 removes from CSV).
- [ ] **T004** [US1] Implement `src/core/inputs_loader.py`: resolve `Path(inputs_root) / language_code`; discover `*.po` / `*.xliff` (case-insensitive); call existing `merge_po_files` / `merge_xliff_files` with paths opened **UTF-8** (`encoding="utf-8"` in parser layer or wrapper); on `UnicodeDecodeError` raise clear error including **file path**.
- [ ] **T005** [US1] In `inputs_loader` (or shared helper), **filter maps** so any entry with `translation.strip() == ""` is **dropped** before maps are returned — **FR-004 / FR-014** (apply before shared-msgid intersection, sampling, benchmark join, scoring).
- [ ] **T006** [P] [US1] Add `tests/unit/test_inputs_loader.py`: fixture with blank `msgstr` removed from counts; optional test for UTF-8 read failure path (mock or temp file with invalid bytes).

**Checkpoint**: Loader returns cleaned maps; tests green for T006.

---

## Phase 3: User Story 1 — Local evaluation from `./inputs/{lang}/` (Priority: P1) 🎯 MVP

**Goal**: CLI uses **relative** `--inputs-root` (default `inputs`), no hard-coded `C:\` roots; end-to-end run works without benchmark.

**Independent test**: `python -m src.cli.translation_eval_cli --lang ru --inputs-root inputs --limit 5` → CSV under `outputs/` with new column layout (after T012–T015).

### Implementation — US1

- [x] **T007** [US1] Refactor `src/cli/translation_eval_cli.py`: replace `--po-root` / `--xliff-root` with `--inputs-root` (default **`inputs`**); resolve relative to **cwd** via `pathlib.Path`; remove Windows-specific default paths.
- [x] **T008** [US1] Wire CLI to `inputs_loader.load_language_inputs(inputs_root, lang)` instead of `discover_language_files` + separate roots for the new path layout.
- [x] **T009** [US1] Ensure `shared_msgids` / `sample_msgids` run **after** T005 cleaning so blank translations never enter the evaluation loop.

### Scoring & output — US1 (Accuracy + Capitalization ONLY)

- [x] **T010** [US1] Refactor `src/core/scoring.py`: compute **only** `accuracy_ai` (via `AIClient.score_accuracy`) and `capitalization_score` (`check_capitalization`); **do not** call `check_placeholders` in default scoring path; `final_score = int(accuracy_component == 1 and capitalization_score == 1)` where `accuracy_component` is `accuracy_human` if provided else `accuracy_ai` (human typically `None` in US1-only runs).
- [x] **T011** [US1] Update `src/core/ai_client.py` only if needed to align naming (e.g. docstrings reference “accuracy_ai”); no new API surface unless required.
- [x] **T012** [US1] Refactor `src/core/output.py`: CSV headers per [`data-model.md`](./data-model.md) — `accuracy_ai_po/xliff`, `capitalization_score_*`, `final_score_*`; **remove** placeholder columns from default export (**FR-001**); keep `error_reason` if still used.
- [x] **T013** [US1] Update `src/core/run_report.py` if needed to match new `EvaluationResult` fields (failed rows / counts).
- [x] **T014** [US1] Remove or stub unused `placeholder_score` / `placeholder_diagnostics` from `EvaluationResult` and CSV output (or gate behind `--debug-placeholders` if product wants diagnostics later).

### Tests — US1 (recommended)

- [x] **T015** [P] [US1] `tests/unit/test_scoring.py`: `final_score` uses only accuracy + cap; when `accuracy_human` is `None`, `final_score` matches AI+cap; when `accuracy_human` set, overrides AI for accuracy component.

**Checkpoint**: US1 MVP: local inputs, relative paths, cleaned blanks, two-metric scoring, CSV without placeholders.

---

## Phase 4: User Story 2 — PO vs XLIFF clarity (Priority: P2)

**Goal**: One row per `msgid` still distinguishes PO vs XLIFF columns; behavior unchanged except column names and no placeholder noise.

**Independent test**: Export shows separate `accuracy_ai_po` / `accuracy_ai_xliff` (and caps) for same msgid sample.

- [x] **T016** [US2] Verify `write_results_csv` in `src/core/output.py` groups by `msgid` and keeps **per-source** columns distinct; adjust labels if plan/data-model names differ from code.
- [x] **T017** [P] [US2] Add integration smoke: `tests/integration/test_cli_smoke.py` (optional) — run CLI with `--limit 1` and assert output file exists and header contains `accuracy_ai` (or project-chosen names).

**Checkpoint**: US2 satisfied when CSV is unambiguous for PO vs XLIFF.

---

## Phase 5: User Story 3 — `--use-benchmark` + discrepancies (Priority: P3)

**Goal**: Russian benchmark CSV joined on **`msgid`**; stale rows reported; **critical discrepancies** summary; **FR-011–FR-013**.

**Independent test**: `--lang ru --use-benchmark` with canonical `inputs/ru/benchmark_ru_human_eval.csv` (rename from `Benchmark_ru_human_eval - Sheet1.csv` if needed). Missing file → clear error.

### Implementation — US3

- [x] **T018** [US3] Implement `src/core/benchmark.py`: `load_benchmark_csv(path) -> dict[str, BenchmarkRow]` using `csv.DictReader`; normalize headers; map `accuracy_score_po` / `accuracy_score_xliff` to human 0/1; **duplicate `msgid` → raise** with line hint (**fail fast**).
- [x] **T019** [US3] Add `resolve_benchmark_path(inputs_root: Path) -> Path` for `inputs/ru/benchmark_ru_human_eval.csv`; if `--use-benchmark` and file missing → **sys.exit** with message (**FR-012**).
- [x] **T020** [US3] CLI: add `--use-benchmark`; if set and `--lang` ≠ `ru` → error (**FR-011**); load benchmark only when flag set.
- [x] **T021** [US3] Join loop in `translation_eval_cli.py`: for each candidate row, attach `accuracy_human` from `BenchmarkRow` by `msgid` + format (po/xliff); leave `None` if no benchmark row.
- [x] **T022** [US3] Implement **stale benchmark** set: benchmark msgids not present in union of evaluated (post-clean) input msgids; pass list/count to summary (**FR-009**).
- [x] **T023** [US3] Implement `src/core/summary_report.py`: `build_benchmark_summary(results, stale_msgids, ...) -> str` listing **stale count**, **critical discrepancy count** (AI pass vs human fail and vice versa after normalizing to 0/1), **sample msgids** (cap at N).
- [x] **T024** [US3] After `write_results_csv`, if `--use-benchmark`, **print** summary to stdout (**FR-013**).

### Tests — US3

- [x] **T025** [P] [US3] `tests/unit/test_benchmark.py`: duplicate msgid fails; join picks correct po vs xliff human column; stale msgid detected.
- [x] **T026** [P] [US3] `tests/unit/test_summary_report.py`: critical discrepancy counts match synthetic `EvaluationResult` lists.

**Checkpoint**: US3 complete when benchmark flag, join, stale + discrepancy summary all work.

---

## Phase 6: Polish & cross-cutting

- [x] **T027** [P] Deprecate or redirect `src/core/file_discovery.py` (document “legacy” or remove if unused) to avoid duplicate discovery logic.
- [x] **T028** [P] Update project `README.md` with new CLI flags and `./inputs` layout; link to `specs/002-refactor-translation-eval/quickstart.md`.
- [x] **T029** Verify **FR-005**: output path remains timestamped; **no code path deletes** `outputs/*.csv`.
- [ ] **T030** Manual run: `python -m src.cli.translation_eval_cli --lang ru --inputs-root inputs --limit 5` and with `--use-benchmark` after renaming benchmark file to canonical name.

---

## Dependencies & execution order

| Phase | Depends on | Notes |
|-------|--------------|--------|
| 2 Foundational | T001 | T003–T006 before CLI wiring |
| 3 US1 | T003–T006 | T007–T015 sequential where same files |
| 4 US2 | US1 output stable | T016–T017 |
| 5 US3 | T003–T015 (models + scoring + output) | T018–T024 after `accuracy_human` in results |
| 6 Polish | All desired stories | T027–T030 |

**Parallel**: T006 with T002; T015 with T017; T025 with T026 after T018–T023 exist.

---

## Focus mapping (requested)

| Focus | Tasks |
|--------|--------|
| **Relative paths / inputs_loader** | T004, T005, T007, T008, T009, T027 |
| **Scoring: Accuracy + Capitalization only** | T003, T010, T012, T014, T015 |
| **`--use-benchmark` + discrepancies** | T018–T024, T025, T026 |
| **Blank / whitespace cleaning** | T005, T009 (integration in pipeline) |

---

## Implementation strategy

1. **MVP**: Complete Phase 2 → Phase 3 (T003–T015) → validate US1.
2. **Then** Phase 4 (US2 polish), Phase 5 (US3 benchmark), Phase 6.

---

## Notes

- Canonical benchmark filename: `inputs/ru/benchmark_ru_human_eval.csv` (rename from `Benchmark_ru_human_eval - Sheet1.csv` if needed).
- All work on branch **`002-refactor-translation-eval`** per spec.
