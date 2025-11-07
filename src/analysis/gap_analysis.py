"""Gap analysis between resume and job keywords."""
from __future__ import annotations

from typing import Iterable

from ..ingest.resume_reader import ResumeDocument
from ..io_models import KeywordMatch
from ..nlp.embeddings import EmbeddingClient
from ..nlp.similarity import pairwise_similarity
from ..utils.vectors import argmax

PRESENT_THRESHOLD = 0.75
WEAK_THRESHOLD = 0.6


def analyze_keywords(
    resume: ResumeDocument,
    keywords: Iterable[str],
    embedding_client: EmbeddingClient,
) -> list[KeywordMatch]:
    """Return keyword matches with similarity evidence."""

    keywords = [kw for kw in keywords if kw]
    if not keywords:
        return []

    bullet_embeddings = embedding_client.embed_texts(resume.bullets or [resume.text])
    keyword_embeddings = embedding_client.embed_texts(keywords)
    similarity_matrix = pairwise_similarity(keyword_embeddings, bullet_embeddings)

    matches: list[KeywordMatch] = []
    for idx, keyword in enumerate(keywords):
        sims = similarity_matrix[idx] if idx < len(similarity_matrix) else []
        best_idx = argmax(sims) if sims else 0
        best_sim = float(sims[best_idx]) if sims else 0.0
        evidence = [resume.bullets[best_idx]] if resume.bullets and best_idx < len(resume.bullets) else []
        if keyword.lower() in resume.text.lower():
            best_sim = max(best_sim, 0.9)
        if best_sim >= PRESENT_THRESHOLD:
            category = "present"
            suggestion = None
        elif best_sim >= WEAK_THRESHOLD:
            category = "weak"
            suggestion = f"If applicable, rephrase as: emphasize {keyword} with concrete metrics."
        else:
            category = "missing"
            suggestion = f"Add only if accurate: highlight experience with {keyword}."
        matches.append(
            KeywordMatch(
                keyword=keyword,
                category=category,
                evidence_lines=evidence,
                similarity=round(best_sim, 3),
                suggestion=suggestion,
            )
        )
    return matches


def summarize_skills_patch(matches: Iterable[KeywordMatch]) -> list[str]:
    """Return suggested skills entries based on missing keywords."""

    suggestions = []
    for match in matches:
        if match.category != "present":
            suggestions.append(f"{match.keyword.title()} (if applicable)")
    return suggestions
