from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from src.features.focus_timer import FocusSession, FocusTimerService


def test_record_session_persists_entry(db_session) -> None:
    service = FocusTimerService()
    started = datetime.now(timezone.utc)
    completed = started + timedelta(minutes=25)
    record = service.record_session(
        db_session,
        target_minutes=25,
        actual_seconds=1500,
        started_at=started,
        completed_at=completed,
    )
    assert record.id is not None

    stored = db_session.scalars(
        select(FocusSession).where(FocusSession.id == record.id)
    ).one()
    assert stored is not None
    assert stored.target_minutes == 25
    assert stored.actual_seconds == 1500
    assert stored.started_at == started
    assert stored.completed_at == completed
