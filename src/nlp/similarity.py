"""Cosine similarity utilities."""
from __future__ import annotations

from typing import Sequence

from ..utils.vectors import cosine as _cosine
from ..utils.vectors import pairwise_cosine


def cosine_similarity(a: Sequence[float], b: Sequence[float]) -> float:
    return _cosine(a, b)


def pairwise_similarity(matrix_a: list[list[float]], matrix_b: list[list[float]]) -> list[list[float]]:
    return pairwise_cosine(matrix_a, matrix_b)
