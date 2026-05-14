from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.dashboard_service import DashboardService


class StatCard(QFrame):
    def __init__(self, title: str, color: str):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("QFrame{border:1px solid #dbe1e7;border-radius:10px;background:#ffffff;}")
        layout = QVBoxLayout(self)
        self.title = QLabel(title)
        self.title.setStyleSheet("color:#64748b;font-size:12px;")
        self.value = QLabel("-")
        self.value.setStyleSheet(f"font-size:28px;font-weight:700;color:{color};")
        layout.addWidget(self.title)
        layout.addWidget(self.value)


class DashboardPage(QWidget):
    def __init__(
        self,
        dashboard_service: DashboardService,
        open_daily_task: Callable[[int], None] | None = None,
        open_long_task: Callable[[int], None] | None = None,
    ):
        super().__init__()
        self.dashboard_service = dashboard_service
        self.open_daily_task = open_daily_task
        self.open_long_task = open_long_task

        root = QVBoxLayout(self)
        header = QHBoxLayout()
        self.title = QLabel("首页总览")
        self.title.setStyleSheet("font-size:22px;font-weight:700;color:#0f4fa8;")
        self.date_label = QLabel("")
        self.date_label.setStyleSheet("color:#64748b;font-size:13px;")
        self.refresh_btn = QPushButton("刷新统计")
        self.refresh_btn.clicked.connect(self.refresh)
        header.addWidget(self.title)
        header.addWidget(self.date_label)
        header.addStretch()
        header.addWidget(self.refresh_btn)
        root.addLayout(header)

        cards = QGridLayout()
        self.total_card = StatCard("今日任务总数", "#0f4fa8")
        self.done_card = StatCard("已完成", "#16a34a")
        self.pending_card = StatCard("未完成", "#f59e0b")
        self.high_card = StatCard("高优先级未完成", "#dc2626")
        cards.addWidget(self.total_card, 0, 0)
        cards.addWidget(self.done_card, 0, 1)
        cards.addWidget(self.pending_card, 0, 2)
        cards.addWidget(self.high_card, 0, 3)
        root.addLayout(cards)

        rate_box = QGroupBox("今日完成率")
        rate_layout = QVBoxLayout(rate_box)
        self.rate_bar = QProgressBar()
        self.rate_bar.setRange(0, 100)
        self.rate_text = QLabel("0%")
        self.rate_text.setAlignment(Qt.AlignRight)
        self.rate_text.setStyleSheet("font-weight:700;color:#0f4fa8;")
        rate_layout.addWidget(self.rate_bar)
        rate_layout.addWidget(self.rate_text)
        root.addWidget(rate_box)

        boards = QHBoxLayout()
        self.high_list = QListWidget()
        self.upcoming_list = QListWidget()
        self.overdue_list = QListWidget()
        for title, lst in [
            ("高优先级未完成（双击跳转）", self.high_list),
            ("7天内到期任务（双击跳转）", self.upcoming_list),
            ("已逾期任务（双击跳转）", self.overdue_list),
        ]:
            box = QGroupBox(title)
            lay = QVBoxLayout(box)
            lay.addWidget(lst)
            boards.addWidget(box)
        root.addLayout(boards)
        root.addStretch()

        self.high_list.itemDoubleClicked.connect(self._open_high_item)
        self.upcoming_list.itemDoubleClicked.connect(self._open_long_item)
        self.overdue_list.itemDoubleClicked.connect(self._open_long_item)

        self.refresh()

    def _fill_list(self, widget: QListWidget, items: list[dict], formatter, target: str) -> None:
        widget.clear()
        if not items:
            empty = QListWidgetItem("无")
            empty.setData(Qt.UserRole, None)
            widget.addItem(empty)
            return
        for x in items[:20]:
            item = QListWidgetItem(formatter(x))
            item.setData(Qt.UserRole, {"target": target, "id": int(x["id"])})
            widget.addItem(item)

    def _open_high_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.UserRole)
        if not data or not self.open_daily_task:
            return
        self.open_daily_task(int(data["id"]))

    def _open_long_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.UserRole)
        if not data or not self.open_long_task:
            return
        self.open_long_task(int(data["id"]))

    def refresh(self) -> None:
        s = self.dashboard_service.today_stats()
        self.date_label.setText(f"日期：{s['date']}")
        self.total_card.value.setText(str(s["total"]))
        self.done_card.value.setText(str(s["done"]))
        self.pending_card.value.setText(str(s["pending"]))
        self.high_card.value.setText(str(len(s["high_priority"])))
        self.rate_bar.setValue(int(s["rate"]))
        self.rate_text.setText(f"{s['rate']}%")

        self._fill_list(self.high_list, s["high_priority"], lambda x: f"{x['title']}（{x['status']}）", "daily")
        self._fill_list(self.upcoming_list, s["upcoming"], lambda x: f"{x['title']} | 截止 {x.get('due_date') or '-'}", "long")
        self._fill_list(self.overdue_list, s["overdue"], lambda x: f"{x['title']} | 截止 {x.get('due_date') or '-'}", "long")
