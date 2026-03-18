# Feature Specification: Translation Quality Evaluation Tool

**Feature Branch**: `001-translation-eval-tool`  
**Created**: 2026-03-11  
**Status**: Draft  
**Input**: User description: "i need a tool to analyse and compair quality of different versions of thanslations of metabase strings that appear in application UI. as imput sourses will recieve 2 types of files with translations .PO files and .xliff files. the files will be located in the local folder on my computer C:\metabase_translations\Ai_translations xliff files and C:\metabase_translations\metabase_v0_57_15\metabase-0.57.15\locales with po files. Both of those files will contain different versions of translations for similar list of strings from english to the target foreign language. The target foreign language is indicated on the file name. ... (truncated for brevity in spec header)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Compare two translation sets for a locale (Priority: P1)

A localization QA analyst wants to compare the quality of two different translation sources (Metabase `.po` files vs AI‑generated `.xliff` files) for the same target language so they can quickly identify which source is better overall and where it fails.

**Why this priority**: This is the core value of the tool: making a quality judgment between two translation sources for a given locale over a representative sample of UI strings.

**Independent Test**: With only this story implemented, a QA analyst can point the tool at the configured `.po` and `.xliff` directories, specify a target language code (e.g. `ru`) and a sample size, and receive a CSV that contains side‑by‑side translations plus per‑criterion scores for each source.

**Acceptance Scenarios**:

1. **Given** the user has `.po` files under `C:\metabase_translations\metabase_v0_57_15\metabase-0.57.15\locales` and `.xliff` files under `C:\metabase_translations\Ai_translations`, **When** they run the tool with language `ru` and sample size `100`, **Then** the tool creates a CSV containing 100 rows where each row includes `msgid`, the `.po` translation, the `.xliff` translation, and scores for each evaluation criterion for both sources.
2. **Given** the user runs the tool for a language that exists in `.po` but not in `.xliff`, **When** the tool executes, **Then** it either warns that no matching `.xliff` files were found and exits with a clear error code, or reports that zero comparable strings were found, without creating a partial or misleading CSV.

---

### User Story 2 - Use AI context to judge accuracy and naturalness (Priority: P1)

A localization QA analyst wants the evaluation to use rich contextual information embedded in the `.xliff` files (between `✨ AI Context` and `✨ 🔚`) so that the AI model can judge whether each translation is accurate and natural in its real UI usage.

**Why this priority**: Without contextual hints, AI evaluation of short UI strings is error‑prone; leveraging existing AI context significantly improves evaluation reliability.

**Independent Test**: With this story alone, the QA analyst can run the tool for a small sample and manually inspect that the AI prompts include the correct AI context snippets from the `.xliff` file for each `msgid` and that the resulting scores change when context is altered.

**Acceptance Scenarios**:

1. **Given** an `.xliff` `trans-unit` that contains an AI context block between `✨ AI Context` and `✨ 🔚`, **When** the tool evaluates the corresponding translation, **Then** the AI request payload for "accuracy in given context" and "naturalness" includes the original English string, the target language code, the translated string under evaluation, and the extracted AI context.
2. **Given** an `.xliff` `trans-unit` without an AI context block, **When** the tool evaluates that translation, **Then** it still evaluates the translation using at least the source string and target translation but either omits context or clearly indicates "no context available" in the AI prompt.

---

### User Story 3 - Enforce placeholder and capitalization fidelity (Priority: P2)

A localization QA analyst wants the tool to automatically detect capitalization mismatches and missing or altered placeholders/variables between the English source string and each translation, so that functional regressions and subtle UX inconsistencies are caught early.

**Why this priority**: Incorrect capitalization and broken placeholders cause visible UI defects and even runtime errors; they are easy to check programmatically and should not require human reviewers to spot them manually.

**Independent Test**: With this story implemented, even without AI‑based scoring turned on, a QA analyst can run the tool and get a CSV that clearly flags which translations fail capitalization or placeholder checks.

**Acceptance Scenarios**:

1. **Given** a source string that starts with an uppercase letter, **When** the tool evaluates translations, **Then** any translation that does not preserve equivalent sentence‑initial capitalization (according to simple language‑agnostic rules) is marked with a `0` for the capitalization criterion.
2. **Given** a source string that contains placeholders such as `{0}`, `{1}`, `%s`, `%d` or `{variable_name}`, **When** the tool evaluates translations, **Then** any translation that omits or alters the set of placeholders (names or indices) is marked with a `0` for the variable/placeholder criterion and the affected placeholders are reported in a machine‑readable way.

---

### User Story 4 - Configure sample size and target language (Priority: P2)

A QA analyst wants to control how many strings the tool evaluates and which target language to focus on, so they can run quick spot‑checks or deeper audits without changing the code.

**Why this priority**: Different review sessions need different sample sizes, and the same codebase may have many locales. Making language and sample size parameters avoids reconfiguring paths or code for each run.

