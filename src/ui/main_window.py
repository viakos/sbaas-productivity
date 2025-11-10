from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QMainWindow, QStatusBar, QToolBar

from src.config.config_loader import Config


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{self.config.app_name} v{self.config.app_version}")
        self.resize(800, 600)

        central_label = QLabel("Welcome to SBAAS Productivity", self)
        central_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_label.setObjectName("welcomeLabel")
        self.setCentralWidget(central_label)

        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        status_bar = QStatusBar(self)
        status_bar.showMessage(f"Theme: {self.config.ui_theme}")
        self.setStatusBar(status_bar)
