# 🤖 AGENTS.md — OpenAI Codex Development Guide

## 1. Project Overview
Local desktop app built with **Python 3.10**, **PySide6 GUI**, and **SQLite + SQLAlchemy ORM**.

Configuration is split between:
- **.env** → sensitive data (loaded via `python-dotenv`)
- **settings.yaml** → general settings (loaded via `pyyaml`)

Dependencies managed via **uv** and **pyproject.toml**. Testing with **pytest**. Code formatting enforced via **black**.

---

## 2. Folder Structure
```
project_root/
│
├── pyproject.toml
├── .env
├── .env.example
├── settings.yaml
├── .gitignore
├── main.py
│
├── src/
│   ├── config/
│   │   ├── __init__.py
│   │   ├── db.py               # SQLAlchemy 2.x, SessionLocal + get_session()
│   │   └── config_loader.py    # Config class handling .env + YAML
│   │
│   ├── features/
│   │   ├── __init__.py
│   │   └── example_feature.py
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── forms/              # Qt Designer .ui files
│   │   └── main_window.py
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   └── helpers.py
│
├── docs/
│   ├── TECHNICAL_SPEC.md
│   └── FUNCTIONAL_SPEC.md
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_example_feature.py
│
└── README.md
```

---

## 3. Database Configuration
- Use **SQLAlchemy 2.x Declarative Syntax** with typing annotations:
  ```python
  from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

  class Base(DeclarativeBase):
      pass
  ```

- Implement reusable **SessionLocal** and `get_session()` context manager in `config/db.py`.
- DB auto-initializes if not exists.
- Optional: add Alembic placeholder for migrations if schema grows.

---

## 4. Configuration Handling
- Centralized `Config` class in `config_loader.py`:
  - Loads `.env` with `python-dotenv`
  - Loads `settings.yaml` with `pyyaml`
  - Provides unified access via attributes
- Add `.env.example` for public structure (non-sensitive values).

---

## 5. Development Setup
- Manage dependencies with `uv` + `pyproject.toml`
- Include **dev-dependencies**:
  - `pytest`
  - `black`
  - `mypy`
  - `pytest-cov`
  - `pylint` (optional)

Run commands:
```bash
uv sync
pytest
black .
```

---

## 6. Testing
- Use **pytest** for critical functions (no UI testing).
- Add reusable fixtures in `tests/conftest.py` for config & DB sessions.
- Optional coverage reporting with `pytest --cov`.

---

## 7. Coding & Architecture Rules
1. Strict **PEP8 + Black** formatting.
2. Full **type hints** everywhere.
3. Each feature is **self-contained** in its own file under `src/features/`.
4. Never hardcode sensitive data.
5. Maintain clear **separation of concerns**.
6. **Prefer composition** over inheritance.
7. Keep `docs/TECHNICAL_SPEC.md` and `docs/FUNCTIONAL_SPEC.md` and README.md updated.

---

## 8. Definition of Done
Each feature is considered done when:
- Code follows PEP8 and passes Black
- All related tests pass
- Technical and Functional specs updated
- Main branch merges cleanly and app runs end-to-end

---

## 9. Version Control Policy
- Always create a new branch for each feature or fix:
  ```bash
  git checkout -b feature/<feature_name>
  ```
- Use clear, imperative commit messages:
  ```
  Fix: prevent crash when missing config file
  Add: task manager UI
  Refactor: move auth logic to auth.py
  ```
- Never commit temporary or debug files (`__pycache__`, `.env`, `.venv`, etc.)
- Before every commit:
  ```bash
  uv sync && pytest
  ```
- Keep **main branch stable**.
- After merge:
  ```bash
  git checkout main
  ```
- Update documentation under `docs/` after each feature.

---

## 10. .gitignore
```
__pycache__/
.venv/
.env
*.pyc
*.pyo
pytest_cache/
.DS_Store
migrations/
.idea/
.vscode/
```

---

## 11. Optional Future Additions
- Add Alembic migrations when schema grows.
- Add `Makefile` or PowerShell `tasks.ps1` for shortcuts.
- Add pre-commit hook for auto Black + pytest.

---

**End of AGENTS.md**