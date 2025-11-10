from __future__ import annotations

from statistics import mean
from typing import Iterable, Sequence


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Return division result while guarding against zero denominators."""
    if denominator == 0:
        return default
    return numerator / denominator


def rolling_average(values: Iterable[float]) -> float:
    """Return the average of the provided iterable or 0.0 when empty."""
    sequence = list(values)
    if not sequence:
        return 0.0
    return mean(sequence)


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value to the provided [min, max] range."""
    return max(min(value, maximum), minimum)


def ensure_sequence(values: Iterable[float]) -> Sequence[float]:
    """Materialize an iterable into an immutable tuple for repeated reuse."""
    return tuple(values)


__all__ = ["safe_divide", "rolling_average", "clamp", "ensure_sequence"]
