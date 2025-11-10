from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pytest

from src.config.config_loader import Config
from src.config.db import SessionLocal, init_db


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def config(project_root: Path) -> Config:
    return Config(base_dir=project_root)


@pytest.fixture(scope="session", autouse=True)
def _initialize_db(config: Config) -> None:
    init_db()


@pytest.fixture()
def db_session() -> Iterator:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()
