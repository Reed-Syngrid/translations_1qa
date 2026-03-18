# Tasks: Translation Quality Evaluation Tool

**Input**: Design documents from `/specs/001-translation-eval-tool/`  
**Prerequisites**: `plan.md` (required), `spec.md` (required for user stories)

**Tests**: Tests are included because the specification explicitly requires reliability and independent validation.

**Organization**: Tasks are grouped by user story so each story can be implemented and validated independently.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and baseline tooling

- [X] T001 Create project directories for `src/cli`, `src/core`, `tests/unit`, `tests/integration`, and `tests/fixtures` in repository root
- [X] T002 Initialize Python dependencies for `polib`, OpenAI client, and `pytest` in `requirements.txt`
- [X] T003 [P] Add environment variable loading for OpenAI key in `src/core/config.py`
- [X] T004 [P] Add test bootstrap configuration in `tests/conftest.py`
- [X] T004A [P] Configure lint and format tooling definitions in `pyproject.toml`
- [X] T004B Add QA gate script to run lint + format checks in `.specify/scripts/bash/qa-check.sh`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core modules required by all user stories

**CRITICAL**: No user story work begins until this phase is complete.

- [X] T004C Document and finalize unresolved planning decisions (filename language patterns, capitalization rules, placeholder taxonomy, AI batching strategy) in `specs/001-translation-eval-tool/research.md`
- [X] T004D Add unit test matrix from research decisions for capitalization and placeholders in `tests/unit/test_checks_matrix.py`
- [X] T005 Implement file discovery for language-specific `.po` and `.xliff` inputs in `src/core/file_discovery.py`
- [X] T006 Implement `.po` parser keyed by `msgid` and `msgstr` in `src/core/po_parser.py`
- [X] T007 Implement `.xliff` parser with source/target/context extraction in `src/core/xliff_parser.py`
- [X] T008 Implement shared `msgid` intersection and sampling logic in `src/core/matching.py`
- [X] T009 Implement core data models (`RunConfig`, `TranslationCandidate`, `EvaluationResult`) in `src/core/models.py`
- [X] T010 [P] Add unit tests for discovery/parsing/matching in `tests/unit/test_file_discovery.py`
- [X] T011 [P] Add unit tests for `.po` and `.xliff` parsing in `tests/unit/test_parsers.py`
- [X] T011A Run mandatory QA gate (lint/format + tests) before unlocking story phases using `.specify/scripts/bash/qa-check.sh`

**Checkpoint**: Foundation ready; user story phases can proceed.

---

## Phase 3: User Story 1 - Compare two translation sets for a locale (Priority: P1) 🎯 MVP

**Goal**: Generate a CSV comparing `.po` vs `.xliff` translations for the same sampled `msgid` set.

**Independent Test**: Run CLI with `--lang ru --limit 10` and verify CSV rows contain `msgid`, source English, both translations, criteria scores, and final scores.

### Tests for User Story 1

- [X] T012 [P] [US1] Add integration test for end-to-end CSV generation in `tests/integration/test_cli_csv_output.py`

### Implementation for User Story 1

- [X] T013 [P] [US1] Implement scoring orchestrator for two translation sources in `src/core/scoring.py`
- [X] T014 [P] [US1] Implement CSV output writer with required columns in `src/core/output.py`
- [X] T015 [US1] Implement CLI command orchestration for parse/match/score/output in `src/cli/translation_eval_cli.py`
- [X] T016 [US1] Add structured run summary logging for evaluated rows and failures in `src/core/run_report.py`

**Checkpoint**: US1 is independently functional and can be demoed as MVP.

---

## Phase 4: User Story 2 - Use AI context to judge accuracy and naturalness (Priority: P1)

**Goal**: Evaluate accuracy and naturalness with OpenAI `gpt-5.4` using extracted AI context.

**Independent Test**: Verify mocked AI requests include source English, target language, translation text, and AI context when available.

### Tests for User Story 2

- [X] T017 [P] [US2] Add unit tests for OpenAI prompt composition and parsing in `tests/unit/test_ai_client.py`

### Implementation for User Story 2

- [X] T018 [US2] Implement OpenAI client wrapper for accuracy and naturalness scoring in `src/core/ai_client.py`
- [X] T019 [US2] Integrate AI scoring into evaluation pipeline in `src/core/scoring.py`
- [X] T020 [P] [US2] Add retry and failure handling for AI calls with error propagation in `src/core/ai_client.py`
- [X] T021 [P] [US2] Add fallback behavior for missing AI context markers in `src/core/xliff_parser.py`

**Checkpoint**: US2 independently delivers contextual AI scoring.

