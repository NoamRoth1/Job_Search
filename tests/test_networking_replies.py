from src.networking.replies import classify_reply
from src.networking.models import ReplyIntent


def test_positive_reply_detection():
    reply = "Let's schedule a time next week. Sounds good to me!"
    analysis = classify_reply(reply)
    assert analysis.intent is ReplyIntent.POSITIVE
    assert analysis.suggested_action.startswith("Send calendar")


def test_deferral_notes_added():
    reply = "Can we circle back next quarter? Also forward to my colleague."
    analysis = classify_reply(reply)
    assert analysis.intent is ReplyIntent.DEFERRAL
    assert any("referral" in note.lower() for note in analysis.notes)
