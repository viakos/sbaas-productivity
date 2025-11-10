from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from src.config.config_loader import Config
from src.config.db import init_db
from src.ui.main_window import MainWindow


def main() -> None:
    config = Config()
    init_db()

    app = QApplication(sys.argv)
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
