"""Pydantic models used by the resume optimization engine."""
from __future__ import annotations

from typing import Literal

try:  # pragma: no cover - optional dependency path
    from pydantic import BaseModel, Field
except ModuleNotFoundError:  # pragma: no cover - fallback path
    import json
    from dataclasses import asdict, dataclass, field

    class BaseModel:  # type: ignore[override]
        def model_dump(self) -> dict:
            return asdict(self)

        def model_dump_json(self, indent: int | None = None) -> str:
            return json.dumps(self.model_dump(), indent=indent)

    def Field(*, default=None, default_factory=None):  # type: ignore[misc]
        if default_factory is not None:
            return field(default_factory=default_factory)
        return field(default=default)

    @dataclass
    class KeywordMatch(BaseModel):
        keyword: str
        category: Literal["present", "weak", "missing"]
        evidence_lines: list[str] = Field(default_factory=list)
        similarity: float | None = None
        suggestion: str | None = None

    @dataclass
    class AtsBreakdown(BaseModel):
        total: float
        hard_skills: float
        soft_skills: float
        seniority: float
        domain: float
        breadth: float
        formatting: float
        top_actions: list[str]

    @dataclass
    class StarBullet(BaseModel):
        bullet: str
        rationale: str

    @dataclass
    class AnalysisReport(BaseModel):
        role: str | None
        company: str | None
        extracted_job_keywords: list[str]
        keyword_matches: list[KeywordMatch]
        ats: AtsBreakdown
        skills_patch: list[str]
        edited_bullets: list[str]
        star_bullets: list[StarBullet] = Field(default_factory=list)
else:

    class KeywordMatch(BaseModel):
        """Information about how a keyword relates to the resume."""

        keyword: str
        category: Literal["present", "weak", "missing"]
        evidence_lines: list[str] = Field(default_factory=list)
        similarity: float | None = None
        suggestion: str | None = None

    class AtsBreakdown(BaseModel):
        """ATS scoring information with a breakdown of contributing factors."""

        total: float
        hard_skills: float
        soft_skills: float
        seniority: float
        domain: float
        breadth: float
        formatting: float
        top_actions: list[str]

    class StarBullet(BaseModel):
        """Representation of a STAR formatted bullet point."""

        bullet: str
        rationale: str

    class AnalysisReport(BaseModel):
        """Full analysis payload returned by the engine."""

        role: str | None
        company: str | None
        extracted_job_keywords: list[str]
        keyword_matches: list[KeywordMatch]
        ats: AtsBreakdown
        skills_patch: list[str]
        edited_bullets: list[str]
        star_bullets: list[StarBullet] = Field(default_factory=list)
