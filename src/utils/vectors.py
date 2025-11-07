"""Lightweight vector math utilities."""
from __future__ import annotations

import math
from typing import Sequence

Vector = list[float]
Matrix = list[Vector]


def zeros(rows: int, cols: int) -> Matrix:
    return [[0.0 for _ in range(cols)] for _ in range(rows)]


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def norm(vec: Sequence[float]) -> float:
    return math.sqrt(sum(x * x for x in vec))


def cosine(a: Sequence[float], b: Sequence[float]) -> float:
    denom = norm(a) * norm(b)
    if denom == 0:
        return 0.0
    return dot(a, b) / denom


def pairwise_cosine(vectors_a: Matrix, vectors_b: Matrix) -> Matrix:
    if not vectors_a or not vectors_b:
        return zeros(len(vectors_a), len(vectors_b))
    return [[cosine(a, b) for b in vectors_b] for a in vectors_a]


def argmax(values: Sequence[float]) -> int:
    best_idx = 0
    best_val = float("-inf")
    for idx, value in enumerate(values):
        if value > best_val:
            best_idx = idx
            best_val = value
    return best_idx
