"""Lightweight reply classification heuristics."""
from __future__ import annotations

from .models import ReplyAnalysis, ReplyIntent

KEYWORDS = {
    ReplyIntent.POSITIVE: ("let's", "schedule", "book", "great to", "sounds good"),
    ReplyIntent.NEUTRAL: ("tell me more", "details", "information", "clarify"),
    ReplyIntent.DEFERRAL: ("next quarter", "later", "circle back", "not now", "follow up"),
    ReplyIntent.REJECTION: ("not interested", "no thanks", "remove me", "unsubscribe"),
}

DEFAULT_ACTIONS = {
    ReplyIntent.POSITIVE: "Send calendar link and two time slots",
    ReplyIntent.NEUTRAL: "Reply with concise 3-bullet summary",
    ReplyIntent.DEFERRAL: "Schedule reminder with note",
    ReplyIntent.REJECTION: "Mark as do-not-contact",
}


def classify_reply(text: str) -> ReplyAnalysis:
    """Classify an inbound email body into one of the supported intents."""

    lower = text.lower()
    scores: dict[ReplyIntent, int] = {intent: 0 for intent in ReplyIntent}

    for intent, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword in lower:
                scores[intent] += 1

    best_intent = max(scores.items(), key=lambda kv: kv[1])[0]
    confidence = min(1.0, scores[best_intent] / 3.0) if scores[best_intent] else 0.25

    notes: list[str] = []
    if scores[ReplyIntent.DEFERRAL]:
        notes.append("Reminder to capture requested timing in CRM")
    if "forward" in lower:
        notes.append("May be a referral request")

    return ReplyAnalysis(
        intent=best_intent,
        confidence=round(confidence, 2),
        suggested_action=DEFAULT_ACTIONS[best_intent],
        notes=notes,
    )