---

## Phase 5: User Story 3 - Enforce placeholder and capitalization fidelity (Priority: P2)

**Goal**: Add deterministic checks for capitalization and placeholder preservation.

**Independent Test**: Feed fixtures with deliberate placeholder/capitalization mismatches and verify criterion score `0` on affected translations.

### Tests for User Story 3

- [X] T022 [P] [US3] Add unit tests for capitalization and placeholder token matching in `tests/unit/test_checks.py`

### Implementation for User Story 3

- [X] T023 [US3] Implement capitalization rule check in `src/core/checks.py`
- [X] T024 [US3] Implement placeholder token extraction and comparison in `src/core/checks.py`
- [X] T025 [US3] Integrate deterministic checks into scoring pipeline in `src/core/scoring.py`
- [X] T026 [P] [US3] Add placeholder diagnostics fields to output rows in `src/core/output.py`

**Checkpoint**: US3 independently delivers deterministic translation integrity checks.

---

## Phase 6: User Story 4 - Configure sample size and target language (Priority: P2)

**Goal**: Support CLI parameters for language and sample size with clear validation errors.

**Independent Test**: `--lang fr --limit 25` returns <=25 French rows; unsupported language exits with clear non-zero error and message.

### Tests for User Story 4

- [X] T027 [P] [US4] Add CLI argument validation tests for language and limit in `tests/unit/test_cli_args.py`

### Implementation for User Story 4

- [X] T028 [US4] Implement and validate `--lang` and `--limit` options in `src/cli/translation_eval_cli.py`
- [X] T029 [P] [US4] Wire `--lang` to file discovery filtering in `src/core/file_discovery.py`
- [X] T030 [P] [US4] Wire `--limit` to deterministic sampling in `src/core/matching.py`
- [X] T031 [US4] Implement explicit error paths for missing language files in `src/cli/translation_eval_cli.py`

**Checkpoint**: US4 independently delivers configurable evaluation runs.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Cross-story hardening and documentation

- [X] T032 [P] Add malformed-file edge-case fixtures and regression tests in `tests/integration/test_malformed_inputs.py`
- [X] T033 [P] Add quickstart run instructions for analysts in `specs/001-translation-eval-tool/quickstart.md`
- [X] T034 Add final execution metrics (runtime, total rows, AI failures) to run report output in `src/core/run_report.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: no dependencies.
- **Phase 2 (Foundational)**: depends on Phase 1; blocks all user stories.
- **Phases 3-6 (User Stories)**: depend on Phase 2 completion.
- **Phase 7 (Polish)**: depends on desired user stories being complete.

### User Story Dependencies

- **US1 (P1)**: starts immediately after Phase 2 and defines MVP.
- **US2 (P1)**: depends on foundation and reuses US1 scoring/output pipeline.
- **US3 (P2)**: depends on foundation; can be integrated into scoring after US1 baseline.
- **US4 (P2)**: depends on foundation; can proceed in parallel with US2/US3 except shared CLI file edits.

### Within Each User Story

- Tests first where listed, then implementation.
- Parsing/model tasks before scoring integration.
- Scoring integration before final CSV/report updates.

### Parallel Opportunities

- Phase 1 tasks marked `[P]` can run together.
- Phase 2 parser tests (`T010`, `T011`) can run in parallel.
- US2 fallback/context handling (`T020`, `T021`) can run in parallel.
- US3 diagnostics task (`T026`) can run in parallel with scoring integration.
- US4 wiring tasks (`T029`, `T030`) can run in parallel.

---

## Parallel Example: User Story 2

```bash
# Parallelizable US2 tasks
Task: "T020 [US2] Add retry and failure handling for AI calls in src/core/ai_client.py"
Task: "T021 [US2] Add fallback behavior for missing AI context markers in src/core/xliff_parser.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 and Phase 2.
2. Complete Phase 3 (US1).
3. Validate end-to-end CSV generation and use as first deliverable.

### Incremental Delivery

1. Add US2 for contextual AI scoring.
2. Add US3 for deterministic integrity checks.
3. Add US4 for robust CLI configurability.
4. Finish with Phase 7 polish.

### Parallel Team Strategy

1. One developer handles parser/discovery baseline and US1 pipeline.
2. A second developer builds AI client and US2 tests.
3. A third developer adds deterministic checks and US3 diagnostics.

---

## Notes

- Every task follows required checklist format: `- [ ] T### [P?] [US?] Description with file path`.
- Story labels are included only for user-story phases.
- Suggested MVP scope: **Phase 3 (US1)** after Setup + Foundational completion.

