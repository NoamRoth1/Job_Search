"""Pydantic data models for the networking copilot."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, computed_field, field_validator


class ReplyIntent(str, Enum):
    """Intent buckets for inbound replies."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    DEFERRAL = "deferral"
    REJECTION = "rejection"


class Contact(BaseModel):
    """Representation of a potential outreach target."""

    id: Optional[int] = None
    name: str
    email: str
    company: str | None = None
    role: str | None = None
    relationship: str | None = None
    notes: str | None = None
    relationship_strength: int = Field(0, ge=0, le=5)
    overlap_skills: int = Field(0, ge=0, le=5)
    mutuals_count: int = Field(0, ge=0)
    recent_activity: int = Field(0, ge=0, le=5)
    cold_days_since_last_touch: int = Field(0, ge=0)
    score: float | None = None

    @field_validator("email")
    @classmethod
    def _validate_email(cls, value: str) -> str:
        if "@" not in value:
            raise ValueError("Email must contain '@'")
        return value

    @computed_field
    @property
    def company_role(self) -> str:
        """Format company + role for easy personalization."""

        bits: list[str] = []
        if self.role:
            bits.append(self.role)
        if self.company:
            bits.append(f"at {self.company}")
        return " ".join(bits)


class Interaction(BaseModel):
    """An email exchange with a contact."""

    id: Optional[int] = None
    contact_id: int
    ts: datetime
    direction: str  # outbound / inbound
    subject: str
    body: str
    status: str


class Template(BaseModel):
    """Store reusable outreach templates."""

    id: Optional[int] = None
    purpose: str
    tone: str
    body: str
    variables_json: dict[str, str] | None = None


class EmailDraft(BaseModel):
    """Concrete draft ready to review or send."""

    subject: str
    body: str
    purpose: str
    tone: str
    variant: str


class VoiceProfile(BaseModel):
    """Author preferences that shape generation prompts."""

    name: str
    role: str
    tone: str = "warm"
    signature: str = "Best,"  # appended before name
    word_limit: int = Field(130, ge=60, le=180)


class DraftRequest(BaseModel):
    """API payload for generating outreach drafts."""

    contact: Contact
    goal: str
    shared_context: str | None = None
    highlight: str | None = None
    avoid_topics: str | None = None
    include_link: str | None = None
    variant_count: int = Field(3, ge=1, le=3)
    follow_up_window_days: int = Field(6, ge=3, le=10)
    time_options: List[str] = Field(default_factory=lambda: ["Tuesday 10am PT", "Thursday 2pm PT"])
    tone: str = "warm"
    voice_profile: VoiceProfile


class DraftResponse(BaseModel):
    """API response containing generated drafts."""

    drafts: list[EmailDraft]
    follow_up_suggestion_days: int


class FollowUpRequest(BaseModel):
    """Request body for scheduling follow ups."""

    interaction: Interaction
    intent: ReplyIntent | None = None
    default_window_days: int = Field(6, ge=1, le=30)


class FollowUpPlan(BaseModel):
    """Scheduled follow-up metadata."""

    interaction_id: int
    due_ts: datetime
    reason: str
    status: str = "scheduled"


class ReplyAnalysis(BaseModel):
    """Classification output for reply parsing."""

    intent: ReplyIntent
    confidence: float = Field(ge=0, le=1)
    suggested_action: str
    notes: list[str] = Field(default_factory=list)
