"""Follow-up scheduling heuristics."""
from __future__ import annotations

from datetime import timedelta

from .models import FollowUpPlan, FollowUpRequest, ReplyIntent

INTENT_WINDOWS = {
    ReplyIntent.POSITIVE: 1,
    ReplyIntent.NEUTRAL: 2,
    ReplyIntent.DEFERRAL: 30,
    ReplyIntent.REJECTION: 0,
}


def schedule_follow_up(request: FollowUpRequest) -> FollowUpPlan | None:
    """Return a follow-up plan based on the reply intent.

    A ``None`` return value indicates that no follow-up should be queued (for
    example, after an explicit rejection).
    """

    interaction = request.interaction
    base_window = request.default_window_days

    if request.intent is None:
        due = interaction.ts + timedelta(days=base_window)
        reason = f"No reply detected — retry in {base_window} days"
        return FollowUpPlan(interaction_id=interaction.id or 0, due_ts=due, reason=reason)

    window_days = INTENT_WINDOWS[request.intent]

    if request.intent is ReplyIntent.REJECTION:
        return None

    if request.intent is ReplyIntent.DEFERRAL:
        reason = "Contact asked to reconnect later"
    elif request.intent is ReplyIntent.POSITIVE:
        reason = "Send calendar slots and next steps"
    else:
        reason = "Provide additional information"

    due = interaction.ts + timedelta(days=window_days or base_window)
    return FollowUpPlan(interaction_id=interaction.id or 0, due_ts=due, reason=reason)
