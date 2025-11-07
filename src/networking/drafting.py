"""Prompt builders and template driven draft generation."""
from __future__ import annotations

from dataclasses import dataclass
from textwrap import dedent
from typing import List, Sequence

from .models import Contact, DraftRequest, EmailDraft, VoiceProfile

PROFILE_PRIMER_TEMPLATE = (
    "You are an assistant that writes concise, warm, and professional "
    "networking emails for {name} ({role}). Keep 90–130 words, one clear ask, "
    "minimal fluff, a specific value proposition, and a CTA with two time options."
)

CONTACT_CONTEXT_TEMPLATE = (
    "Contact: {contact_name}, {contact_role}. Notes: {notes}. Goal: {goal}. Tone: {tone}. "
    "Include: {include}. Avoid: {avoid}."
)

CRITIQUE_TEMPLATE = dedent(
    """Check: personalization (≥2 specifics), clarity (1 ask), length (≤130 words),\n"""
    """jargon (low), next step (2 slots). Return improved draft."""
)


@dataclass(slots=True)
class DraftVariant:
    """Metadata describing each preconfigured variant."""

    key: str
    purpose: str
    tone: str
    template: str


VARIANTS: Sequence[DraftVariant] = (
    DraftVariant(
        key="warm_intro",
        purpose="Warm intro via mutual",
        tone="warm",
        template=dedent(
            """Subject: Quick intro via {mutual_name}\n"
            "Hi {first_name} — {mutual_name} thought we should connect given your work at {company} on {specific_area}.\n"
            "I’m {author_name} ({author_role}). I’ve been working on {highlight}, and I’d value your perspective on {goal}.\n"
            "Would a quick 15 minutes {option1} or {option2} work? If not, I can send a 3-bullet summary by email.\n"
            "{signature}\n{author_name}"""
        ),
    ),
    DraftVariant(
        key="cold_intro",
        purpose="Cold outreach with value",
        tone="concise",
        template=dedent(
            """Subject: Idea for {company_possessive}\n"
            "Hi {first_name}, noticed {recent_event}. I built a lightweight prototype that {outcome} and could be adapted for {company}.\n"
            "If helpful, I can share a 2-minute Loom or a repo snippet. Open to a brief chat {option1} / {option2}.\n"
            "Best,\n{author_name}"""
        ),
    ),
    DraftVariant(
        key="reconnect",
        purpose="Reconnect",
        tone="upbeat",
        template=dedent(
            """Subject: Quick catch-up?\n"
            "Hi {first_name}, it’s been a while since {context}. I’m exploring roles focused on {goal_focus} and thought of your team’s {relevant_work}.\n"
            "Could we do 15 minutes {option1} or {option2}? If easier, I’ll email a concise update and a couple of specific questions.\n"
            "Thanks,\n{author_name}"""
        ),
    ),
)


class PromptBuilder:
    """Utility to assemble few-shot prompts for LLM drafting."""

    def __init__(self, voice_profile: VoiceProfile) -> None:
        self.voice_profile = voice_profile

    def build_profile_primer(self) -> str:
        return PROFILE_PRIMER_TEMPLATE.format(
            name=self.voice_profile.name, role=self.voice_profile.role
        )

    def build_contact_context(self, request: DraftRequest) -> str:
        notes = request.shared_context or request.contact.notes or "No additional notes"
        include = request.highlight or request.include_link or "Specific project or link"
        avoid = request.avoid_topics or "None"
        return CONTACT_CONTEXT_TEMPLATE.format(
            contact_name=request.contact.name,
            contact_role=request.contact.company_role or "their role",
            notes=notes,
            goal=request.goal,
            tone=request.tone,
            include=include,
            avoid=avoid,
        )

    def build_critique_prompt(self) -> str:
        return CRITIQUE_TEMPLATE

    def assemble(self, request: DraftRequest) -> list[str]:
        return [
            self.build_profile_primer(),
            self.build_contact_context(request),
            self.build_critique_prompt(),
        ]


def _pick_specific_area(contact: Contact, request: DraftRequest) -> str:
    candidates = [
        request.highlight,
        request.shared_context,
        contact.notes,
        contact.company_role,
        contact.company,
    ]
    for candidate in candidates:
        if candidate:
            return candidate
    return "a recent project"


def _first_name(name: str) -> str:
    return name.split()[0]


def _ensure_two_options(options: Sequence[str]) -> tuple[str, str]:
    opts = list(options)
    if len(opts) >= 2:
        return opts[0], opts[1]
    if len(opts) == 1:
        return opts[0], "next week"
    return "Tuesday at 10am", "Thursday at 2pm"


def _company_possessive(company: str | None) -> str:
    if not company:
        return "your team"
    suffix = "'" if company.endswith("s") else "'s"
    return f"{company}{suffix} initiatives"


def _render_variant(
    variant: DraftVariant, request: DraftRequest, voice_profile: VoiceProfile
) -> EmailDraft:
    contact = request.contact
    option1, option2 = _ensure_two_options(request.time_options)
    mutual_name = request.shared_context or "a mutual connection"
    recent_event = request.highlight or contact.notes or "your recent work"
    outcome = "delivered measurable lift for a recent client"
    if request.highlight:
        outcome = request.highlight
    specific_area = _pick_specific_area(contact, request)
    context = request.shared_context or contact.notes or "our last conversation"
    relevant_work = contact.notes or "recent launch"

    body = variant.template.format(
        mutual_name=mutual_name,
        first_name=_first_name(contact.name),
        company=contact.company or "your team",
        company_possessive=_company_possessive(contact.company),
        specific_area=specific_area,
        author_name=voice_profile.name,
        author_role=voice_profile.role,
        highlight=request.highlight or "a new product sprint",
        goal=request.goal,
        option1=option1,
        option2=option2,
        signature=voice_profile.signature,
        recent_event=recent_event,
        outcome=outcome,
        context=context,
        goal_focus=request.goal,
        relevant_work=relevant_work,
    )

    return EmailDraft(
        subject=body.splitlines()[0].replace("Subject: ", "", 1),
        body="\n".join(body.splitlines()[1:]).strip(),
        purpose=variant.purpose,
        tone=variant.tone,
        variant=variant.key,
    )


def generate_variants(request: DraftRequest) -> List[EmailDraft]:
    """Produce up to three outreach drafts using lightweight templating."""

    voice_profile = request.voice_profile
    drafts: list[EmailDraft] = []
    for variant in VARIANTS[: request.variant_count]:
        drafts.append(_render_variant(variant, request, voice_profile))
    return drafts


def build_prompt_bundle(request: DraftRequest) -> List[str]:
    """Return the recommended prompt stack for LLM-based drafting."""

    builder = PromptBuilder(request.voice_profile)
    return builder.assemble(request)
