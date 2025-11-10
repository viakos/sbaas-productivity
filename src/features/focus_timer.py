from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.config.db import Base


class FocusSession(Base):
    """SQLAlchemy model capturing completed deep-focus sessions."""

    __tablename__ = "focus_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_seconds: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


@dataclass(slots=True, frozen=True)
class FocusSessionData:
    target_minutes: int
    actual_seconds: int


class FocusTimerService:
    """Handles persistence of completed focus sessions."""

    def record_session(
        self,
        session: Session,
        target_minutes: int,
        actual_seconds: int,
        *,
        started_at: datetime | None = None,
        completed_at: datetime | None = None,
    ) -> FocusSession:
        if target_minutes <= 0:
            raise ValueError("target_minutes must be greater than zero.")
        if actual_seconds <= 0:
            raise ValueError("actual_seconds must be greater than zero.")

        started = started_at or datetime.now(timezone.utc)
        completed = completed_at or datetime.now(timezone.utc)

        record = FocusSession(
            target_minutes=target_minutes,
            actual_seconds=actual_seconds,
            started_at=started,
            completed_at=completed,
        )
        session.add(record)
        session.flush()
        return record


__all__ = ["FocusSession", "FocusTimerService", "FocusSessionData"]
