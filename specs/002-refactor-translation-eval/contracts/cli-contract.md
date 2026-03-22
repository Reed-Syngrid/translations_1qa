# CLI Contract: Refactored Translation Evaluator

**Version**: 0.1 (draft) | **Branch**: `002-refactor-translation-eval`

## Command

`python -m src.cli.translation_eval_cli`

## Arguments

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `--lang`, `-l` | yes | — | Language folder under `inputs`, e.g. `ru`, `es-ES`. |
| `--inputs-root` | no | `inputs` | Root directory containing `{lang}` subfolders. |
| `--limit`, `-n` | no | `100` | Max shared msgids to sample (positive int). |
| `--output`, `-o` | no | auto under `outputs/` | Output CSV path; must not delete existing files when omitted (new timestamp). |
| `--model` | no | (project default) | OpenAI model for accuracy. |
| `--use-benchmark` | no | off | Enable Russian benchmark CSV join and summary. **Only valid with `--lang ru`.** |
| `--verbose` | no | off | Progress logging. |

## Exit codes

| Code | Meaning |
|------|---------|
| `0` | Success |
| `2` | Invalid arguments (e.g. `limit <= 0`, `--use-benchmark` with non-`ru` lang) |
| `3` | No PO files found |
| `4` | No XLIFF files found |
| `5` | No shared msgids |
| `6` | Benchmark file missing or invalid when `--use-benchmark` |
| `7` | Encoding / IO error on inputs |

*(Exact numbering may align with existing CLI; document in code.)*

## Behavioral contract

1. **FR-014**: Entries with blank/whitespace-only translations are **never** scored or benchmark-joined.
2. **FR-011 / FR-012**: `--use-benchmark` without `ru` → error; with `ru` but missing `benchmark_ru_human_eval.csv` → error with path.
3. **FR-005**: Implementation never deletes previous `outputs/*.csv` when creating new runs.
