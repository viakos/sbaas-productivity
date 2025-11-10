from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
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

        self._build_ui()
        self.refresh_block_list()

    def _build_ui(self) -> None:
        self.setWindowTitle(f"{self.config.app_name} v{self.config.app_version}")
        self.resize(900, 650)

        central_widget = QWidget(self)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(32, 32, 32, 32)
        root_layout.setSpacing(16)

        tab_widget = QTabWidget(self)
        tab_widget.setObjectName("mainTabs")

        # Overview tab
        overview_tab = QWidget(self)
        overview_layout = QVBoxLayout(overview_tab)
        overview_layout.setSpacing(12)

        central_label = QLabel("Welcome to SBAAS Productivity", self)
        central_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        central_label.setObjectName("welcomeLabel")
        overview_layout.addWidget(central_label)

        if self.warning_message:
            warning_label = QLabel(self.warning_message, self)
            warning_label.setWordWrap(True)
            warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            warning_label.setObjectName("warningLabel")
            warning_label.setStyleSheet("color: #b3261e; font-weight: bold;")
            overview_layout.addWidget(warning_label)

        tab_widget.addTab(overview_tab, "Overview")

        # Site blocking tab
        site_tab = QWidget(self)
        site_layout = QVBoxLayout(site_tab)
        site_layout.setSpacing(12)

        if self.warning_message:
            site_warning = QLabel(self.warning_message, self)
            site_warning.setWordWrap(True)
            site_warning.setAlignment(Qt.AlignmentFlag.AlignCenter)
            site_warning.setObjectName("siteWarningLabel")
            site_warning.setStyleSheet("color: #b3261e; font-weight: bold;")
            site_layout.addWidget(site_warning)

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

        site_layout.addLayout(controls_layout)

        self.block_list_widget = QListWidget(self)
        self.block_list_widget.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.block_list_widget.setObjectName("blockedSitesList")
        site_layout.addWidget(self.block_list_widget, stretch=1)

        self.status_label = QLabel("", self)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setObjectName("statusLabel")
        site_layout.addWidget(self.status_label)

        tab_widget.addTab(site_tab, "Site Blocking")

        root_layout.addWidget(tab_widget)
        self.setCentralWidget(central_widget)

        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        status_bar = QStatusBar(self)
        status_bar.showMessage(f"Theme: {self.config.ui_theme}")
        self.setStatusBar(status_bar)

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
