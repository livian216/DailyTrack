from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.task_service import TaskService
from dailytrack.ui.components import PageHeader, PriorityBadge, SecondaryButton, StatusBadge


class ArchivedTaskCard(QWidget):
    def __init__(self, task: dict, page: 'LongArchivePage'):
        super().__init__()
        self.task = task
        self.page = page
        self.task_id = int(task['id'])
        self._selected = False

        root = QVBoxLayout(self)
        root.setContentsMargins(2, 4, 2, 4)

        self.card = QWidget()
        self.card.setObjectName('ArchivedTaskCard')
        self.card.setStyleSheet('#ArchivedTaskCard{background:#FFFFFF;border:1px solid #E6EFEB;border-radius:14px;}')
        shell = QVBoxLayout(self.card)
        shell.setContentsMargins(0, 0, 0, 0)
        shell.setSpacing(0)

        strip = QFrame()
        strip.setFixedHeight(5)
        strip.setStyleSheet('background:#6B7280;border-top-left-radius:14px;border-top-right-radius:14px;')
        shell.addWidget(strip)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(14, 12, 14, 12)
        body_l.setSpacing(8)

        top = QHBoxLayout()
        title = QLabel(task.get('title') or '-')
        title.setStyleSheet('font-size:16px;font-weight:700;color:#1F2937;background:transparent;border:none;')
        top.addWidget(title)
        top.addStretch()
        top.addWidget(StatusBadge(task.get('status') or '已归档'))
        top.addWidget(PriorityBadge(task.get('priority') or '中'))
        body_l.addLayout(top)

        goal = QLabel(task.get('goal') or '暂无目标描述')
        goal.setStyleSheet('color:#64748B;background:transparent;border:none;')
        body_l.addWidget(goal)

        p = QProgressBar()
        p.setRange(0, 100)
        p.setValue(int(task.get('progress') or 0))
        p.setFormat(f"进度 {int(task.get('progress') or 0)}%")
        body_l.addWidget(p)

        meta = QLabel(f"归档时间：{task.get('archived_at') or '-'}    截止：{task.get('due_date') or '-'}")
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
        self.card.setStyleSheet(f'#ArchivedTaskCard{{background:#FFFFFF;border:{border};border-radius:14px;}}')
        if selected:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(38)
            effect.setOffset(0, 12)
            effect.setColor(QColor(16, 24, 40, 88))
            self.card.setGraphicsEffect(effect)
        else:
            self.card.setGraphicsEffect(None)


class LongArchivePage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        self.cards: list[ArchivedTaskCard] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        self.header = PageHeader('归档任务', '回看归档的长线任务，可按标题关键词搜索。')
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入标题关键词...')
        self.refresh_btn = SecondaryButton('查询')
        self.header.actions.addWidget(self.search_input)
        self.header.add_action(self.refresh_btn)
        root.addWidget(self.header)

        self.tip = QLabel('')
        self.tip.setStyleSheet('font-size:13px;color:#6B7280;')
        root.addWidget(self.tip)

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
        self.search_input.returnPressed.connect(self.refresh)
        self.search_input.textChanged.connect(lambda *_: self.refresh())
        self.refresh()

    def select_card(self, task_id: int):
        for card in self.cards:
            card.set_selected(card.task_id == int(task_id))

    def refresh(self) -> None:
        keyword = self.search_input.text().strip()
        self.cards.clear()

        while self.host_layout.count():
            item = self.host_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        items = self.task_service.list_archived_long_tasks(keyword)
        if not items:
            self.tip.setText('暂无匹配的长线归档任务，请核对关键词是否为长线任务标题')
            self.host_layout.addStretch()
            return

        self.tip.setText('')
        for task in items:
            card = ArchivedTaskCard(task, self)
            self.cards.append(card)
            self.host_layout.addWidget(card)
        self.host_layout.addStretch()

