# SBAAS Productivity – Technical Specification

## Overview
SBAAS Productivity is a local desktop application built with Python 3.10, PySide6 for the GUI, and SQLite via SQLAlchemy 2.x. Configuration is centralized through a `Config` class that merges `.env` and `settings.yaml`. The application is packaged and managed with `uv` using the `pyproject.toml`.

## Architecture
- **Entry point (`main.py`)** initializes configuration, database metadata, and launches the PySide6 event loop with the main window defined in `src/ui/main_window.py`.
- **Configuration (`src/config/config_loader.py`)** loads `.env` values with `python-dotenv` and YAML settings with `pyyaml`. It exposes helpers for app metadata and database connectivity details.
- **Database (`src/config/db.py`)** defines the SQLAlchemy Declarative Base, engine, and session factory. `init_db()` auto-creates tables when the app starts.
- **Features (`src/features/`)** contain focused business logic modules. `site_blocker.py` manages hosts modifications while `focus_timer.py` defines the `FocusSession` ORM model plus persistence helpers for completed deep-focus sessions.
- **UI Layer (`src/ui/main_window.py`)** uses a tabbed interface surfaced through Qt widgets: the Site Blocking tab controls the Windows hosts file, and the Focus Timer tab orchestrates a countdown interface tied to the persistence service.
- **UI Layer (`src/ui/`)** contains widgets and Qt Designer forms. `main_window.py` wires configuration data into the top-level window.
- **Utilities (`src/utils/helpers.py`)** host reusable math helpers with deterministic outputs suitable for unit testing.

## Dependencies
Runtime dependencies are PySide6, SQLAlchemy 2.x, python-dotenv, and PyYAML. Development tooling adds pytest, pytest-cov, black, mypy, and pylint for linting and tests. All dependencies are declared in `pyproject.toml`.

## Testing Strategy
Pytest is used for validating configuration loading, helper utilities, and feature logic. Shared fixtures live in `tests/conftest.py` and provide ready-to-use configuration objects and database sessions. Future database models should add corresponding tests ensuring migrations and ORM behavior remain stable.

## Future Work
- Introduce Alembic migrations once persistent models are added.
- Expand `src/features/` with additional productivity insights and expose the site-blocking workflow via the GUI (activation toggles, schedule, etc.).
- Add integration tests that cover the Config + DB stack together.
