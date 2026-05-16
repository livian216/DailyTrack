from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from dailytrack.config import APP_NAME, APP_VERSION
from dailytrack.services.dashboard_service import DashboardService
from dailytrack.services.task_service import ServiceContainer, TaskService
from dailytrack.ui.daily_tasks_page import DailyTasksPage
from dailytrack.ui.dashboard_page import DashboardPage
from dailytrack.ui.daily_history_page import DailyHistoryPage
from dailytrack.ui.long_tasks_page import LongTasksPage
from dailytrack.ui.long_archive_page import LongArchivePage
from dailytrack.ui.review_page import ReviewPage
from dailytrack.ui.settings_page import SettingsPage
from dailytrack.ui.texts import APP_SUBTITLE, NAV_ITEMS, VERSION_LABEL
from dailytrack.ui.theme import SIZES


class FirstRunGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('首次使用向导')
        self.setMinimumWidth(520)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('欢迎使用 DailyTrack。'))
        layout.addWidget(QLabel('1. 左侧可切换：首页、今日待办、长线任务、每日复盘、设置/数据。'))
        layout.addWidget(QLabel('2. 数据默认保存在 %APPDATA%\\DailyTrack，可在设置中迁移。'))
        layout.addWidget(QLabel('3. 建议每天完成“今日待办 + 每日复盘”的闭环。'))
        ok = QPushButton('开始使用')
        ok.clicked.connect(self.accept)
        layout.addWidget(ok, alignment=Qt.AlignRight)


class MainWindow(QMainWindow):
    def __init__(self, container: ServiceContainer):
        super().__init__()
        self.container = container
        self.task_service = TaskService(self.container)
        self.dashboard_service = DashboardService(self.container)

        self.setWindowTitle(APP_NAME)
        icon_root = Path(__file__).parent / 'resources' / 'icons'
        mascot_icon_path = icon_root / 'mascot_beaver.svg'
        if mascot_icon_path.exists():
            self.setWindowIcon(QIcon(str(mascot_icon_path)))
        self.resize(SIZES['window_width'], SIZES['window_height'])
        self.setMinimumSize(SIZES['window_min_width'], SIZES['window_min_height'])

        central = QWidget()
        central_layout = QHBoxLayout(central)
        central_layout.setContentsMargins(14, 14, 14, 14)
        central_layout.setSpacing(14)
        self.setCentralWidget(central)

        nav_wrap = QFrame()
        nav_wrap.setProperty('card', True)
        nav_wrap.setFixedWidth(SIZES['nav_width'])
        nav_layout = QVBoxLayout(nav_wrap)
        nav_layout.setContentsMargins(14, 14, 14, 14)
        nav_layout.setSpacing(10)

        brand_row = QHBoxLayout()
        brand_row.setContentsMargins(0, 0, 0, 0)
        brand_row.setSpacing(8)

        mascot = QLabel()
        mascot.setFixedSize(32, 32)
        if mascot_icon_path.exists():
            mascot.setPixmap(QIcon(str(mascot_icon_path)).pixmap(32, 32))

        brand = QLabel(APP_NAME)
        brand.setStyleSheet('font-size:22px;font-weight:700;color:#1F2937;')
        sub = QLabel(APP_SUBTITLE)
        sub.setStyleSheet('font-size:12px;color:#6B7280;')

        brand_row.addWidget(mascot)
        brand_row.addWidget(brand)
        brand_row.addStretch()

        nav_layout.addLayout(brand_row)
        nav_layout.addWidget(sub)

        self.nav = QListWidget()
        self.nav.setObjectName('mainNav')
        self.nav.setFrameShape(QFrame.NoFrame)
        self.nav.setStyleSheet(
            'QListWidget{background:transparent;border:none;outline:0;}'
            'QListWidget::item{height:40px;padding:0 10px;border-radius:8px;color:#374151;}'
            'QListWidget::item:hover{background:#F1F5F9;}'
            'QListWidget::item:selected{background:#EAF1FF;color:#2563EB;font-weight:700;border-left:3px solid #2563EB;}'
            'QListWidget::item:focus{outline:none;border:none;}'
        )

        self.nav.setIconSize(QSize(18, 18))
        for name, icon_name in NAV_ITEMS:
            item = QListWidgetItem(name, self.nav)
            icon_path = icon_root / f'{icon_name}.svg'
            if icon_path.exists():
                item.setIcon(QIcon(str(icon_path)))

        nav_layout.addWidget(self.nav)
        nav_layout.addStretch()

        version = QLabel(f'{VERSION_LABEL} {APP_VERSION}')
        version.setStyleSheet('font-size:12px;color:#9CA3AF;')
        nav_layout.addWidget(version)

        self.stack = QStackedWidget()
        self.stack.setProperty('card', True)

        self.daily_page = DailyTasksPage(self.task_service)
        self.long_page = LongTasksPage(self.task_service)
        self.daily_history_page = DailyHistoryPage(self.task_service)
        self.long_archive_page = LongArchivePage(self.task_service)
        self.review_page = ReviewPage(self.task_service)
        self.settings_page = SettingsPage(self._container_provider)
        self.dashboard_page = DashboardPage(
            self.dashboard_service,
            open_daily_task=self.open_daily_task_from_dashboard,
            open_long_task=self.open_long_task_from_dashboard,
        )

        for page in [
            self.dashboard_page,
            self.daily_page,
            self.long_page,
            self.daily_history_page,
            self.long_archive_page,
            self.review_page,
            self.settings_page,
        ]:
            self.stack.addWidget(page)

        central_layout.addWidget(nav_wrap)
        central_layout.addWidget(self.stack, 1)

        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.stack.currentChanged.connect(self._refresh_current_page)
        self.nav.setCurrentRow(0)
        self._show_first_run_guide_once()
        self._refresh_current_page(0)

    def open_daily_task_from_dashboard(self, task_id: int) -> None:
        self.daily_page.refresh()
        self.nav.setCurrentRow(1)
        self.daily_page.focus_task(task_id)

    def open_long_task_from_dashboard(self, task_id: int) -> None:
        self.long_page.refresh()
        self.nav.setCurrentRow(2)
        self.long_page.focus_task(task_id)

    def _container_provider(self, reload_from=None):
        if reload_from is not None:
            self.container = ServiceContainer.build(reload_from)
            self.task_service = TaskService(self.container)
            self.dashboard_service = DashboardService(self.container)
            self.dashboard_page.dashboard_service = self.dashboard_service
            self.daily_page.task_service = self.task_service
            self.long_page.task_service = self.task_service
            self.daily_history_page.task_service = self.task_service
            self.long_archive_page.task_service = self.task_service
            self.review_page.task_service = self.task_service
            return self.container
        return self.container

    def _show_first_run_guide_once(self) -> None:
        with self.container.db.connect() as conn:
            row = conn.execute("SELECT value FROM app_meta WHERE key='first_run_guide_shown'").fetchone()
            shown = row['value'] if row else None
            if shown == '1':
                return
        FirstRunGuideDialog(self).exec()
        with self.container.db.connect() as conn:
            conn.execute(
                "INSERT INTO app_meta(key, value) VALUES ('first_run_guide_shown', '1') "
                "ON CONFLICT(key) DO UPDATE SET value='1'"
            )
            conn.commit()

    def _refresh_current_page(self, index: int) -> None:
        page = self.stack.widget(index)
        if hasattr(page, 'refresh'):
            try:
                page.refresh()
            except Exception:
                # Keep navigation responsive even if one page refresh fails.
                pass
