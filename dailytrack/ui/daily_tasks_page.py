from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFontMetrics
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QGraphicsDropShadowEffect

from dailytrack.services.task_service import TaskService
from dailytrack.ui.components import ActionButton, EmptyState, PageHeader, PriorityBadge, SecondaryButton, StatusBadge
from dailytrack.ui.dialogs import DailyTaskDialog, show_error
from dailytrack.ui.texts import (
    BTN_ADD_DAILY,
    BTN_DELETE,
    BTN_DONE,
    BTN_EDIT,
    BTN_POSTPONE,
    BTN_REFRESH_LIST,
    PAGE_DAILY,
)
from dailytrack.utils.date_utils import today_str


class DailyTaskCard(QWidget):
    def __init__(self, task: dict, page: 'DailyTasksPage', index: int):
        super().__init__()
        self.task = task
        self.page = page
        self.task_id = int(task['id'])
        self._selected = False

        root = QVBoxLayout(self)
        root.setContentsMargins(2, 4, 2, 4)

        card = QWidget()
        card.setObjectName('DailyTaskCardShell')
        self._card_bg = '#FFFFFF'
        self.card = card
        self._apply_card_style()

        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

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
        layout.addWidget(strip)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(16, 12, 16, 14)
        body_l.setSpacing(8)

        top = QHBoxLayout()
        title_label = QLabel()
        title_label.setStyleSheet('font-size:16px;font-weight:700;color:#1F2937;')
        fm = QFontMetrics(title_label.font())
        full_title = task['title']
        title_label.setText(fm.elidedText(full_title, Qt.ElideRight, 480))
        title_label.setToolTip(full_title)
        top.addWidget(title_label)
        top.addStretch()
        top.addWidget(PriorityBadge(task['priority']))
        top.addWidget(StatusBadge(task['status']))
        body_l.addLayout(top)

        desc = task.get('description') or '暂无说明'
        desc_label = QLabel()
        desc_label.setStyleSheet('font-size:13px;color:#64748B;')
        desc_label.setText(fm.elidedText(desc, Qt.ElideRight, 700))
        desc_label.setToolTip(desc)
        body_l.addWidget(desc_label)

        meta = QLabel(
            f"预计耗时：{task.get('estimated_minutes') or 0} 分钟    来源：{task.get('source_type') or 'manual'}    日期：{task.get('task_date') or '-'}"
        )
        meta.setStyleSheet('font-size:12px;color:#6B7280;')
        body_l.addWidget(meta)

        actions = QHBoxLayout()
        edit_btn = SecondaryButton(BTN_EDIT)
        edit_btn.clicked.connect(lambda: page.edit_task(int(task['id'])))
        quick_done = SecondaryButton(BTN_DONE)
        quick_done.clicked.connect(lambda: page.complete(int(task['id'])))
        postpone_btn = SecondaryButton(BTN_POSTPONE)
        postpone_btn.clicked.connect(lambda: page.postpone(int(task['id'])))
        delete_btn = SecondaryButton(BTN_DELETE)
        delete_btn.setProperty('variant', 'danger')
        delete_btn.style().polish(delete_btn)
        delete_btn.clicked.connect(lambda: page.delete(int(task['id'])))

        actions.addWidget(edit_btn)
        actions.addWidget(quick_done)
        actions.addWidget(postpone_btn)
        actions.addWidget(delete_btn)
        actions.addStretch()
        body_l.addLayout(actions)
        layout.addWidget(body)

        root.addWidget(card)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.page.select_card(self.task_id)

    def _apply_card_style(self) -> None:
        border = '1px solid #D5E2DC' if self._selected else '1px solid #E6EFEB'
        self.card.setStyleSheet(
            f'#DailyTaskCardShell{{background:{self._card_bg};border:{border};border-radius:14px;}}'
        )

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self._apply_card_style()
        if selected:
            effect = QGraphicsDropShadowEffect(self)
            effect.setBlurRadius(38)
            effect.setOffset(0, 12)
            effect.setColor(QColor(16, 24, 40, 88))
            self.card.setGraphicsEffect(effect)
        else:
            self.card.setGraphicsEffect(None)


class DailyTasksPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        self.task_cards: list[DailyTaskCard] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        self.header = PageHeader(PAGE_DAILY, '聚焦今天要完成的任务')
        self.add_btn = ActionButton(BTN_ADD_DAILY)
        self.refresh_btn = SecondaryButton(BTN_REFRESH_LIST)
        self.rate_label = QLabel('今日完成率：0%')
        self.rate_label.setProperty('role', 'page-subtitle')
        self.header.actions.addWidget(self.rate_label)
        self.header.add_action(self.refresh_btn)
        self.header.add_action(self.add_btn)
        root.addWidget(self.header)

        progress_wrap = QWidget()
        progress_l = QHBoxLayout(progress_wrap)
        progress_l.setContentsMargins(0, 0, 0, 0)
        progress_l.setSpacing(10)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setFormat('%p%')
        progress_l.addWidget(self.progress)
        root.addWidget(progress_wrap)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_host = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_host)
        self.scroll_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_layout.setSpacing(14)
        self.scroll.setWidget(self.scroll_host)
        root.addWidget(self.scroll)

        self.empty_state = EmptyState('今天还没有待办事项', '点击“新增今日任务”开始规划今天的工作。')
        root.addWidget(self.empty_state)
        self.empty_state.hide()

        self.add_btn.clicked.connect(self.add_task)
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh()

    def refresh(self) -> None:
        try:
            tasks = [x for x in self.task_service.list_tasks_for_date(today_str()) if x.get('status') != '已完成']
            self.task_cards.clear()

            while self.scroll_layout.count():
                item = self.scroll_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            done = 0
            for idx, task in enumerate(tasks):
                card = DailyTaskCard(task, self, idx)
                self.task_cards.append(card)
                self.scroll_layout.addWidget(card)
                if task['status'] == '已完成':
                    done += 1
            self.scroll_layout.addStretch()

            total = len(tasks)
            rate = 0 if total == 0 else round(done / total * 100, 1)
            self.rate_label.setText(f'今日完成率：{rate}% · 任务数：{total}')
            self.progress.setValue(int(rate))

            has_data = total > 0
            self.scroll.setVisible(has_data)
            self.empty_state.setVisible(not has_data)
        except Exception as exc:
            show_error(self, str(exc))

    def focus_task(self, task_id: int) -> None:
        self.refresh()
        self.select_card(task_id)

    def select_card(self, task_id: int) -> None:
        for card in self.task_cards:
            card.set_selected(card.task_id == int(task_id))

    def add_task(self) -> None:
        dlg = DailyTaskDialog(self, {'task_date': today_str(), 'status': '未开始'})
        if dlg.exec():
            try:
                self.task_service.create_daily_task(dlg.payload())
                self.refresh()
            except Exception as exc:
                show_error(self, str(exc))

    def edit_task(self, task_id: int) -> None:
        current = self.task_service.c.daily_repo.get(task_id)
        if not current:
            return
        dlg = DailyTaskDialog(self, current)
        if dlg.exec():
            try:
                self.task_service.update_daily_task(task_id, dlg.payload())
                self.refresh()
            except Exception as exc:
                show_error(self, str(exc))

    def complete(self, task_id: int) -> None:
        try:
            self.task_service.complete_daily_task(task_id)
            self.refresh()
        except Exception as exc:
            show_error(self, str(exc))

    def postpone(self, task_id: int) -> None:
        try:
            self.task_service.postpone_to_tomorrow(task_id)
            self.refresh()
        except Exception as exc:
            show_error(self, str(exc))

    def delete(self, task_id: int) -> None:
        if QMessageBox.question(self, '确认删除', '确定删除这条今日任务吗？') != QMessageBox.Yes:
            return
        try:
            self.task_service.delete_daily_task(task_id)
            self.refresh()
        except Exception as exc:
            show_error(self, str(exc))
