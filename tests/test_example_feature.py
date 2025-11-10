from __future__ import annotations

from src.features.example_feature import ProductivitySummary, summarize_productivity


def test_summarize_productivity_handles_zero_total() -> None:
    summary = summarize_productivity(completed_tasks=5, planned_tasks=0)
    assert isinstance(summary, ProductivitySummary)
    assert summary.completion_rate == 0.0
    assert summary.remaining_tasks == 0


def test_summarize_productivity_caps_completion_rate() -> None:
    summary = summarize_productivity(completed_tasks=15, planned_tasks=10)
    assert summary.completion_rate == 100.0
    assert summary.remaining_tasks == 0
