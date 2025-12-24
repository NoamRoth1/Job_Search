import logging
import re
from functools import lru_cache
from typing import Iterable, List

import spacy
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_nlp_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        from spacy.cli import download

        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def extract_keywords(text: str, limit: int = 20) -> List[str]:
    nlp = get_nlp_model()
    doc = nlp(text)
    keywords = []
    for chunk in doc.noun_chunks:
        keyword = chunk.lemma_.lower().strip()
        keyword = re.sub(r"[^a-z0-9\s]", "", keyword)
        if keyword and keyword not in keywords:
            keywords.append(keyword)
        if len(keywords) >= limit:
            break
    if not keywords:
        keywords = list({token.lemma_.lower() for token in doc if token.is_alpha and not token.is_stop})[:limit]
    return keywords


def compute_similarity(resume_text: str, job_text: str) -> float:
    model = get_embedding_model()
    embeddings = model.encode([resume_text, job_text])
    score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(score)


def enhance_bullets(resume_text: str, keywords: Iterable[str]) -> str:
    action_verbs = [
        "spearheaded",
        "improved",
        "designed",
        "implemented",
        "optimized",
        "built",
        "led",
        "delivered",
        "automated",
        "orchestrated",
    ]
    keyword_iter = list(keywords)
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    enhanced = []
    for idx, line in enumerate(lines):
        bullet = line
        words = bullet.split()
        if words:
            first = words[0].rstrip(":")
            if first.lower() not in {v.lower() for v in action_verbs}:
                verb = action_verbs[idx % len(action_verbs)]
                bullet = f"{verb.capitalize()} {bullet[0].lower() + bullet[1:] if bullet else ''}"
        if keyword_iter:
            missing_keyword = keyword_iter[idx % len(keyword_iter)]
            if missing_keyword.lower() not in bullet.lower():
                bullet = f"{bullet}; highlighted {missing_keyword}"
        bullet = re.sub(r"\s+", " ", bullet).strip()
        enhanced.append(bullet)
    return "\n".join(enhanced)
