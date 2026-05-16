from __future__ import annotations

from typing import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QProgressBar, QVBoxLayout, QWidget

from dailytrack.services.dashboard_service import DashboardService
from dailytrack.ui.components import ActionButton, EmptyState, MetricCard, PageHeader, SectionCard, SecondaryButton
from dailytrack.ui.texts import BOARD_HIGH, BOARD_OVERDUE, BOARD_UPCOMING, BTN_REFRESH_STATS, PAGE_DASHBOARD


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
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(16)

        self.header = PageHeader(PAGE_DASHBOARD, '快速了解今天进度与长线任务风险')
        self.date_label = QLabel('')
        self.date_label.setProperty('role', 'page-subtitle')
        self.refresh_btn = SecondaryButton(BTN_REFRESH_STATS)
        self.refresh_btn.clicked.connect(self.refresh)
        self.header.actions.addWidget(self.date_label)
        self.header.add_action(self.refresh_btn)
        root.addWidget(self.header)

        cards = QGridLayout()
        cards.setSpacing(12)
        self.total_card = MetricCard('今日任务总数', '-', '今日计划事项')
        self.done_card = MetricCard('已完成', '-', '完成数量')
        self.pending_card = MetricCard('未完成', '-', '待处理数量')
        self.rate_card = MetricCard('完成率', '0%', '完成效率')
        cards.addWidget(self.total_card, 0, 0)
        cards.addWidget(self.done_card, 0, 1)
        cards.addWidget(self.pending_card, 0, 2)
        cards.addWidget(self.rate_card, 0, 3)
        root.addLayout(cards)

        progress_card = SectionCard('今日完成进度')
        self.rate_bar = QProgressBar()
        self.rate_bar.setRange(0, 100)
        self.rate_bar.setFormat('%p%')
        progress_card.body_layout.addWidget(self.rate_bar)
        root.addWidget(progress_card)

        board = QHBoxLayout()
        board.setSpacing(12)

        self.high_box, self.high_list = self._build_task_board(BOARD_HIGH)
        self.upcoming_box, self.upcoming_list = self._build_task_board(BOARD_UPCOMING)
        self.overdue_box, self.overdue_list = self._build_task_board(BOARD_OVERDUE)

        board.addWidget(self.high_box)
        board.addWidget(self.upcoming_box)
        board.addWidget(self.overdue_box)
        root.addLayout(board)

        self.high_list.itemDoubleClicked.connect(self._open_high_item)
        self.upcoming_list.itemDoubleClicked.connect(self._open_long_item)
        self.overdue_list.itemDoubleClicked.connect(self._open_long_item)

        self.refresh()

    def _build_task_board(self, title: str):
        box = SectionCard(title)
        task_list = QListWidget()
        task_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        task_list.setStyleSheet(
            'QListWidget{border:none;background:transparent;outline:0;}'
            'QListWidget::item{padding:8px;border-radius:8px;border:1px solid #EAF5EE;background:#FFFFFF;color:#1F2937;}'
            'QListWidget::item:selected{background:#EAF7FF;color:#1F2937;border:1px solid #D7EEF9;}'
            'QListWidget::item:hover{background:#F3FBF8;color:#1F2937;border:1px solid #D7EEF9;}'
            'QListWidget::item:focus{outline:none;}'
        )
        box.body_layout.addWidget(task_list)
        return box, task_list

    def _fill_list(self, widget: QListWidget, items: list[dict], formatter, target: str) -> None:
        widget.clear()
        if not items:
            widget.addItem(QListWidgetItem('暂无数据'))
            return
        for idx, row in enumerate(items[:20]):
            full_text = formatter(row)
            metrics = QFontMetrics(widget.font())
            # Keep list rows single-line and readable; reveal full text by tooltip.
            short_text = metrics.elidedText(full_text, Qt.ElideRight, max(widget.viewport().width() - 24, 120))
            item = QListWidgetItem(short_text)
            item.setToolTip(full_text)
            item.setBackground(QColor('#FFFFFF' if idx % 2 == 0 else '#F8FFFB'))
            item.setData(Qt.UserRole, {'target': target, 'id': int(row['id'])})
            widget.addItem(item)

    def _open_high_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.UserRole)
        if not data or not self.open_daily_task:
            return
        self.open_daily_task(int(data['id']))

    def _open_long_item(self, item: QListWidgetItem) -> None:
        data = item.data(Qt.UserRole)
        if not data or not self.open_long_task:
            return
        self.open_long_task(int(data['id']))

    def refresh(self) -> None:
        stats = self.dashboard_service.today_stats()
        self.date_label.setText(f"日期：{stats['date']}")

        self.total_card.set_value(str(stats['total']))
        self.done_card.set_value(str(stats['done']))
        self.pending_card.set_value(str(stats['pending']))
        self.rate_card.set_value(f"{stats['rate']}%")
        self.rate_bar.setValue(int(stats['rate']))

        self._fill_list(
            self.high_list,
            stats['high_priority'],
            lambda x: f"{x['title']} · {x['status']}",
            'daily',
        )
        self._fill_list(
            self.upcoming_list,
            stats['upcoming'],
            lambda x: f"{x['title']} · 截止 {x.get('due_date') or '-'}",
            'long',
        )
        self._fill_list(
            self.overdue_list,
            stats['overdue'],
            lambda x: f"{x['title']} · 截止 {x.get('due_date') or '-'}",
            'long',
        )
