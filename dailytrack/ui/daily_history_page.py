from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.task_service import TaskService
from dailytrack.ui.components import PageHeader, PriorityBadge, SecondaryButton, StatusBadge
from dailytrack.utils.date_utils import is_valid_date, today_str


class HistoryTaskCard(QWidget):
    def __init__(self, task: dict, page: 'DailyHistoryPage'):
        super().__init__()
        self.task = task
        self.page = page
        self.task_id = int(task['id'])
        self._selected = False

        root = QVBoxLayout(self)
        root.setContentsMargins(2, 4, 2, 4)

        self.card = QWidget()
        self.card.setStyleSheet('#HistoryTaskCard{background:#FFFFFF;border:1px solid #E6EFEB;border-radius:14px;}')
        self.card.setObjectName('HistoryTaskCard')
        shell = QVBoxLayout(self.card)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        strip = QFrame()
        strip.setFixedHeight(5)
        status_color = {
            '未开始': '#94A3B8',
            '进行中': '#2F80ED',
            '已完成': '#14B86A',
            '已推迟': '#D97706',
            '已取消': '#9CA3AF',
        }.get(task.get('status', ''), '#94A3B8')
        strip.setStyleSheet(f'background:{status_color};border-top-left-radius:14px;border-top-right-radius:14px;')
        shell.addWidget(strip)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(16, 12, 16, 14)
        body_l.setSpacing(8)

        top = QHBoxLayout()
        title = QLabel(task.get('title') or '-')
        title.setStyleSheet('font-size:16px;font-weight:700;color:#1F2937;background:transparent;border:none;')
        top.addWidget(title)
        top.addStretch()
        top.addWidget(PriorityBadge(task.get('priority') or '中'))
        top.addWidget(StatusBadge(task.get('status') or '未开始'))
        body_l.addLayout(top)

        desc = QLabel(task.get('description') or '暂无说明')
        desc.setStyleSheet('color:#64748B;background:transparent;border:none;')
        body_l.addWidget(desc)

        meta = QLabel(f"日期：{task.get('task_date') or '-'}   预计耗时：{task.get('estimated_minutes') or 0} 分钟")
        meta.setStyleSheet('font-size:12px;color:#6B7280;background:transparent;border:none;')
        body_l.addWidget(meta)

        shell.addWidget(body)
        root.addWidget(self.card)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.page.select_card(self.task_id)

    def set_selected(self, selected: bool):
        self._selected = selected
        border = '1px solid #D5E2DC' if selected else '1px solid #E6EFEB'
        self.card.setStyleSheet(f'#HistoryTaskCard{{background:#FFFFFF;border:{border};border-radius:14px;}}')
        if selected:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(38)
            effect.setOffset(0, 12)
            effect.setColor(QColor(16, 24, 40, 88))
            self.card.setGraphicsEffect(effect)
        else:
            self.card.setGraphicsEffect(None)


class DailyHistoryPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        self.cards: list[HistoryTaskCard] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        self.header = PageHeader('任务回看', '按日期查看当天所有今日任务（含已完成、已推迟）。')
        self.date_input = QLineEdit(today_str())
        self.date_input.setPlaceholderText('请输入日期，格式：YYYY-MM-DD')
        self.refresh_btn = SecondaryButton('查询')
        self.header.actions.addWidget(self.date_input)
        self.header.add_action(self.refresh_btn)
        root.addWidget(self.header)

        self.hint = QLabel('')
        self.hint.setStyleSheet('font-size:12px;color:#D97706;')
        root.addWidget(self.hint)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.host = QWidget()
        self.host_layout = QVBoxLayout(self.host)
        self.host_layout.setContentsMargins(8, 8, 8, 8)
        self.host_layout.setSpacing(12)
        self.scroll.setWidget(self.host)
        root.addWidget(self.scroll)

        self.refresh_btn.clicked.connect(self.refresh)
        self.date_input.returnPressed.connect(self.refresh)
        self.refresh()

    def select_card(self, task_id: int):
        for card in self.cards:
            card.set_selected(card.task_id == int(task_id))

    def refresh(self) -> None:
        date_text = self.date_input.text().strip()
        self.cards.clear()

        while self.host_layout.count():
            item = self.host_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        if not is_valid_date(date_text):
            self.hint.setText('日期格式不正确，请输入 YYYY-MM-DD')
            self.host_layout.addStretch()
            return

        self.hint.setText('')
        items = self.task_service.list_tasks_for_date(date_text)
        if not items:
            msg = QLabel('该日期暂无今日任务')
            msg.setStyleSheet('font-size:13px;color:#6B7280;')
            self.host_layout.addWidget(msg)
            self.host_layout.addStretch()
            return

        for task in items:
            card = HistoryTaskCard(task, self)
            self.cards.append(card)
            self.host_layout.addWidget(card)
        self.host_layout.addStretch()

