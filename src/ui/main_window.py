from __future__ import annotations

from datetime import datetime, timezone

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from src.config.config_loader import Config
from src.config.db import get_session
from src.features.focus_timer import FocusTimerService
from src.features.site_blocker import BlockedSite, SiteBlocker, SiteBlockerError


class MainWindow(QMainWindow):
    """Primary application window."""

    def __init__(
        self,
        config: Config,
        site_blocker: SiteBlocker,
        warning_message: str | None = None,
    ) -> None:
        super().__init__()
        self.config = config
        self.site_blocker = site_blocker
        self.warning_message = warning_message
        self.domain_input: QLineEdit | None = None
        self.block_list_widget: QListWidget | None = None
        self.status_label: QLabel | None = None
        self.focus_service = FocusTimerService()
        self.focus_minutes_input: QLineEdit | None = None
        self.focus_elapsed_label: QLabel | None = None
        self.focus_message_label: QLabel | None = None
        self.focus_start_button: QPushButton | None = None
        self.focus_stop_button: QPushButton | None = None
        self.focus_timer = QTimer(self)
        self.focus_timer.setInterval(1000)
        self.focus_timer.timeout.connect(self._handle_focus_tick)
        self.focus_target_minutes: int = 0
        self.focus_target_seconds: int = 0
        self.focus_remaining_seconds: int = 0
        self.focus_running = False
        self.focus_started_at: datetime | None = None

        self._build_ui()
        self.refresh_block_list()

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{self.config.app_name} v{self.config.app_version}")
        self.resize(900, 650)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(24, 24, 24, 24)
        root_layout.setSpacing(16)

        tab_widget = QTabWidget(self)
        tab_widget.setObjectName("mainTabs")
        tab_widget.addTab(self._build_site_blocking_tab(), "Site Blocking")
        tab_widget.addTab(self._build_focus_timer_tab(), "Focus Timer")
        root_layout.addWidget(tab_widget)

        self.setCentralWidget(central_widget)

        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        status_bar = QStatusBar(self)
        status_bar.showMessage(f"Theme: {self.config.ui_theme}")
        self.setStatusBar(status_bar)

    def _build_site_blocking_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        if self.warning_message:
            warning_label = QLabel(self.warning_message, self)
            warning_label.setWordWrap(True)
            warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warning_label.setObjectName("warningLabel")
            warning_label.setStyleSheet("color: #b3261e; font-weight: bold;")
            layout.addWidget(warning_label)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)

        self.domain_input = QLineEdit(self)
        self.domain_input.setPlaceholderText("Enter domain to block (e.g., example.com)")
        controls_layout.addWidget(self.domain_input, stretch=2)

        add_button = QPushButton("Add", self)
        add_button.clicked.connect(self.handle_add_domain)
        controls_layout.addWidget(add_button)

        remove_button = QPushButton("Remove Selected", self)
        remove_button.clicked.connect(self.handle_remove_selected)
        controls_layout.addWidget(remove_button)

        layout.addLayout(controls_layout)

        self.block_list_widget = QListWidget(self)
        self.block_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.block_list_widget.setObjectName("blockedSitesList")
        layout.addWidget(self.block_list_widget, stretch=1)

        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        layout.addWidget(self.status_label)

        return tab

    def _build_focus_timer_tab(self) -> QWidget:
        tab = QWidget(self)
        layout = QVBoxLayout(tab)
        layout.setSpacing(12)
        layout.setContentsMargins(16, 16, 16, 16)

        instructions = QLabel("Set your deep focus target (minutes)", self)
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instructions)

        self.focus_minutes_input = QLineEdit(self)
        self.focus_minutes_input.setPlaceholderText("Minutes (e.g., 25)")
        self.focus_minutes_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_minutes_input.setValidator(QIntValidator(1, 600, self))
        font = self.focus_minutes_input.font()
        font.setPointSize(28)
        self.focus_minutes_input.setFont(font)
        layout.addWidget(self.focus_minutes_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.focus_start_button = QPushButton("Start", self)
        self.focus_start_button.clicked.connect(self.handle_start_focus)
        buttons_layout.addWidget(self.focus_start_button)

        self.focus_stop_button = QPushButton("Stop", self)
        self.focus_stop_button.setEnabled(False)
        self.focus_stop_button.clicked.connect(self.handle_stop_focus)
        buttons_layout.addWidget(self.focus_stop_button)

        layout.addLayout(buttons_layout)

        self.focus_elapsed_label = QLabel("Remaining: 00:00", self)
        self.focus_elapsed_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_elapsed_label.setObjectName("focusElapsedLabel")
        layout.addWidget(self.focus_elapsed_label)

        self.focus_message_label = QLabel("", self)
        self.focus_message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.focus_message_label.setObjectName("focusMessageLabel")
        layout.addWidget(self.focus_message_label)

        return tab

    def refresh_block_list(self) -> None:
        if self.block_list_widget is None:
            return

        self.block_list_widget.clear()
        try:
            with get_session() as session:
                stmt = (
                    select(BlockedSite)
                    .where(BlockedSite.is_active.is_(True))
                    .order_by(BlockedSite.url)
                )
                sites = [
                    (site.url, site.redirect_ip)
                    for site in session.scalars(stmt).all()
                ]
        except Exception as exc:  # pragma: no cover - fallback UI path
            self._set_status(f"Failed to load blocked sites: {exc}", error=True)
            return

        for url, redirect_ip in sites:
            label = f"{url} -> {redirect_ip}"
            item = QListWidgetItem(label)
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.block_list_widget.addItem(item)

        if not sites:
            self._set_status("No blocked sites configured.", error=False)

    def handle_add_domain(self) -> None:
        if not self.domain_input:
            return
        domain = self.domain_input.text().strip()
        if not domain:
            self._set_status("Enter a domain before adding.", error=True)
            return

        try:
            blocked_url: str | None = None
            with get_session() as session:
                site = self.site_blocker.add_site(session, domain)
                blocked_url = site.url
        except SiteBlockerError as exc:
            self._set_status(str(exc), error=True)
            return

        self.domain_input.clear()
        self._set_status(f"Blocked {blocked_url}", error=False)
        self.refresh_block_list()

    def handle_remove_selected(self) -> None:
        if not self.block_list_widget:
            return

        items = self.block_list_widget.selectedItems()
        if not items:
            self._set_status("Select at least one domain to remove.", error=True)
            return

        domains = [item.data(Qt.ItemDataRole.UserRole) for item in items if item.data(Qt.ItemDataRole.UserRole)]
        removed: list[str] = []
        try:
            with get_session() as session:
                for domain in domains:
                    if domain and self.site_blocker.remove_site(session, domain):
                        removed.append(domain)
        except SiteBlockerError as exc:
            self._set_status(str(exc), error=True)
            return

        if removed:
            self._set_status(f"Removed {', '.join(removed)}", error=False)
        else:
            self._set_status("No domains were removed.", error=True)
        self.refresh_block_list()

    def _set_status(self, message: str, error: bool) -> None:
        if not self.status_label:
            return
        color = "#b3261e" if error else "#1b5e20"
        self.status_label.setStyleSheet(f"color: {color};")
        self.status_label.setText(message)

    def handle_start_focus(self) -> None:
        if self.focus_minutes_input is None or self.focus_start_button is None or self.focus_stop_button is None:
            return
        if self.focus_running:
            return

        raw_value = self.focus_minutes_input.text().strip()
        if not raw_value:
            self._set_focus_status("Enter the focus duration in minutes.", error=True)
            return

        try:
            minutes = int(raw_value)
        except ValueError:
            self._set_focus_status("Focus duration must be a whole number.", error=True)
            return

        if minutes <= 0:
            self._set_focus_status("Focus duration must be greater than zero.", error=True)
            return

        self.focus_target_minutes = minutes
        self.focus_target_seconds = minutes * 60
        self.focus_remaining_seconds = self.focus_target_seconds
        self.focus_running = True
        self.focus_started_at = datetime.now(timezone.utc)
        self.focus_timer.start()
        self._set_focus_controls(running=True)
        self._update_focus_elapsed_label()
        self._set_focus_status("Focus session started. Stay on task!", error=False)

    def handle_stop_focus(self) -> None:
        if not self.focus_running:
            self._set_focus_status("No focus session is running.", error=True)
            return

        self.focus_timer.stop()
        self.focus_running = False
        self.focus_target_minutes = 0
        self.focus_target_seconds = 0
        self.focus_remaining_seconds = 0
        self.focus_started_at = None
        self._set_focus_controls(running=False)
        self._update_focus_elapsed_label()
        self._set_focus_status("Focus session stopped early.", error=True)

    def _handle_focus_tick(self) -> None:
        if not self.focus_running:
            return

        if self.focus_remaining_seconds > 0:
            self.focus_remaining_seconds -= 1
            self._update_focus_elapsed_label()

        if self.focus_remaining_seconds <= 0:
            self.focus_timer.stop()
            self.focus_running = False
            self._finalize_focus_session()

    def _finalize_focus_session(self) -> None:
        minutes = max(self.focus_target_minutes, 1)
        seconds = max(self.focus_target_seconds, 60)
        self.focus_target_minutes = 0
        self.focus_target_seconds = 0
        self.focus_remaining_seconds = 0
        started_at = self.focus_started_at or datetime.now(timezone.utc)
        completed_at = datetime.now(timezone.utc)
        self.focus_started_at = None
        self._set_focus_controls(running=False)
        self._update_focus_elapsed_label()

        try:
            with get_session() as session:
                self.focus_service.record_session(
                    session,
                    target_minutes=minutes,
                    actual_seconds=seconds,
                    started_at=started_at,
                    completed_at=completed_at,
                )
        except Exception as exc:  # pragma: no cover - UI feedback only
            self._set_focus_status(f"Focus completed but failed to save: {exc}", error=True)
            return

        self._set_focus_status("Focus session completed!", error=False)
        QMessageBox.information(
            self,
            "Focus Complete",
            "Great job! You completed your focus session.",
        )

    def _update_focus_elapsed_label(self) -> None:
        if not self.focus_elapsed_label:
            return
        minutes, seconds = divmod(max(self.focus_remaining_seconds, 0), 60)
        self.focus_elapsed_label.setText(f"Remaining: {minutes:02d}:{seconds:02d}")

    def _set_focus_controls(self, running: bool) -> None:
        if self.focus_start_button:
            self.focus_start_button.setEnabled(not running)
        if self.focus_stop_button:
            self.focus_stop_button.setEnabled(running)
        if self.focus_minutes_input:
            self.focus_minutes_input.setEnabled(not running)

    def _set_focus_status(self, message: str, error: bool) -> None:
        if not self.focus_message_label:
            return
        color = "#b3261e" if error else "#1b5e20"
        self.focus_message_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        self.focus_message_label.setText(message)
