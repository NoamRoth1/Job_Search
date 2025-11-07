"""Resume rewrite helpers for ATS-friendly suggestions."""
from __future__ import annotations

import json
import logging

from ..io_models import KeywordMatch

logger = logging.getLogger(__name__)


def _openai_rewrite(bullet: str, keywords: list[str]) -> str | None:
    try:
        import openai

        client = openai.OpenAI()  # type: ignore[attr-defined]
        user_prompt = (
            "Target keywords: {keywords}\n"
            "Original bullet: {bullet}\n"
            "Constraints: \u226430 words, strong verb, include one metric if available, no fluff."
        ).format(keywords=", ".join(keywords), bullet=bullet)
        response = client.responses.create(  # type: ignore[attr-defined]
            model="gpt-4.1-mini",
            temperature=0.3,
            input=[
                {"role": "system", "content": "You improve resume bullets while preserving truthfulness and adding relevant keywords naturally."},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = response.output[0].content[0].text  # type: ignore[index]
        data = json.loads(content)
        return data.get("edited")
    except Exception as exc:  # pragma: no cover - optional path
        logger.warning("OpenAI rewrite failed: %s", exc)
        return None


def suggest_rewrites(matches: list[KeywordMatch], resume_bullets: list[str]) -> list[str]:
    """Return ATS-friendly rewrite suggestions for weak or missing keywords."""

    suggestions: list[str] = []
    for match in matches:
        if match.category == "present":
            continue
        bullet = resume_bullets[0] if resume_bullets else "Drove results"
        rewritten = _openai_rewrite(bullet, [match.keyword])
        if rewritten:
            suggestions.append(rewritten)
        else:
            suggestions.append(
                f"If applicable, rephrase as: {bullet.split()[0] if bullet.split() else 'Led'} projects featuring {match.keyword} and quantified outcomes."
            )
    return suggestions
