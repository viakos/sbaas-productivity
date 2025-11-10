from __future__ import annotations

import os
from pathlib import Path

from src.config.config_loader import Config


def test_config_reads_app_section(config: Config) -> None:
    assert config.app_name == "SBAAS Productivity"
    assert config.app_version == "0.1.0"
    assert config.get("ui.theme") == "light"


def test_config_computes_database_url(tmp_path: Path, monkeypatch) -> None:
    base_dir = tmp_path
    (base_dir / "data").mkdir()
    (base_dir / ".env").write_text("APP_ENV=test\n", encoding="utf-8")
    (base_dir / "settings.yaml").write_text(
        "database:\n  path: data/local.db\napp:\n  name: Test App\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("DATABASE_URL", raising=False)

    cfg = Config(base_dir=base_dir)

    assert cfg.database_url.endswith("data/local.db")
