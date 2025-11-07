"""End-to-end orchestration for the resume optimization engine."""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterable

from .analysis.gap_analysis import analyze_keywords, summarize_skills_patch
from .analysis.match_scoring import score_resume
from .analysis.star import generate_star_bullets
from .ingest.job_reader import read_job
from .ingest.resume_reader import read_resume
from .io_models import AnalysisReport
from .nlp.embeddings import EmbeddingClient
from .nlp.keywords import score_keywords
from .suggestions.rewriter import suggest_rewrites

logger = logging.getLogger(__name__)


class Pipeline:
    """Coordinates all stages of the analysis."""

    def __init__(self, *, use_openai: bool = False) -> None:
        self.embedding_client = EmbeddingClient()
        self.use_openai = use_openai

    def analyze(self, resume_path: str | Path, job_input: str, *, include_star: bool = False) -> AnalysisReport:
        resume = read_resume(resume_path)
        job = read_job(job_input)

        keywords = score_keywords(job.text, embedding_client=self.embedding_client, top_k=20)
        keyword_matches = analyze_keywords(resume, keywords, self.embedding_client)
        ats = score_resume(resume, job, keyword_matches)
        skills_patch = summarize_skills_patch(keyword_matches)
        edited_bullets = suggest_rewrites(keyword_matches, resume.bullets)

        star_bullets = []
        if include_star:
            missing = [match for match in keyword_matches if match.category != "present"]
            for match in missing[:3]:
                requirement = next(iter(job.sections.values()), job.text.split("\n")[0] if job.text else match.keyword)
                star_bullets.extend(
                    generate_star_bullets(
                        role=job.role,
                        company=job.company,
                        requirement=requirement,
                        resume_line=resume.bullets[0] if resume.bullets else None,
                        metrics=None,
                        n=1,
                        use_openai=self.use_openai,
                    )
                )

        return AnalysisReport(
            role=job.role,
            company=job.company,
            extracted_job_keywords=keywords,
            keyword_matches=keyword_matches,
            ats=ats,
            skills_patch=skills_patch,
            edited_bullets=edited_bullets,
            star_bullets=star_bullets,
        )
