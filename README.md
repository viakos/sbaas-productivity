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
- `src/config/` - configuration loader + database session helpers.
- `src/features/` - domain-specific logic modules (e.g., `site_blocker.py`).
- `src/ui/` - PySide6 widgets and Designer forms.
- `src/utils/` - shared helper utilities.
- `docs/` - technical and functional specifications.
- `tests/` - pytest suite with fixtures in `conftest.py`.

## Development Notes
- Formatting is enforced with `black`.
- Type hints are required throughout the codebase; run `uv run mypy` as needed.
- Keep documentation in `docs/` updated when features evolve.

## Site Blocking Feature
- Blocked domains live in the `blocked_sites` table and are managed through `SiteBlocker`.
- Active entries are written to the Windows hosts file using lines tagged with `# SBAAS_BLOCK`.
- Launch the application with administrative privileges so it can write to `C:\Windows\System32\drivers\etc\hosts`. If elevated permissions are missing, the GUI surfaces a warning and site blocking remains disabled until access is granted.
- The main window exposes a Site Blocking panel where you can enter a domain, click **Add**, and manage the list via multi-select removal.

## Focus Timer Feature
- Switch to the **Focus Timer** tab to set a deep-focus goal in minutes using the large input field.
- Start begins a live countdown (displayed beneath the controls); Stop pauses early without recording progress.
- When the timer naturally reaches zero, the app congratulates the user and persists the completed session (target minutes + total seconds) to the SQLite database via `FocusTimerService`.
