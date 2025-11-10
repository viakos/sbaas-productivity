from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse

from sqlalchemy import Boolean, DateTime, Integer, String, select
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.config.db import Base


DEFAULT_HOSTS_PATH = Path(r"C:\Windows\System32\drivers\etc\hosts")
HOSTS_MARKER = "# SBAAS_BLOCK"


class SiteBlockerError(RuntimeError):
    """Raised when the site blocking workflow fails."""


class BlockedSite(Base):
    """SQLAlchemy model storing blocked sites."""

    __tablename__ = "blocked_sites"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    redirect_ip: Mapped[str] = mapped_column(String(45), default="127.0.0.1", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


@dataclass(slots=True, frozen=True)
class HostEntry:
    hostname: str
    redirect_ip: str

    def render(self) -> str:
        return f"{self.redirect_ip}\t{self.hostname}\t{HOSTS_MARKER}"


class SiteBlocker:
    """Coordinates database state with the Windows hosts file."""

    def __init__(self, hosts_path: str | Path | None = None) -> None:
        self.hosts_path = Path(hosts_path) if hosts_path else DEFAULT_HOSTS_PATH

    def add_site(self, session: Session, url: str, redirect_ip: str = "127.0.0.1") -> BlockedSite:
        """Ensure a site is blocked both in the DB and hosts file."""
        hostname = self._normalize_url(url)
        stmt = select(BlockedSite).where(BlockedSite.url == hostname)
        site = session.scalars(stmt).first()

        if site:
            site.redirect_ip = redirect_ip
            site.is_active = True
        else:
            site = BlockedSite(url=hostname, redirect_ip=redirect_ip)
            session.add(site)

        session.flush()
        self.apply_blocklist(session)
        return site

    def remove_site(self, session: Session, url: str) -> bool:
        """Deactivate a blocked site and refresh hosts file. Returns True if modified."""
        hostname = self._normalize_url(url)
        stmt = select(BlockedSite).where(BlockedSite.url == hostname)
        site = session.scalars(stmt).first()

        if not site:
            return False

        site.is_active = False
        session.flush()
        self.apply_blocklist(session)
        return True

    def apply_blocklist(self, session: Session) -> None:
        """Rewrite hosts file to match active blocked sites."""
        stmt = (
            select(BlockedSite)
            .where(BlockedSite.is_active.is_(True))
            .order_by(BlockedSite.url)
        )
        active_sites = session.scalars(stmt).all()
        entries = [HostEntry(hostname=site.url, redirect_ip=site.redirect_ip) for site in active_sites]
        self._rewrite_hosts_file(entries)

    def _normalize_url(self, raw_url: str) -> str:
        candidate = raw_url.strip()
        if not candidate:
            raise SiteBlockerError("URL cannot be empty.")

        parsed = urlparse(candidate if "://" in candidate else f"http://{candidate}")
        hostname = parsed.netloc or parsed.path
        hostname = hostname.split("/")[0]
        hostname = hostname.split(":")[0].lower().lstrip(".")

        if not hostname:
            raise SiteBlockerError(f"Could not determine hostname from '{raw_url}'.")

        return hostname

    def _rewrite_hosts_file(self, entries: Iterable[HostEntry]) -> None:
        new_lines = [entry.render() for entry in entries]
        existing_lines = self._read_hosts_lines()
        filtered = [line for line in existing_lines if HOSTS_MARKER not in line]
        final_lines = filtered + new_lines
        text = "\n".join(final_lines)
        if final_lines:
            text += "\n"

        try:
            self.hosts_path.parent.mkdir(parents=True, exist_ok=True)
            self.hosts_path.write_text(text, encoding="utf-8")
        except OSError as exc:
            raise SiteBlockerError(f"Failed to write hosts file: {exc}") from exc

    def _read_hosts_lines(self) -> list[str]:
        if not self.hosts_path.exists():
            return []

        try:
            return self.hosts_path.read_text(encoding="utf-8").splitlines()
        except OSError as exc:
            raise SiteBlockerError(f"Failed to read hosts file: {exc}") from exc


__all__ = ["BlockedSite", "HostEntry", "SiteBlocker", "SiteBlockerError"]
