from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config_loader import Config


class Base(DeclarativeBase):
    """Base declarative class for all ORM models."""


def _create_engine(config: Config) -> tuple[str, sessionmaker[Session]]:
    database_url = config.database_url
    engine = create_engine(
        database_url,
        echo=bool(config.get("database.echo", False)),
        future=True,
    )
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    return engine, factory


_CONFIG = Config()
ENGINE, SessionLocal = _create_engine(_CONFIG)


def init_db() -> None:
    """Create database tables if they do not exist."""
    Base.metadata.create_all(bind=ENGINE)


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


__all__ = ["Base", "ENGINE", "SessionLocal", "get_session", "init_db"]
