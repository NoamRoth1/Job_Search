"""ATS style scoring heuristics."""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from typing import Iterable

from ..ingest.resume_reader import ResumeDocument
from ..ingest.job_reader import JobPosting
from ..io_models import AtsBreakdown, KeywordMatch

logger = logging.getLogger(__name__)


@dataclass
class ScoringWeights:
    hard_skills: float = 45.0
    soft_skills: float = 15.0
    seniority: float = 10.0
    domain: float = 10.0
    breadth: float = 10.0
    formatting: float = 10.0


SOFT_SKILLS = {"communication", "leadership", "collaboration", "mentoring", "stakeholder"}
SENIORITY_TERMS = {"senior", "lead", "principal", "manager"}
FORMAT_REGEXES = {
    "dates": re.compile(r"\b20\d{2}|19\d{2}"),
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+"),
    "phone": re.compile(r"\+?\d[\d \-]{7,}"),
    "bullets": re.compile(r"^(?:[-*\u2022]|\d+\.)\s+", re.MULTILINE),
}


def _fraction(count: float, total: float) -> float:
    return 0.0 if total <= 0 else min(1.0, count / total)


def _score_soft_skills(resume: ResumeDocument) -> float:
    text = resume.text.lower()
    hits = sum(1 for skill in SOFT_SKILLS if skill in text)
    return _fraction(hits, len(SOFT_SKILLS))


def _score_seniority(resume: ResumeDocument, job: JobPosting) -> float:
    resume_text = resume.text.lower()
    job_text = job.text.lower()
    resume_hits = any(term in resume_text for term in SENIORITY_TERMS)
    job_hint = any(term in job_text for term in SENIORITY_TERMS)
    if not job_hint:
        return 1.0
    return 1.0 if resume_hits else 0.3


def _score_domain(resume: ResumeDocument, job: JobPosting) -> float:
    resume_tokens = set(resume.text.lower().split())
    job_tokens = set(job.text.lower().split())
    overlap = len(resume_tokens & job_tokens)
    return _fraction(overlap, len(job_tokens) or 1)


def _score_formatting(resume: ResumeDocument) -> float:
    text = resume.text
    matches = sum(1 for regex in FORMAT_REGEXES.values() if regex.search(text))
    return _fraction(matches, len(FORMAT_REGEXES))


def _score_hard_skills(keyword_matches: Iterable[KeywordMatch]) -> float:
    matches = list(keyword_matches)
    present = sum(1 for match in matches if match.category == "present")
    return _fraction(present, len(matches) or 1)


def _score_breadth(keyword_matches: Iterable[KeywordMatch]) -> float:
    categories = {match.category for match in keyword_matches}
    if not categories:
        return 0.0
    return 1.0 if "missing" not in categories else 0.5 if "weak" not in categories else 0.3


def score_resume(
    resume: ResumeDocument,
    job: JobPosting,
    keyword_matches: list[KeywordMatch],
    weights: ScoringWeights | None = None,
) -> AtsBreakdown:
    """Compute the ATS score breakdown."""

    weights = weights or ScoringWeights()
    hard = _score_hard_skills(keyword_matches)
    soft = _score_soft_skills(resume)
    seniority = _score_seniority(resume, job)
    domain = _score_domain(resume, job)
    breadth = _score_breadth(keyword_matches)
    formatting = _score_formatting(resume)

    total = (
        hard * weights.hard_skills
        + soft * weights.soft_skills
        + seniority * weights.seniority
        + domain * weights.domain
        + breadth * weights.breadth
        + formatting * weights.formatting
    ) / 100.0 * 100

    top_actions: list[str] = []
    if hard < 1.0:
        top_actions.append("Add strong evidence for missing hard skills")
    if soft < 1.0:
        top_actions.append("Mention collaboration or leadership outcomes")
    if formatting < 1.0:
        top_actions.append("Ensure contact info, dates, and bullets are present")

    return AtsBreakdown(
        total=round(total, 1),
        hard_skills=round(hard * weights.hard_skills, 1),
        soft_skills=round(soft * weights.soft_skills, 1),
        seniority=round(seniority * weights.seniority, 1),
        domain=round(domain * weights.domain, 1),
        breadth=round(breadth * weights.breadth, 1),
        formatting=round(formatting * weights.formatting, 1),
        top_actions=top_actions[:5],
    )
