from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from src.config.config_loader import Config
from src.config.db import get_session, init_db
from src.features.site_blocker import SiteBlocker, SiteBlockerError
from src.ui.main_window import MainWindow


def main() -> None:
    config = Config()
    init_db()

    site_blocker = SiteBlocker()
    warning_message: str | None = None
    try:
        with get_session() as session:
            site_blocker.apply_blocklist(session)
    except SiteBlockerError as exc:
        warning_message = "We couldn't set up site blocking because Windows needs administrator access. Please restart SBAAS Productivity with “Run as administrator” to enable blocking."

    app = QApplication(sys.argv)
    window = MainWindow(config, site_blocker=site_blocker, warning_message=warning_message)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
