"""FastAPI router exposing the networking copilot endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from .drafting import build_prompt_bundle, generate_variants
from .followups import schedule_follow_up
from .importers import CSVImportError, parse_contacts_csv
from .models import (
    Contact,
    DraftRequest,
    DraftResponse,
    FollowUpPlan,
    FollowUpRequest,
    ReplyAnalysis,
)
from .replies import classify_reply
from .scoring import rank_contacts

router = APIRouter(prefix="/networking", tags=["networking"])


@router.post("/contacts/import", response_model=list[Contact])
async def import_contacts(csv_text: str) -> list[Contact]:
    """Parse a CSV payload into contacts and annotate with scores."""

    try:
        contacts = parse_contacts_csv(csv_text)
    except CSVImportError as exc:  # pragma: no cover - FastAPI transport
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    ranked = rank_contacts(contacts)
    return ranked


@router.post("/drafts", response_model=DraftResponse)
async def create_drafts(payload: DraftRequest) -> DraftResponse:
    """Generate outreach variants and suggest a follow-up window."""

    drafts = generate_variants(payload)
    prompts = build_prompt_bundle(payload)

    _ = prompts  # placeholder for future LLM integration

    return DraftResponse(
        drafts=drafts,
        follow_up_suggestion_days=payload.follow_up_window_days,
    )


@router.post("/followups", response_model=FollowUpPlan | None)
async def create_follow_up(payload: FollowUpRequest) -> FollowUpPlan | None:
    """Create a follow-up schedule based on reply signal."""

    return schedule_follow_up(payload)


@router.post("/replies/classify", response_model=ReplyAnalysis)
async def classify(payload: dict[str, str]) -> ReplyAnalysis:
    """Classify a reply body and return suggested action."""

    body = payload.get("body")
    if not body:
        raise HTTPException(status_code=400, detail="Missing reply body")
    return classify_reply(body)
