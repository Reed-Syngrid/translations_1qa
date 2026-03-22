# Quickstart: Refactored Translation Evaluator

**Branch**: `002-refactor-translation-eval`

## Prerequisites

- Python 3.10+
- Dependencies installed (`pip install -e .` or `pip install -r requirements.txt` per repo).
- `OPENAI_API_KEY` set for AI accuracy scoring.

## Layout

```text
inputs/
└── {lang}/
    ├── *.po
    ├── *.xliff
    └── ru/benchmark_ru_human_eval.csv   # only for --use-benchmark
outputs/
└── translation_eval_{lang}_{timestamp}.csv
```

## Commands (after implementation)

```powershell
# Standard evaluation (local inputs)
python -m src.cli.translation_eval_cli --lang ru --inputs-root inputs --limit 100

# Russian + human benchmark join + summary
python -m src.cli.translation_eval_cli --lang ru --inputs-root inputs --limit 100 --use-benchmark
```

## Branch safety

Commit changes on **`002-refactor-translation-eval`**; merge to `main` via PR per team policy.
