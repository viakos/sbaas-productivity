from __future__ import annotations

from dataclasses import dataclass

from src.utils.helpers import clamp, safe_divide


@dataclass(slots=True, frozen=True)
class ProductivitySummary:
    completion_rate: float
    remaining_tasks: int


def summarize_productivity(completed_tasks: int, planned_tasks: int) -> ProductivitySummary:
    """Return a simple summary of team productivity for the dashboard."""
    completed = max(completed_tasks, 0)
    planned = max(planned_tasks, 0)

    if planned == 0:
        completion_rate = 0.0
    else:
        completion_rate = clamp(
            safe_divide(completed, planned, default=0.0) * 100.0,
            0.0,
            100.0,
        )
    remaining = max(planned - completed, 0)
    return ProductivitySummary(completion_rate=round(completion_rate, 2), remaining_tasks=remaining)


__all__ = ["ProductivitySummary", "summarize_productivity"]
