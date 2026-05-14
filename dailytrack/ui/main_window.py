from __future__ import annotations

from PySide6.QtWidgets import (
    QDialog,
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

from dailytrack.config import APP_NAME
from dailytrack.services.dashboard_service import DashboardService
from dailytrack.services.task_service import ServiceContainer, TaskService
from dailytrack.ui.daily_tasks_page import DailyTasksPage
from dailytrack.ui.dashboard_page import DashboardPage
from dailytrack.ui.long_tasks_page import LongTasksPage
from dailytrack.ui.review_page import ReviewPage
from dailytrack.ui.settings_page import SettingsPage


class FirstRunGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("首次使用向导")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("欢迎使用 DailyTrack。"))
        layout.addWidget(QLabel("1. 左侧可切换：首页、今日待办、长线任务、每日复盘、设置/数据。"))
        layout.addWidget(QLabel("2. 数据默认保存在 %APPDATA%\\DailyTrack，可在设置/数据页修改。"))
        layout.addWidget(QLabel("3. 建议每天完成 今日待办 + 每日复盘。"))
        ok = QPushButton("开始使用")
        ok.clicked.connect(self.accept)
        layout.addWidget(ok)


class MainWindow(QMainWindow):
    def __init__(self, container: ServiceContainer):
        super().__init__()
        self.container = container
        self.task_service = TaskService(self.container)
        self.dashboard_service = DashboardService(self.container)
        self.setWindowTitle(APP_NAME)
        self.resize(1360, 860)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)

        self.nav = QListWidget()
        for name in ["首页", "今日待办", "长线任务", "每日复盘", "设置/数据"]:
            QListWidgetItem(name, self.nav)

        self.stack = QStackedWidget()
        self.daily_page = DailyTasksPage(self.task_service)
        self.long_page = LongTasksPage(self.task_service)
        self.review_page = ReviewPage(self.task_service)
        self.settings_page = SettingsPage(self._container_provider)
        self.dashboard_page = DashboardPage(
            self.dashboard_service,
            open_daily_task=self.open_daily_task_from_dashboard,
            open_long_task=self.open_long_task_from_dashboard,
        )
        for p in [self.dashboard_page, self.daily_page, self.long_page, self.review_page, self.settings_page]:
            self.stack.addWidget(p)

        root.addWidget(self.nav, 1)
        root.addWidget(self.stack, 5)
        self.nav.currentRowChanged.connect(self.stack.setCurrentIndex)
        self.nav.setCurrentRow(0)
        self._show_first_run_guide_once()

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
            self.review_page.task_service = self.task_service
            return self.container
        return self.container

    def _show_first_run_guide_once(self) -> None:
        with self.container.db.connect() as conn:
            row = conn.execute("SELECT value FROM app_meta WHERE key='first_run_guide_shown'").fetchone()
            shown = row["value"] if row else None
            if shown == "1":
                return
        dlg = FirstRunGuideDialog(self)
        dlg.exec()
        with self.container.db.connect() as conn:
            conn.execute(
                "INSERT INTO app_meta(key, value) VALUES ('first_run_guide_shown', '1') ON CONFLICT(key) DO UPDATE SET value='1'"
            )
            conn.commit()
