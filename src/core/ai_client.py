from __future__ import annotations

import time

from .config import get_openai_api_key
from .models import TranslationCandidate


class AIClient:
    """
    AI-assisted **accuracy** scoring only.
    Capitalization is scored in Python (`checks.check_capitalization`).
    Naturalness and placeholder/variable checks are not used in this tool (FR-001).
    """

    def __init__(
        self,
        model: str = "gpt-5.4",
        max_retries: int = 2,
        debug_prompts: bool = False,
    ) -> None:
        self.model = model
        self.max_retries = max_retries
        self.debug_prompts = debug_prompts

    def _heuristic_accuracy(self, candidate: TranslationCandidate) -> int:
        """Offline fallback when the API is unavailable."""
        if not candidate.translation_text.strip():
            return 0
        if candidate.source_en.strip() == candidate.translation_text.strip():
            return 0
        return 1

    def _call_openai(self, prompt: str) -> int:
        api_key = get_openai_api_key()
        if not api_key:
            return -1
        try:
            from openai import OpenAI  # type: ignore

            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=self.model,
                input=prompt,
                temperature=0,
            )
            text = (response.output_text or "").strip().lower()
            if "1" in text and "0" not in text:
                return 1
            if "0" in text and "1" not in text:
                return 0
            return -1
        except Exception:
            return -1

    def score_accuracy(self, candidate: TranslationCandidate) -> int:
        """
        Return 0/1: whether the translation is accurate in context (meaning preserved).
        Does not judge capitalization, naturalness, or placeholder preservation.
        """
        prompt = (
            "You evaluate UI translation accuracy only.\n"
            "Return 1 if the translation preserves the meaning of the English source "
            "given the product context. Return 0 if there is a clear mistranslation, "
            "wrong sense, important omission/addition, or serious error.\n"
            "Do not judge sentence capitalization or placeholder tokens here.\n"
            "Reply with a single character: 1 or 0.\n\n"
            f"Target language: {candidate.language_code}\n"
            f"Source: {candidate.source_en}\n"
            f"Translation: {candidate.translation_text}\n"
            f"Context: {candidate.ai_context or 'none'}\n"
        )
        if self.debug_prompts:
            print("----- AI ACCURACY PROMPT -----", flush=True)
            print(
                f"[lang={candidate.language_code}] [msgid={candidate.msgid!r}]",
                flush=True,
            )
            print(prompt, flush=True)
            print("----- END PROMPT -----", flush=True)
        for _ in range(self.max_retries + 1):
            score = self._call_openai(prompt)
            if score in (0, 1):
                return score
            time.sleep(0.2)
        return self._heuristic_accuracy(candidate)
