# Quickstart

## 1) Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 2) Set API key (optional but recommended)

```powershell
$env:OPENAI_API_KEY="your_key_here"
```

## 3) Run evaluation

```powershell
python -m src.cli.translation_eval_cli `
  --lang ru `
  --limit 25 `
  --po-root "C:\metabase_translations\metabase_v0_57_15\metabase-0.57.15\locales" `
  --xliff-root "C:\metabase_translations\Ai_translations"
```

## 4) Review output

CSV files are written under `outputs/` unless `--output` is provided.

