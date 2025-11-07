"""Keyword extraction utilities."""
from __future__ import annotations

import logging
import re
from collections import Counter
from typing import Iterable

from .embeddings import EmbeddingClient
from .similarity import cosine_similarity

logger = logging.getLogger(__name__)


def _load_spacy_model():
    import spacy

    for name in ("en_core_web_trf", "en_core_web_sm"):
        try:
            return spacy.load(name)  # type: ignore[arg-type]
        except Exception:  # pragma: no cover - optional dependency
            continue
    logger.warning("Falling back to blank spaCy model")
    return spacy.blank("en")


_SPACY = None


def _get_nlp():
    global _SPACY
    if _SPACY is None:
        _SPACY = _load_spacy_model()
    return _SPACY


def _normalize_keyword(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9+ ]", "", text)
    return text.strip()


def extract_candidates(text: str) -> list[str]:
    """Extract noun phrase candidates using spaCy."""

    nlp = _get_nlp()
    doc = nlp(text)
    if doc.is_space:
        return []
    candidates = [chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 2]
    if not candidates:
        tokens = [token.text for token in doc if token.is_alpha and not token.is_stop]
        candidates = [" ".join(tokens[i : i + 2]).strip() for i in range(0, len(tokens), 2) if tokens[i : i + 2]]
    return candidates


def score_keywords(
    text: str,
    top_k: int = 25,
    seed_keywords: Iterable[str] | None = None,
    embedding_client: EmbeddingClient | None = None,
) -> list[str]:
    """Return ranked keywords from the provided text."""

    candidates = extract_candidates(text)
    counts = Counter(_normalize_keyword(c) for c in candidates if _normalize_keyword(c))
    if seed_keywords:
        for kw in seed_keywords:
            counts[_normalize_keyword(kw)] += 3

    phrases = list(counts)
    if not phrases:
        return []

    scores = [float(counts[p]) for p in phrases]

    if embedding_client is not None:
        doc_embedding = embedding_client.embed_text(text)
        phrase_embeddings = embedding_client.embed_texts(phrases)
        for idx, emb in enumerate(phrase_embeddings):
            scores[idx] += cosine_similarity(doc_embedding, emb)

    ranked = [phrase for phrase, _ in sorted(zip(phrases, scores), key=lambda item: item[1], reverse=True)]
    return ranked[:top_k]
