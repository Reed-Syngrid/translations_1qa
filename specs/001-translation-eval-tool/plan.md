# Implementation Plan: Translation Quality Evaluation Tool

**Branch**: `001-translation-eval-tool` | **Date**: 2026-03-11 | **Spec**: `specs/001-translation-eval-tool/spec.md`
**Input**: Feature specification from `/specs/001-translation-eval-tool/spec.md`

## Summary

We will build a small, scriptable CLI tool that runs on Windows (PowerShell friendly) and evaluates the quality of two translation sources for Metabase UI strings: upstream `.po` files and AI‑generated `.xliff` files. The tool will:

- Discover and match `.po` and `.xliff` files by language code.
- Identify a shared set of `msgid`s present in both sources.
- Extract translations and AI context from `.xliff`.
- Call OpenAI `gpt-5.4` to score each translation on accuracy and naturalness in context.
- Perform deterministic checks for capitalization and placeholder fidelity.
- Emit a CSV summarizing side‑by‑side translations and per‑criterion scores.

## Technical Context

**Language/Version**: Python 3.11 (or compatible 3.10+)  
**Primary Dependencies**:  
- `polib` (for parsing `.po` files)  
- `lxml` or `xml.etree.ElementTree` (for parsing `.xliff` XML)  
- `python-dotenv` (optional, for loading OpenAI API keys)  
- `openai` (or official client for `gpt-5.4`)  
**Storage**: Local filesystem only; no persistent DB. Outputs are CSV and optional log files.  
**Testing**: `pytest` for unit tests around parsing, matching, and scoring logic.  
**Target Platform**: Windows (PowerShell) first, but code should remain OS‑agnostic where possible.  
**Project Type**: CLI utility (single repo folder, no long‑lived service).  
**Performance Goals**: Handle ~100–300 strings per run without hitting OpenAI rate limits; underlying parsing and string matching should be effectively instantaneous at this scale.  
**Constraints**:  
- Must not require installing Metabase itself; operates on exported `.po`/`.xliff` files only.  
- Must handle intermittent OpenAI failures gracefully.  
**Scale/Scope**: Single CLI, single responsibility: comparing two translation sources for one locale at a time.

## Constitution Check

- **Source of truth**: We treat upstream Metabase `.po` files and the `.xliff` files as inputs; the tool must not mutate them.  
- **Completeness & coverage**: For each run, we only claim coverage over the sampled set; the tool should report sample size and total shared `msgid`s found.  
- **Consistency & placeholders**: Placeholder checks must be strict and deterministic to avoid runtime translation bugs.  
- **Review & QA**: Provide a simple way to run dry‑runs on a known test corpus; ensure CSV output is diff‑friendly and stable.  
- **Traceability**: Each run should log configuration (language, sample size, file roots, model) and timestamp so results can be reproduced.

No constitution violations are planned; this is a read‑only analysis tool with well‑bounded scope.

## Project Structure

### Documentation (this feature)

```text
specs/001-translation-eval-tool/
├── spec.md
├── plan.md
├── research.md          # optional, can be added later
├── data-model.md        # optional, can be added later if needed
├── quickstart.md        # optional: brief "how to run" for analysts
└── tasks.md
```

### Source Code (repository root)

```text
src/
├── cli/
│   └── translation_eval_cli.py          # entrypoint for the CLI
├── core/
│   ├── file_discovery.py                # find & match .po / .xliff by language
│   ├── po_parser.py                     # parse .po and expose msgid/msgstr mappings
│   ├── xliff_parser.py                  # parse .xliff, extract targets & AI context
│   ├── matching.py                      # intersect msgids across sources, sampling
│   ├── checks.py                        # capitalization + placeholder checks
│   ├── ai_client.py                     # OpenAI wrapper for gpt-5.4 calls
│   └── scoring.py                       # orchestrate per‑criterion scoring + final score
└── outputs/
    └── (git‑ignored) CSV exports, logs

tests/
├── unit/
│   ├── test_po_parser.py
│   ├── test_xliff_parser.py
│   ├── test_matching.py
│   ├── test_checks.py
│   └── test_scoring.py
└── fixtures/
    ├── sample.po
    ├── sample.xliff
    └── malformed/
```

