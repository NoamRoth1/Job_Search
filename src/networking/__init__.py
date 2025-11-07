"""Networking copilot package providing outreach tooling."""

from . import drafting, followups, replies, scoring
from .models import (
    Contact,
    DraftRequest,
    DraftResponse,
    EmailDraft,
    FollowUpPlan,
    FollowUpRequest,
    ReplyAnalysis,
    ReplyIntent,
    VoiceProfile,
)

__all__ = [
    "Contact",
    "DraftRequest",
    "DraftResponse",
    "EmailDraft",
    "FollowUpPlan",
    "FollowUpRequest",
    "ReplyAnalysis",
    "ReplyIntent",
    "VoiceProfile",
    "drafting",
    "followups",
    "replies",
    "scoring",
]

try:  # pragma: no cover - optional dependency guard
    from . import router as router  # type: ignore
except Exception:  # pragma: no cover - exposed for FastAPI users only
    router = None
else:  # pragma: no cover - executed when FastAPI is available
    __all__.append("router")
