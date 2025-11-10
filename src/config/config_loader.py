from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Mapping

import yaml
from dotenv import load_dotenv


class ConfigError(RuntimeError):
    """Raised when required configuration files are missing or malformed."""


class Config:
    """Centralized configuration loader for .env and settings.yaml values."""

    def __init__(
        self,
        base_dir: Path | None = None,
        settings_path: Path | None = None,
    ) -> None:
        self.base_dir = base_dir or Path(__file__).resolve().parents[2]
        self.settings_path = settings_path or self.base_dir / "settings.yaml"

        load_dotenv(dotenv_path=self.base_dir / ".env", override=False)
        self._settings = self._load_settings()

    def _load_settings(self) -> dict[str, Any]:
        if not self.settings_path.exists():
            raise ConfigError(f"Missing settings file: {self.settings_path}")

        with self.settings_path.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}

        if not isinstance(data, Mapping):
            raise ConfigError("settings.yaml must define a mapping at the root level")

        return dict(data)

    def get(self, dotted_path: str, default: Any = None) -> Any:
        """Return a nested config value using dotted-path notation."""
        current: Any = self._settings
        for segment in dotted_path.split("."):
            if isinstance(current, Mapping) and segment in current:
                current = current[segment]
            else:
                return default
        return current

    @property
    def app_name(self) -> str:
        return str(self.get("app.name", "SBAAS Productivity"))

    @property
    def app_version(self) -> str:
        return str(self.get("app.version", "0.1.0"))

    @property
    def ui_theme(self) -> str:
        return str(self.get("ui.theme", "light"))

    @property
    def database_url(self) -> str:
        env_url = os.getenv("DATABASE_URL")
        if env_url:
            return env_url

        db_path = Path(self.get("database.path", "data/sbaas.db"))
        if not db_path.is_absolute():
            db_path = self.base_dir / db_path
        return f"sqlite:///{db_path.as_posix()}"


__all__ = ["Config", "ConfigError"]
