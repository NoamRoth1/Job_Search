from datetime import datetime

from src.networking.followups import schedule_follow_up
from src.networking.models import FollowUpRequest, Interaction, ReplyIntent


def _interaction(ts: datetime | None = None) -> Interaction:
    return Interaction(
        id=7,
        contact_id=3,
        ts=ts or datetime(2024, 1, 1, 12, 0, 0),
        direction="outbound",
        subject="Hello",
        body="Body",
        status="sent",
    )


def test_follow_up_none_for_rejection():
    request = FollowUpRequest(interaction=_interaction(), intent=ReplyIntent.REJECTION)
    assert schedule_follow_up(request) is None


def test_follow_up_default_window():
    request = FollowUpRequest(interaction=_interaction())
    plan = schedule_follow_up(request)
    assert plan is not None
    assert plan.due_ts.day == 7  # default 6 day window from Jan 1
    assert "No reply" in plan.reason


def test_follow_up_positive_fast_tracks():
    request = FollowUpRequest(
        interaction=_interaction(),
        intent=ReplyIntent.POSITIVE,
        default_window_days=6,
    )
    plan = schedule_follow_up(request)
    assert plan is not None
    assert plan.due_ts.day == 2  # 1 day later
    assert "calendar" in plan.reason.lower()
