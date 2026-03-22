# translations_1qa

Translation evaluation CLI: compares **PO** vs **XLIFF** strings under `./inputs/{lang}/`, scores **Accuracy** (AI + optional human benchmark) and **Capitalization** only.

## Quickstart

1. Put `.po` and `.xliff` files in `inputs/<lang>/` (e.g. `inputs/ru/`).
2. For Russian, place the human benchmark CSV under `inputs/ru/` (e.g. `benchmark_ru_human_eval.csv` or `Benchmark_ru_human_eval - Sheet1.csv`).
3. Run from the repo root:

```bash
python -m src.cli.translation_eval_cli --lang ru --inputs-root inputs --use-benchmark
```

**`--use-benchmark`** — joins the Russian human benchmark on `msgid`, fills **`accuracy_human_*`** next to **`accuracy_ai_*`**, prefers human scores for **`final_score`**, and prints a **benchmark summary** (stale msgids + critical AI vs human discrepancies). Only valid with **`--lang ru`**.

Run **without** the benchmark (AI-only human columns empty):

```bash
python -m src.cli.translation_eval_cli --lang ru --inputs-root inputs --limit 50
```

4. Results are written to **`outputs/translation_eval_<lang>_<timestamp>.csv`** (new file each run; no automatic deletion of old CSVs).

More detail: [`specs/002-refactor-translation-eval/quickstart.md`](specs/002-refactor-translation-eval/quickstart.md).

## Requirements

- Python 3.10+
- Dependencies: `polib`, `openai`, `python-dotenv` (see project setup)
- `OPENAI_API_KEY` for AI accuracy

## Branch

Feature work for the refactored evaluator: **`002-refactor-translation-eval`**.
