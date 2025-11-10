from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from src.features.site_blocker import BlockedSite, HOSTS_MARKER, SiteBlocker


def _prepare_hosts(tmp_path: Path) -> Path:
    hosts_path = tmp_path / "hosts"
    hosts_path.write_text("127.0.0.1 localhost\n", encoding="utf-8")
    return hosts_path


def test_add_site_updates_db_and_hosts(db_session, tmp_path) -> None:
    hosts_path = _prepare_hosts(tmp_path)
    blocker = SiteBlocker(hosts_path=hosts_path)

    blocker.add_site(db_session, "https://Example.com")

    persisted = db_session.scalars(
        select(BlockedSite).where(BlockedSite.url == "example.com")
    ).first()
    assert persisted is not None
    assert persisted.is_active

    hosts_text = hosts_path.read_text(encoding="utf-8")
    assert "example.com" in hosts_text
    assert HOSTS_MARKER in hosts_text


def test_remove_site_cleans_hosts_entry(db_session, tmp_path) -> None:
    hosts_path = _prepare_hosts(tmp_path)
    blocker = SiteBlocker(hosts_path=hosts_path)

    blocker.add_site(db_session, "blocked.test")
    assert blocker.remove_site(db_session, "blocked.test") is True

    hosts_text = hosts_path.read_text(encoding="utf-8")
    assert "blocked.test" not in hosts_text
    # Non-managed lines remain untouched.
    assert "localhost" in hosts_text
