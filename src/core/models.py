from dataclasses import dataclass


@dataclass
class RunConfig:
    language_code: str
    sample_size: int
    po_root: str
    xliff_root: str
    output_csv_path: str
    openai_model: str = "gpt-5.4"


@dataclass
class TranslationCandidate:
    msgid: str
    source_en: str
    translation_source: str  # po|xliff
    translation_text: str
    ai_context: str
    language_code: str


@dataclass
class EvaluationResult:
    msgid: str
    translation_source: str
    source_en: str
    translation_text: str
    language_code: str
    ai_context: str
    accuracy_score: int
    capitalization_score: int
    placeholder_score: int
    final_score: int
    placeholder_diagnostics: str = ""
    error_reason: str = ""

