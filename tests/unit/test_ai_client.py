from src.core.ai_client import AIClient
from src.core.models import TranslationCandidate


def test_ai_client_fallback_scores_binary() -> None:
    client = AIClient(model="gpt-5.4")
    candidate = TranslationCandidate(
        msgid="Hello",
        source_en="Hello",
        translation_source="po",
        translation_text="Привет",
        ai_context="Greeting in app header",
        language_code="ru",
    )
    assert client.score_accuracy(candidate) in (0, 1)
    assert client.score_naturalness(candidate) in (0, 1)