**Independent Test**: With only this story, a CLI user can set `--lang ru --limit 25` and see that exactly 25 comparable strings are chosen for Russian; changing `--lang fr` switches to French files without further configuration.

**Acceptance Scenarios**:

1. **Given** the user passes `--lang ru` and `--limit 25` to the CLI, **When** the tool runs, **Then** the CSV contains at most 25 rows and every row refers to a `msgid` present in both Russian `.po` and `.xliff` sources.
2. **Given** the user passes an unsupported or missing language code, **When** the tool runs, **Then** it exits with a clear, non‑zero error code and a message explaining that no matching `.po`/`.xliff` pairs were found for that language.

---

### Edge Cases

- What happens when there are fewer shared `msgid` values between `.po` and `.xliff` than the requested sample size?  
  - Tool should evaluate all available shared `msgid`s, warn about the shortfall, and still produce a valid CSV.
- How does the system handle network or API failures when calling the OpenAI `gpt-5.4` model?  
  - Tool should retry a limited number of times per request and clearly mark rows where AI evaluation failed, without crashing the entire run.
- What happens if `.xliff` AI context blocks are malformed (missing `✨ 🔚`, nested markers, or unexpected markup)?  
  - Tool should fall back to a safe parser that either extracts best‑effort context or treats context as unavailable, without throwing unhandled exceptions.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST scan a configured filesystem root for `.po` files under `metabase_v0_57_15/metabase-0.57.15/locales` and `.xliff` files under `Ai_translations`, and match files by target language code derived from filenames (e.g., `ru`, `fr`, `de`, `zh-CN`).
- **FR-002**: The tool MUST identify a common set of strings by `msgid` that appear in both the `.po` files and the `.xliff` files for the chosen target language.
- **FR-003**: For each selected `msgid`, the tool MUST extract:
  - The English source string (`msgid`)
  - The `.po` translation (`msgstr`)
  - The `.xliff` translation from the `<target>` element in the corresponding `<trans-unit>`
  - The AI context text between `✨ AI Context` and `✨ 🔚` in the relevant `.xliff` `<context>` node, when present.
- **FR-004**: The tool MUST allow the caller to specify the target language code (e.g., `--lang ru`) and the maximum number of strings to evaluate (e.g., `--limit 100`) via command‑line arguments or equivalent configuration.
- **FR-005**: The tool MUST evaluate, for each translation string (per source: `.po` and `.xliff`), the following criteria, producing a binary score (1/0) for each:
  - Accuracy in the given context (using OpenAI `gpt-5.4`)
  - Capitalization match with the English source string
  - Variable / placeholder preservation relative to the English source string
  - Naturalness for data analysts and data engineers (using OpenAI `gpt-5.4`)
- **FR-006**: The tool MUST compute a "final score" per translation string that is `1` only if all other criteria (accuracy, capitalization, placeholders, naturalness) are `1`, otherwise `0`.
- **FR-007**: The tool MUST output a CSV file that, for each evaluated `msgid`, includes at minimum:
  - `msgid`
  - English source string
  - `.po` translation
  - `.xliff` translation
  - AI context snippet (or indicator that none was available)
  - Per‑criterion scores for each translation source
  - Final score per translation source.
- **FR-008**: The tool MUST be able to run non‑interactively from a CLI on Windows (PowerShell) given only the root directory path, target language code, and sample size.
- **FR-009**: The tool MUST log or report any untranslated `msgid`s, missing translations, malformed files, or AI evaluation failures in a way that can be inspected after the run (e.g., sidecar log file or structured error summary).

### Key Entities *(include if feature involves data)*

- **TranslationCandidate**
  - Attributes: `msgid`, `source_en`, `translation_source` (enum: `po`, `xliff`), `translation_text`, `ai_context`, `language_code`.
- **EvaluationResult**
  - Attributes: `msgid`, `translation_source`, `accuracy_score`, `capitalization_score`, `placeholder_score`, `naturalness_score`, `final_score`, `error_reason` (optional).
- **RunConfig**
  - Attributes: `root_path`, `po_subpath`, `xliff_subpath`, `language_code`, `sample_size`, `openai_model` (default `gpt-5.4`), `output_csv_path`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Given valid `.po` and `.xliff` files for at least one language, running the CLI with default settings MUST produce a CSV file with at least 50 evaluated strings and no unhandled exceptions.
- **SC-002**: For a curated test set where human reviewers have pre‑labeled "good" vs "bad" translations, at least 80% of cases MUST agree with the tool’s final score for that translation source.
- **SC-003**: Running the tool on a sample of 100 strings MUST complete within a target time budget (e.g., under 10 minutes) given reasonable OpenAI rate limits and batching, or else clearly report that external API limits are the bottleneck.
- **SC-004**: Localization QA analysts report that they can make a confident decision about which translation source (e.g., `.po` vs `.xliff`) is better for a given language after reviewing a single CSV export from the tool, without manually re‑evaluating more than 10% of strings.

