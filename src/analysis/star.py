"""STAR bullet generation utilities."""
from __future__ import annotations

import json
import logging

from ..io_models import StarBullet

logger = logging.getLogger(__name__)


STAR_SYSTEM_PROMPT = "You write one-line STAR bullets that are truthful, concise, numeric, and tailored to the target job."


def _call_openai(prompt: str, *, temperature: float = 0.3) -> list[StarBullet]:
    import openai

    client = openai.OpenAI()  # type: ignore[attr-defined]
    response = client.responses.create(  # type: ignore[attr-defined]
        model="gpt-4.1-mini",
        temperature=temperature,
        input=[{"role": "system", "content": STAR_SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
    )
    message = response.output[0].content[0].text  # type: ignore[index]
    data = json.loads(message)
    bullets = [StarBullet(**item) for item in data.get("bullets", [])]
    return bullets


def _fallback_bullet(role: str | None, requirement: str, line: str | None) -> StarBullet:
    base = line or "Delivered project outcomes"
    situation = requirement.split(".")[0]
    bullet = f"Drove {situation.lower()} by {base.lower()} to achieve measurable impact"
    words = bullet.split()
    if len(words) > 35:
        words = words[:35]
    bullet = " ".join(words)
    bullet = bullet[:1].upper() + bullet[1:]
    rationale = "S: requirement context, T: goal, A: described action, R: highlight impact"
    return StarBullet(bullet=bullet, rationale=rationale)


def generate_star_bullets(
    *,
    role: str | None,
    company: str | None,
    requirement: str,
    resume_line: str | None = None,
    metrics: str | None = None,
    n: int = 1,
    use_openai: bool = False,
) -> list[StarBullet]:
    """Generate STAR bullets optionally using OpenAI."""

    if not requirement:
        return []

    if use_openai:
        user_prompt = (
            "Role: {role}\n"
            "Company: {company}\n"
            "Job requirement: {requirement}\n"
            "Current resume line (optional): {line}\n"
            "Known metrics (optional): {metrics}\n"
            "Constraints: \u226435 words, start with strong verb, include numbers if known, avoid jargon, no first person."
        ).format(role=role or "", company=company or "", requirement=requirement, line=resume_line or "", metrics=metrics or "")
        try:
            bullets = _call_openai(user_prompt)
            if bullets:
                return bullets[:n]
        except Exception as exc:  # pragma: no cover - network path
            logger.warning("OpenAI STAR generation failed: %s", exc)

    return [_fallback_bullet(role, requirement, resume_line) for _ in range(n)]
