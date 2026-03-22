from dataclasses import dataclass


@dataclass
class RunConfig:
    """CLI run configuration."""

    language_code: str
    sample_size: int
    inputs_root: str
    output_csv_path: str
    openai_model: str = "gpt-5.4"
    use_benchmark: bool = False


@dataclass
class TranslationCandidate:
    msgid: str
    source_en: str
    translation_source: str  # po|xliff
    translation_text: str
    ai_context: str
    language_code: str


@dataclass
class BenchmarkRow:
    """Human benchmark scores keyed by msgid (Russian benchmark CSV)."""

    msgid: str
    accuracy_human_po: int | None
    accuracy_human_xliff: int | None


@dataclass
class EvaluationResult:
    """Per-candidate evaluation: Accuracy (AI + optional human) and Capitalization only."""

    msgid: str
    translation_source: str
    source_en: str
    translation_text: str
    language_code: str
    ai_context: str
    accuracy_ai: int
    accuracy_human: int | None
    capitalization_score: int
    final_score: int
    error_reason: str = ""
