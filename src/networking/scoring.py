"""Contact scoring utilities."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from .models import Contact


@dataclass(slots=True)
class ScoreWeights:
    """Weight configuration for the contact scoring formula."""

    relationship_strength: float = 3.0
    overlap_skills: float = 2.0
    mutuals_count: float = 2.0
    recent_activity: float = 1.0
    cold_penalty: float = 1.0


DEFAULT_WEIGHTS = ScoreWeights()


def calculate_score(contact: Contact, weights: ScoreWeights = DEFAULT_WEIGHTS) -> float:
    """Compute the contact score using the rule-based formula.

    The calculation intentionally mirrors the formula outlined in the
    product brief to keep the behaviour interpretable.
    """

    base = 0.0
    base += weights.relationship_strength * float(contact.relationship_strength)
    base += weights.overlap_skills * float(contact.overlap_skills)
    base += weights.mutuals_count * float(contact.mutuals_count)
    base += weights.recent_activity * float(contact.recent_activity)

    if contact.cold_days_since_last_touch > 120:
        base -= weights.cold_penalty

    return base


def rank_contacts(contacts: Iterable[Contact], weights: ScoreWeights = DEFAULT_WEIGHTS) -> List[Contact]:
    """Return contacts ordered by score (descending).

    Each contact receives a ``score`` attribute so downstream components can
    render the value without re-computation.
    """

    scored: list[Contact] = []
    for contact in contacts:
        contact.score = calculate_score(contact, weights)
        scored.append(contact)

    scored.sort(key=lambda c: c.score or 0.0, reverse=True)
    return scored
