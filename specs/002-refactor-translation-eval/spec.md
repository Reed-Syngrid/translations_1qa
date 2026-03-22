# Feature Specification: Refactor Translation Evaluation Tool

**Feature Branch**: `002-refactor-translation-eval`  
**Created**: 2026-03-19  
**Status**: Draft  
**Input**: User description: "Refactor Translation Evaluation Tool — simplified metrics (Accuracy, Capitalization only); local `./inputs/{lang}/` with `.po` and `.xliff`; skip blank translations; retain prior evaluation exports; optional Russian benchmark comparison (reference data supplied later); `./inputs/` version-controlled; compare PO vs XLIFF outputs in tabular results."

**Clarified**: 2026-03-22 — Russian human benchmark integration logic (see [Russian Human Evaluation Benchmark](#clarification-russian-human-evaluation-benchmark-integration-logic)).

## Clarification: Russian Human Evaluation Benchmark (Integration Logic) {#clarification-russian-human-evaluation-benchmark-integration-logic}

The following decisions apply when the Russian **ground-truth** file is present at `./inputs/ru/benchmark_ru_human_eval.csv` (or the project-agreed canonical name aligned with that dataset). Spreadsheet exports may use a different filename until renamed to the canonical name.

| Topic | Decision |
|-------|----------|
| **Matching protocol** | Use a **strict match on `msgid`** (the canonical source message identifier) to align benchmark rows with entries loaded from `.po` and `.xliff`. Entries in XLIFF MUST resolve to the **same logical `msgid`** as in PO so one benchmark row can join to at most one evaluated row per format. |
| **Benchmark row with no input** | If a benchmark `msgid` has **no** corresponding entry in the current input files (after cleaning), record it as a **stale benchmark entry** (logged and included in run summary counts—not silently ignored). |
| **Input entry with no benchmark** | If an evaluated entry has **no** benchmark row, **accuracy_human** is absent (empty or explicitly marked as not applicable); scoring for Accuracy/Capitalization still proceeds for **accuracy_ai** and capitalization per tool rules. |
| **Output columns (Russian, benchmark mode)** | The export MUST include **`accuracy_ai`** (automated accuracy) and **`accuracy_human`** (from the benchmark). When the benchmark provides **separate human scores per format** (e.g. PO vs XLIFF), each evaluated row MUST take **`accuracy_human`** from the column that matches that row’s format. **`final_score`** (or the single field used for pass/fail / threshold decisions on **accuracy**) MUST use **`accuracy_human` when present**, and otherwise fall back to **`accuracy_ai`**. |
| **Scoring dimensions** | Remains **Accuracy** and **Capitalization** only. The human benchmark file is treated as the **human accuracy** reference; **Capitalization** continues to be produced by the evaluation tool unless the benchmark is later extended with a human capitalization column (out of scope unless added by a future change). |
| **Data cleaning before match** | **Yes**: entries where the translation string is **blank or whitespace-only** (after trim) MUST be **excluded before** attempting benchmark join or AI accuracy on that row—consistent with global cleaning rules. |
| **Discrepancy reporting** | **Yes**: at end of run, produce a **short summary** that flags **critical discrepancies**, including at minimum cases where **automated accuracy and human accuracy strongly disagree** (e.g. high AI score vs low human score, or the inverse as defined by project thresholds). |
| **Execution mode** | Benchmark comparison is **not** implied by `--lang ru` alone. It MUST be **opt-in** via an explicit run option (e.g. **`--use-benchmark`**) so runs without the flag behave as standard evaluation. When the flag is set for Russian and the benchmark file is missing or unreadable, the run MUST **fail with a clear message** (not a silent no-op). |

**Project constraint**: Implementation for this feature is targeted to the **`002-refactor-translation-eval`** branch.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Run evaluation from local language inputs (Priority: P1)

A localization owner places translation files under a predictable folder per language and runs the evaluation. The tool reads those files, ignores unusable entries, and produces scores for the two retained quality dimensions so the team can see how good the translations are without relying on previous metric sets that are no longer needed.

**Why this priority**: Without local, repeatable evaluation on the two agreed metrics, no other story delivers value.

**Independent Test**: Can be fully tested by placing valid sample files under the required folder layout, running the evaluation once, and confirming scores appear only for Accuracy and Capitalization and that blank translations never contribute.

**Acceptance Scenarios**:

1. **Given** `./inputs/{language}/` contains supported translation files for that language, **When** the user runs evaluation, **Then** the tool loads strings from those files and produces a tabular results export including Accuracy and Capitalization scores (and no scores for removed dimensions).
2. **Given** an entry has a missing or empty translated string, **When** evaluation runs, **Then** that entry is skipped or removed from consideration and does not affect scores.
3. **Given** prior evaluation exports already exist from earlier runs, **When** the user runs evaluation again, **Then** existing result files are not deleted by the tool.

---

### User Story 2 - Compare PO-based vs XLIFF-based translation sets (Priority: P2)

The same stakeholder needs to decide which file format pipeline produces better outcomes. They run the tool so that results distinguish performance for content originating from PO versus XLIFF for the same language context.

**Why this priority**: Comparison between formats is the stated goal and depends on P1 working, but can be validated as soon as P1 is stable.

**Independent Test**: Can be tested by supplying both file types for one language and verifying the export clearly separates or labels PO versus XLIFF outcomes.

**Acceptance Scenarios**:

1. **Given** both `.po` and `.xliff` inputs exist under the same language folder (or as required by the agreed layout), **When** evaluation completes, **Then** the results allow the user to see Accuracy and Capitalization outcomes for each format (or each run) without mixing them ambiguously.
2. **Given** only one format is present, **When** evaluation runs, **Then** the tool still completes and records results for the available format without failing solely due to the absence of the other.

---

### User Story 3 - Align results with an external Russian benchmark (Priority: P3)

When the human-corrected benchmark file is in `./inputs/ru/`, reviewers can compare automated accuracy to human accuracy per **`msgid`**, see **`accuracy_ai`** vs **`accuracy_human`**, and rely on **`final_score`** that **prefers human** when present. Stale benchmark rows and critical AI–human disagreements are visible in run output.

**Why this priority**: Benchmarking is valuable for governance but depends on reference data and opt-in; it must not block baseline evaluation.

**Independent Test**: With benchmark file present, run with `--lang ru` and `--use-benchmark` (or agreed equivalent), then verify strict `msgid` joins, stale entry logging, column presence, **final_score** precedence, and end-of-run discrepancy summary.

**Acceptance Scenarios**:

1. **Given** `benchmark_ru_human_eval.csv` is present and the user enables benchmark mode for Russian, **When** evaluation completes, **Then** each matched row includes **accuracy_ai** and **accuracy_human** where the benchmark supplies a value, and **final_score** reflects **human over AI** when human is present.
2. **Given** benchmark mode is **off**, **When** the user evaluates Russian, **Then** behavior matches standard evaluation (no requirement to load the benchmark).
3. **Given** benchmark mode is **on** but the file is missing, **When** the user runs evaluation, **Then** the run fails with a clear error (no silent skip).
4. **Given** a benchmark `msgid` exists with no matching input string after cleaning, **When** evaluation completes, **Then** that situation is reported as a **stale benchmark entry** in logs or summary counts.

---

### Edge Cases

- Language folder missing or empty: evaluation should fail gracefully with a clear message, not silent success.
- Malformed or unreadable files: user receives a clear error or skip behavior consistent with requirements; partial runs should be defined (e.g., skip bad file vs abort entire run).
- All entries blank after cleaning: user is informed that there is nothing to score.
- Repeated runs same day: new exports do not overwrite prior results unless the user explicitly chooses overwrite (default must preserve history per persistence requirement).
- Only PO or only XLIFF present: handled per User Story 2.
- `./inputs/` must remain tracked in version control: project policy forbids ignoring this folder in ignore rules.
- Russian benchmark: duplicate `msgid` rows in the CSV, malformed rows, or encoding issues—the run MUST **fail fast** with a clear error in benchmark mode (no partial silent drops of benchmark data).
- Russian benchmark: the same `msgid` may be evaluated once for PO and once for XLIFF; **`accuracy_human`** MUST follow the benchmark’s **format-specific** human column when available so PO and XLIFF rows are not conflated.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST evaluate translations using exactly two quality dimensions: **Accuracy** and **Capitalization**. It MUST NOT report scores for **Variables** or **Naturalness** (those dimensions are out of scope for this refactor).
- **FR-002**: The tool MUST read translation content from a local project path structured as `./inputs/{language}/` where `{language}` identifies the target language (for example, `ru` for Russian).
- **FR-003**: Each language folder MUST be able to contain its own `.po` files and its own `.xliff` files as inputs to evaluation.
- **FR-004**: Before scoring, the tool MUST exclude any entries where the translation text is blank or empty (after any defined trimming of whitespace).
- **FR-005**: The tool MUST NOT delete previous evaluation result files when new evaluations are run; new outputs must be additive or use non-destructive naming so history remains available unless the user explicitly opts into overwrite (default is preserve).
- **FR-006**: The tool MUST produce a tabular export (spreadsheet-friendly) that includes Accuracy and Capitalization results in a way that supports comparing PO-sourced versus XLIFF-sourced outcomes for the same evaluation workflow.
- **FR-007**: The repository MUST keep `./inputs/` under version control: this folder MUST NOT be listed in ignore rules that would untrack it from collaborators’ clones.
- **FR-008**: For Russian, when benchmark mode is enabled, the tool MUST load `./inputs/ru/benchmark_ru_human_eval.csv` (canonical name) and MUST join benchmark rows to evaluated entries using **strict `msgid` equality** after input cleaning.
- **FR-009**: For any benchmark `msgid` that does not match an entry in the current inputs (after cleaning), the tool MUST classify and report **stale benchmark entries** (not ignore silently).
- **FR-010**: For Russian runs with benchmark mode, each applicable results row MUST expose **`accuracy_ai`** and **`accuracy_human`**. When the benchmark supplies distinct human scores per format, **`accuracy_human`** MUST match the row’s format (PO vs XLIFF). **`final_score`** (or equivalent accuracy gate) MUST use **human accuracy when present**, otherwise **automated accuracy**.
- **FR-011**: Benchmark comparison MUST be **opt-in** via an explicit option (e.g. **`--use-benchmark`**) in addition to selecting Russian; **`--lang ru` alone MUST NOT** activate benchmark logic.
- **FR-012**: When benchmark mode is requested and the benchmark file is missing or unusable, the tool MUST **fail with a clear error**.
- **FR-013**: After a benchmark run, the tool MUST emit an **end-of-run summary** that includes **critical discrepancies** between automated and human accuracy (at minimum the class of cases where one indicates pass and the other indicates fail, per agreed thresholds).
- **FR-014**: Data cleaning (blank/whitespace-only translations) MUST be applied **before** benchmark matching and automated scoring on a given entry.

### Key Entities *(include if feature involves data)*

- **Language input bundle**: A folder `./inputs/{language}/` containing one or more `.po` and/or `.xliff` files for that language.
- **Translatable entry**: A unit with source text, translated text, and identifiers as needed for matching; excluded if translation is blank after cleaning.
- **Evaluation run result**: A dated or sequenced tabular export holding Accuracy and Capitalization outcomes, tied to the input format (PO vs XLIFF) and language where applicable.
- **Benchmark reference set** (optional phase): Human Russian accuracy ground truth keyed by **`msgid`**, stored as `./inputs/ru/benchmark_ru_human_eval.csv` when using benchmark mode.
- **Stale benchmark entry**: A benchmark row whose `msgid` does not match any post-cleaning input entry.

### Assumptions

- “Blank” translation means empty or whitespace-only after trimming; tabs and line breaks are treated consistently with product convention.
- Comparing PO vs XLIFF may be implemented as separate runs or clearly labeled rows in one export; the user can tell which format produced which scores.
- The benchmark CSV maps **`msgid`** to human accuracy columns agreed in planning (column names in exports may vary; mapping is fixed in implementation). Human **capitalization** scores are not required from the benchmark file for MVP; **Capitalization** remains tool-generated per FR-001.

### Out of Scope

- Scoring dimensions other than Accuracy and Capitalization (including former Variables and Naturalness).
- Non-local primary data sources for routine evaluation (cloud-only inputs) unless later specified.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For a sample language folder with valid PO and XLIFF files, users obtain a complete tabular export with Accuracy and Capitalization populated within one evaluation session, without manual spreadsheet steps to compute those two metrics.
- **SC-002**: In tests with known blank translations mixed with valid ones, 100% of blank entries are excluded from scoring while valid entries are still scored.
- **SC-003**: After at least two evaluation runs on the same machine, earlier result files remain present and readable unless the user deliberately removes or overwrites them.
- **SC-004**: Stakeholders can state unambiguously—from the export alone—which rows correspond to PO versus XLIFF evaluation for the same language context.
- **SC-005**: When Russian benchmark data is provided, reviewers can complete a comparison workflow in a single sitting (under 30 minutes for typical batch size) and document any material mismatches between tool output and the benchmark.
- **SC-006**: With benchmark mode enabled, 100% of stale benchmark `msgid`s (no matching input) appear in reported stale counts or logs, and zero such cases are dropped without trace.
- **SC-007**: With benchmark mode enabled, reviewers can list **critical discrepancies** from the end-of-run summary without scanning the full per-row export.