**Structure Decision**: Single‑project CLI layout under `src/` is sufficient. No need for separate backend/frontend projects because there is no UI; analysis happens via CLI and CSV output. Tests live under `tests/` with fixtures mirroring expected input file shapes.

## Phase 0 – Research / Clarifications

1. Confirm exact filename patterns for `.po` and `.xliff` language codes (e.g., `ru.po`, `ru_RU.po`, `metabase-frontend-ru.xliff`, etc.).  
2. Decide normalization rules for capitalization comparison across languages (e.g., focus on first character only; ignore locales with non‑Latin scripts beyond simple heuristics).  
3. Enumerate placeholder patterns to support (e.g., `{0}`, `{1}`, `%s`, `%d`, `{variable}`, `${variable}`) and document limitations.  
4. Decide on batching strategy for OpenAI calls (e.g., group 5–10 strings per request vs one per request) based on model context limits and cost.  
5. Define minimal configuration for OpenAI (env var name for API key, optional base URL if using a proxy).

## Phase 1 – Design & Data Model

1. **Data structures**
   - Design `TranslationCandidate` and `EvaluationResult` Python dataclasses mirroring the entities in the spec.  
   - Decide on an internal representation for placeholder sets (e.g., normalized list of tokens) for easy comparison.
2. **Parsing layer**
   - For `.po`: use `polib` (or a simple custom parser) to load entries keyed by `msgid` with associated `msgstr`.  
   - For `.xliff`: parse XML, locating `<trans-unit>` nodes, reading `<source>`, `<target>`, and AI context from `<context>` blocks.
3. **Matching & sampling**
   - Implement a matching layer that intersects `msgid`s across `.po` and `.xliff` for the target language, then samples deterministically (e.g., sorted `msgid`s, then take first N or use a seeded random sample).  
4. **Scoring**
   - Define a scoring pipeline that, for each `TranslationCandidate`, runs:
     1. Placeholder + capitalization checks (pure Python, deterministic).  
     2. AI evaluation for accuracy and naturalness via `ai_client`.  
     3. Final score computation.  
5. **Output format**
   - Define a consistent CSV column order that can be easily filtered and pivoted in spreadsheets.

## Phase 2 – Implementation Plan

1. **CLI & configuration**
   - Implement a `translation-eval` CLI command (e.g., `python -m src.cli.translation_eval_cli`) that accepts:
     - `--lang` / `-l` (target language code).  
     - `--limit` / `-n` (maximum number of strings).  
     - `--po-root` and `--xliff-root` (optional; default to the given Metabase paths).  
     - `--output` (CSV path; default `outputs/translation_eval_[lang]_[timestamp].csv`).  
   - Load OpenAI API key from environment or a `.env` file.
2. **File discovery**
   - Implement `file_discovery` to:
     - Locate all `.po` files for the requested language under the `locales` root.  
     - Locate all `.xliff` files for the requested language under `Ai_translations`.  
     - Validate that at least one pair of files exists; otherwise exit with an informative error.
3. **Parsing implementations**
   - Implement `po_parser` and `xliff_parser` modules with robust error handling and unit tests.  
   - Ensure AI context extraction handles missing or malformed markers gracefully.
4. **Matching and sampling**
   - Implement `matching` that:
     - Builds `TranslationCandidate` instances for each shared `msgid`.  
     - Applies sampling logic based on `--limit`.  
   - Include safeguards for very small intersection sizes.
5. **Checks and AI integration**
   - Implement `checks` for capitalization and placeholders.  
   - Implement `ai_client` to interact with OpenAI `gpt-5.4`, exposing a simple function like `score_translation(candidate, criteria) -> dict`.  
   - Add minimal retry logic and structured error reporting for failed AI calls.
6. **Scoring aggregation & CSV writer**
   - Implement `scoring` to combine deterministic and AI‑based results for each candidate.  
   - Implement a CSV writer that writes one row per `(msgid, translation_source)` pair with all required fields.
7. **Logging & observability**
   - Add optional verbose logging (e.g., `--verbose`) to trace which files, `msgid`s, and AI calls were made.  
   - Capture a summary at the end (count of evaluated strings, failures, runtime).

## Complexity Tracking

No exceptional complexity beyond a small CLI utility is anticipated. If later we add a UI or multi‑project structure, we should revisit this section.

