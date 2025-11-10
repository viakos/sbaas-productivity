# SBAAS Productivity

Local productivity desktop application built with Python 3.10, PySide6, and SQLite via SQLAlchemy 2.x. The project includes a centralized configuration system, a basic GUI shell, and starter tests to grow upon.

## Requirements
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) for dependency management

## Quick Start
1. Install dependencies: `uv sync`
2. Copy `.env.example` to `.env` and adjust values as needed.
3. Launch the app: `uv run python main.py`
4. Run tests: `uv run pytest`

## Project Layout
- `src/config/` – configuration loader + database session helpers.
- `src/features/` – domain-specific logic modules.
- `src/ui/` – PySide6 widgets and Designer forms.
- `src/utils/` – shared helper utilities.
- `docs/` – technical and functional specifications.
- `tests/` – pytest suite with fixtures in `conftest.py`.

## Development Notes
- Formatting is enforced with `black`.
- Type hints are required throughout the codebase; run `uv run mypy` as needed.
- Keep documentation in `docs/` updated when features evolve.
