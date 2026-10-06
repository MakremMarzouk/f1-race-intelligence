import json
from typing import Any

import httpx

from app.core.config import settings


class OllamaBriefingService:
    """Turns validated race analysis into a short factual briefing."""

    def generate_briefing(self, race_analysis: dict[str, Any]) -> str:
        prompt = (
            "You are a precise Formula 1 race reporter. Write an engaging, "
            "post-race briefing of no more than 80 words.\n"
            "Use only facts explicitly present in the JSON. Never invent details or "
            "infer causes, strategy, or driver motives. Omit missing or null facts. "
            "Preserve names, positions, and points exactly. Use neutral, literal "
            "wording; do not judge a performance or exaggerate it.\n"
            "Start with a short headline, then write 2–3 concise sentences. Prioritize "
            "the winner and podium, then the biggest position gain, fastest lap, "
            "DNFs, or points if available. Avoid filler, predictions, and repeating "
            "the full data. Proofread for grammar, normal spaces between words, "
            "and sentence case.\n\n"
            f"RACE FACTS:\n{json.dumps(race_analysis, ensure_ascii=False)}"
        )

        try:
            response = httpx.post(
                f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
                timeout=120.0,
            )
            response.raise_for_status()
            briefing = response.json().get("response", "").strip()
        except (httpx.RequestError, httpx.HTTPStatusError, ValueError) as error:
            raise RuntimeError("Ollama could not generate the briefing.") from error

        if not briefing:
            raise RuntimeError("Ollama returned an empty briefing.")

        return briefing
