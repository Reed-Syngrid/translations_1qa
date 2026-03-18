# Research Decisions: Translation Quality Evaluation Tool

## Decision 1: Language filename matching and normalization
- **Decision**: Normalize locale codes to BCP-47-like lowercase language + optional uppercase region (e.g., `ru`, `fr`, `zh-CN`). Accept `-` and `_` variants in filenames.
- **Rationale**: Input files may use mixed naming conventions; normalization avoids false negatives.
- **Alternatives considered**:
  - Strict exact filename matching (rejected: too brittle).
  - Hardcoded language map (rejected: not scalable).

## Decision 2: Capitalization rule
- **Decision**: Compare sentence-initial capitalization category using first alphabetic character in source and translation:
  - uppercase vs lowercase must match
  - if no alphabetic chars in source, return pass.
- **Rationale**: Deterministic and language-agnostic enough for UI strings.
- **Alternatives considered**:
  - Full title-case comparison (rejected: locale-sensitive complexity).

## Decision 3: Placeholder taxonomy
- **Decision**: Support these placeholder families:
  - C-style: `%s`, `%d`, `%f`, `%1$s`
  - Brace indexed/named: `{0}`, `{name}`
  - Template style: `${name}`
- **Rationale**: Covers common Metabase translation placeholders.
- **Alternatives considered**:
  - ICU parser-level support only (rejected for current scope).

## Decision 4: OpenAI call strategy
- **Decision**: Evaluate each translation independently with optional retry (max 2 retries) and deterministic fallback heuristic if API is unavailable.
- **Rationale**: Keeps per-row traceability and isolates failures.
- **Alternatives considered**:
  - Batch prompts for many strings (rejected for easier debugging and per-row error reporting).

