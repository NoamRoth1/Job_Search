"""Embedding helpers for the resume optimization engine."""
from __future__ import annotations

import hashlib
import logging
import os
from dataclasses import dataclass
from typing import Sequence

from ..utils.vectors import Vector

logger = logging.getLogger(__name__)


@dataclass
class EmbeddingConfig:
    model_name: str = os.getenv("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
    use_openai: bool = False


class EmbeddingClient:
    """Wrapper around sentence-transformers with lightweight fallbacks."""

    def __init__(self, config: EmbeddingConfig | None = None) -> None:
        self.config = config or EmbeddingConfig()
        self._model = None
        self._maybe_load_model()

    def _maybe_load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            self._model = SentenceTransformer(self.config.model_name)
            logger.info("Loaded sentence transformer model %s", self.config.model_name)
        except Exception as exc:  # pragma: no cover - optional dependency path
            logger.warning("Falling back to hashed embeddings: %s", exc)
            self._model = None

    def _simple_embed(self, text: str) -> Vector:
        tokens = text.lower().split()
        vec = [0.0] * 64
        if not tokens:
            return vec
        for token in tokens:
            digest = hashlib.sha1(token.encode("utf-8")).hexdigest()
            idx = int(digest[:8], 16) % len(vec)
            vec[idx] += 1.0
        length = sum(x * x for x in vec) ** 0.5 or 1.0
        return [x / length for x in vec]

    def embed_texts(self, texts: Sequence[str]) -> list[Vector]:
        if not texts:
            return []

        if self.config.use_openai:
            try:
                import openai

                client = openai.OpenAI()  # type: ignore[attr-defined]
                response = client.embeddings.create(
                    model="text-embedding-3-large",
                    input=list(texts),
                )
                return [list(item.embedding) for item in response.data]
            except Exception as exc:  # pragma: no cover - network path
                logger.warning("OpenAI embedding failed, falling back to local model: %s", exc)

        if self._model is not None:
            try:
                embeddings = self._model.encode(list(texts), batch_size=16, show_progress_bar=False)
                return [list(map(float, vector)) for vector in embeddings]
            except Exception as exc:  # pragma: no cover - encode failure
                logger.warning("Sentence transformer encoding failed: %s", exc)

        return [self._simple_embed(text) for text in texts]

    def embed_text(self, text: str) -> Vector:
        vectors = self.embed_texts([text])
        return vectors[0] if vectors else [0.0] * 64


def hash_text(text: str) -> str:
    """Return a deterministic short hash for caching purposes."""

    return hashlib.sha1(text.encode("utf-8")).hexdigest()
