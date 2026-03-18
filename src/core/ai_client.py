from __future__ import annotations

import time

from .config import get_openai_api_key
from .models import TranslationCandidate


class AIClient:
    def __init__(
        self,
        model: str = "gpt-5.4",
        max_retries: int = 2,
        debug_prompts: bool = False,
    ) -> None:
        self.model = model
        self.max_retries = max_retries
        self.debug_prompts = debug_prompts

    def _heuristic_score(self, candidate: TranslationCandidate, criterion: str) -> int:
        # Offline fallback: deterministic minimal heuristic.
        if not candidate.translation_text.strip():
            return 0
        if (
            criterion == "accuracy"
            and candidate.source_en.strip() == candidate.translation_text.strip()
        ):
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

    def _score(self, candidate: TranslationCandidate, criterion: str) -> int:
        prompt = (
            "You are a strict evaluator of software UI translations.\n"
            "Evaluate exactly one candidate translation of an English source string "
            "into a target language.\n\n"
            "Scoring criteria:\n"
            "1. accuracy_in_context: Score 1 only if the translation preserves the "
            "meaning of the English source and fits the provided UI/product context. "
            "Fail for clear mistranslation, wrong sense in context, important "
            "omission/addition, or clearly unnatural / ungrammatical UI wording. "
            "Do NOT fail for harmless stylistic variation, different word order, "
            "normal target-language grammar or punctuation differences.\n"
            "2. capitalization_match: Score 1 if sentence-initial capitalization is "
            "appropriately aligned with the source, or any difference is justified "
            "by target-language orthography or UI conventions. Fail only for a real "
            "capitalization inconsistency.\n"
            "3. placeholder_preservation: Score 1 only if the translation preserves "
            "exactly the same placeholders as the source (e.g. {0}, {name}, %s, "
            "%1$s, ${name}); placeholders may move position but tokens must remain "
            "identical. Fail if any placeholder is missing, added, renamed, "
            "reindexed, or reformatted.\n"
            "4. final_score: 1 only if all relevant criteria above are 1; otherwise 0.\n\n"
            "Evaluation rules:\n"
            "- Use the provided context to resolve ambiguity.\n"
            "- If context is insufficient, do not fail accuracy unless there is a "
            "clear error.\n"
            "- Apply normal conventions of the target language.\n"
            "- Evaluate each criterion independently.\n\n"
            "Now evaluate ONE criterion for ONE translation.\n"
            "Return only a single character: 1 (criterion met) or 0 (criterion not met).\n"
            f"Criterion: {criterion}\n"
            f"Target language: {candidate.language_code}\n"
            f"Source: {candidate.source_en}\n"
            f"Translation: {candidate.translation_text}\n"
            f"Context: {candidate.ai_context or 'none'}\n"
        )
        if self.debug_prompts:
            print("----- AI EVAL PROMPT -----", flush=True)
            print(
                f"[criterion={criterion}] [lang={candidate.language_code}] "
                f"[msgid={candidate.msgid!r}]",
                flush=True,
            )
            print(prompt, flush=True)
            print("----- END PROMPT -----", flush=True)
        for _ in range(self.max_retries + 1):
            score = self._call_openai(prompt)
            if score in (0, 1):
                return score
            time.sleep(0.2)
        return self._heuristic_score(candidate, criterion)

    def score_accuracy(self, candidate: TranslationCandidate) -> int:
        return self._score(candidate, "accuracy-in-context")

    def score_naturalness(self, candidate: TranslationCandidate) -> int:
        return self._score(candidate, "naturalness-for-data-analysts-and-engineers")

