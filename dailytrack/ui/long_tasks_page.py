from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFontMetrics
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QFormLayout,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.task_service import TaskService
from dailytrack.ui.components import ActionButton, EmptyState, PageHeader, PriorityBadge, SecondaryButton, StatusBadge
from dailytrack.ui.dialogs import DailyTaskDialog, LongTaskDialog, StageDialog, show_error
from dailytrack.ui.texts import BTN_ADD_LONG, BTN_REFRESH_LIST, PAGE_LONG
from dailytrack.utils.date_utils import days_until, today_str


class StageManagerDialog(QDialog):
    def __init__(self, parent, task_service: TaskService, long_task_id: int):
        super().__init__(parent)
        self.task_service = task_service
        self.long_task_id = long_task_id
        self.setWindowTitle('阶段管理')
        self.resize(760, 440)
        self.selected_stage_id: int | None = None
        self.current_stages: list[dict] = []

        root = QVBoxLayout(self)
        bar = QHBoxLayout()
        self.add_btn = ActionButton('新增阶段')
        self.edit_btn = SecondaryButton('编辑阶段')
        self.del_btn = SecondaryButton('删除阶段')
        self.refresh_btn = SecondaryButton('刷新')
        for btn in [self.add_btn, self.edit_btn, self.del_btn, self.refresh_btn]:
            bar.addWidget(btn)
        bar.addStretch()
        root.addLayout(bar)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_host = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_host)
        self.scroll_layout.setContentsMargins(2, 2, 2, 2)
        self.scroll_layout.setSpacing(12)
        self.scroll.setWidget(self.scroll_host)
        root.addWidget(self.scroll)

        self.add_btn.clicked.connect(self.add_stage)
        self.edit_btn.clicked.connect(self.edit_stage)
        self.del_btn.clicked.connect(self.delete_stage)
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh()

    def _sid(self):
        return self.selected_stage_id

    def _set_selected_stage(self, stage_id: int):
        self.selected_stage_id = stage_id
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if not widget or not widget.property('stage-card'):
                continue
            is_selected = int(widget.property('stage-id')) == stage_id
            if is_selected:
                widget.setStyleSheet('#StageCard{background:#FFFFFF;border:1px solid #D5E2DC;border-radius:12px;}')
                effect = QGraphicsDropShadowEffect(widget)
                effect.setBlurRadius(28)
                effect.setOffset(0, 8)
                effect.setColor(QColor(16, 24, 40, 72))
                widget.setGraphicsEffect(effect)
            else:
                widget.setStyleSheet('#StageCard{background:#FFFFFF;border:1px solid #E6EFEB;border-radius:12px;}')
                widget.setGraphicsEffect(None)

    def _build_stage_card(self, stage: dict, idx: int) -> QWidget:
        card = QWidget()
        card.setObjectName('StageCard')
        card.setProperty('stage-card', True)
        card.setProperty('stage-id', int(stage['id']))
        card.setStyleSheet('#StageCard{background:#FFFFFF;border:1px solid #E6EFEB;border-radius:12px;}')

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        row1 = QHBoxLayout()
        title = QLabel(stage.get('title') or '-')
        title.setStyleSheet('font-size:16px;font-weight:700;color:#1F2937;')
        row1.addWidget(title)
        row1.addStretch()
        row1.addWidget(StatusBadge(stage.get('status') or '未开始'))
        layout.addLayout(row1)

        meta = QLabel(f"ID: {stage['id']}    排序: {stage.get('sort_order', 0)}")
        meta.setStyleSheet('font-size:12px;color:#6B7280;')
        layout.addWidget(meta)

        desc = QLabel(stage.get('description') or '暂无描述')
        desc.setStyleSheet('font-size:13px;color:#64748B;')
        desc.setWordWrap(True)
        layout.addWidget(desc)

        def _on_press(_event):
            self._set_selected_stage(int(stage['id']))

        card.mousePressEvent = _on_press  # type: ignore[method-assign]
        return card

    def refresh(self):
        self.current_stages = self.task_service.list_stages(self.long_task_id)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.selected_stage_id = None

        for i, stage in enumerate(self.current_stages):
            self.scroll_layout.addWidget(self._build_stage_card(stage, i))
        self.scroll_layout.addStretch()

        if self.current_stages:
            self._set_selected_stage(int(self.current_stages[0]['id']))

    def add_stage(self):
        dlg = StageDialog(self)
        if dlg.exec():
            payload = dlg.payload()
            payload['long_task_id'] = self.long_task_id
            self.task_service.create_stage(payload)
            self.refresh()

    def edit_stage(self):
        sid = self._sid()
        if sid is None:
            return
        stage = next((s for s in self.current_stages if int(s['id']) == sid), None)
        if not stage:
            return
        dlg = StageDialog(
            self,
            {
                'title': stage.get('title') or '',
                'status': stage.get('status') or '未开始',
                'sort_order': int(stage.get('sort_order') or 0),
                'description': stage.get('description') or '',
            },
        )
        if dlg.exec():
            self.task_service.update_stage(sid, dlg.payload())
            self.refresh()

    def delete_stage(self):
        sid = self._sid()
        if sid is None:
            return
        if QMessageBox.question(self, '确认删除', '确定删除该阶段吗？') == QMessageBox.Yes:
            self.task_service.delete_stage(sid)
            self.refresh()


class ProgressLogDialog(QDialog):
    def __init__(self, parent, task_service: TaskService, long_task_id: int):
        super().__init__(parent)
        self.task_service = task_service
        self.long_task_id = long_task_id
        self.selected_log_id: int | None = None
        self.setWindowTitle('进展日志')
        self.resize(860, 560)

        root = QVBoxLayout(self)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_host = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_host)
        self.scroll_layout.setContentsMargins(2, 2, 2, 2)
        self.scroll_layout.setSpacing(10)
        self.scroll.setWidget(self.scroll_host)
        root.addWidget(self.scroll)

        form = QFormLayout()
        self.date_edit = QLineEdit(today_str())
        self.date_edit.setPlaceholderText('YYYY-MM-DD')
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText('记录今天推进了什么、遇到什么阻碍、下一步计划。')
        self.content_edit.setMinimumHeight(120)
        form.addRow('日志日期', self.date_edit)
        form.addRow('日志内容', self.content_edit)
        root.addLayout(form)

        actions = QHBoxLayout()
        self.add_btn = ActionButton('新增日志')
        self.refresh_btn = SecondaryButton('刷新')
        actions.addWidget(self.add_btn)
        actions.addWidget(self.refresh_btn)
        actions.addStretch()
        root.addLayout(actions)

        self.add_btn.clicked.connect(self.add_log)
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh()

    def _set_selected_log(self, log_id: int):
        self.selected_log_id = log_id
        for i in range(self.scroll_layout.count()):
            widget = self.scroll_layout.itemAt(i).widget()
            if not widget or not widget.property('log-card'):
                continue
            is_selected = int(widget.property('log-id')) == log_id
            if is_selected:
                widget.setStyleSheet('#LogCard{background:#FFFFFF;border:1px solid #D5E2DC;border-radius:12px;}')
                effect = QGraphicsDropShadowEffect(widget)
                effect.setBlurRadius(28)
                effect.setOffset(0, 8)
                effect.setColor(QColor(16, 24, 40, 72))
                widget.setGraphicsEffect(effect)
            else:
                widget.setStyleSheet('#LogCard{background:#FFFFFF;border:1px solid #E6EFEB;border-radius:12px;}')
                widget.setGraphicsEffect(None)

    def _build_log_card(self, entry: dict, idx: int) -> QWidget:
        card = QWidget()
        card.setObjectName('LogCard')
        card.setProperty('log-card', True)
        card.setProperty('log-id', int(entry['id']))
        card.setStyleSheet('#LogCard{background:#FFFFFF;border:1px solid #E6EFEB;border-radius:12px;}')

        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(6)

        row1 = QHBoxLayout()
        id_label = QLabel(f"#{entry['id']}")
        id_label.setStyleSheet('font-size:12px;color:#6B7280;')
        row1.addWidget(id_label)
        row1.addStretch()
        date_label = QLabel(entry.get('log_date') or '-')
        date_label.setStyleSheet('font-size:12px;color:#6B7280;')
        row1.addWidget(date_label)
        layout.addLayout(row1)

        content = QLabel(entry.get('content') or '')
        content.setWordWrap(True)
        content.setStyleSheet('font-size:14px;color:#1F2937;')
        layout.addWidget(content)

        def _on_press(_event):
            self._set_selected_log(int(entry['id']))

        card.mousePressEvent = _on_press  # type: ignore[method-assign]
        return card

    def refresh(self):
        logs = self.task_service.list_progress_logs(self.long_task_id)
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for i, entry in enumerate(logs):
            self.scroll_layout.addWidget(self._build_log_card(entry, i))
        self.scroll_layout.addStretch()
        self.selected_log_id = None
        if logs:
            self._set_selected_log(int(logs[0]['id']))

    def add_log(self):
        content = self.content_edit.toPlainText().strip()
        if not content:
            return
        self.task_service.create_progress_log(
            {'long_task_id': self.long_task_id, 'log_date': self.date_edit.text().strip(), 'content': content}
        )
        self.content_edit.clear()
        self.refresh()


class LongTaskCard(QWidget):
    def __init__(self, task: dict, page: 'LongTasksPage', index: int):
        super().__init__()
        self.task = task
        self.page = page
        self.task_id = int(task['id'])
        self._selected = False

        wrap = QVBoxLayout(self)
        wrap.setContentsMargins(2, 4, 2, 4)

        card = QWidget()
        card.setObjectName('LongTaskCardShell')
        self.card = card
        self._card_bg = '#FFFFFF'
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
            '已暂停': '#D97706',
            '已归档': '#6B7280',
        }.get(task.get('status', ''), '#94A3B8')
        strip.setStyleSheet(f'background:{status_color};border-top-left-radius:14px;border-top-right-radius:14px;')
        layout.addWidget(strip)

        body = QWidget()
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(16, 12, 16, 14)
        body_l.setSpacing(8)

        row1 = QHBoxLayout()
        title = QLabel()
        title_metrics = QFontMetrics(title.font())
        full_title = task['title']
        title.setText(title_metrics.elidedText(full_title, Qt.ElideRight, 460))
        title.setToolTip(full_title)
        title.setStyleSheet('font-size:16px;font-weight:700;color:#1F2937;')
        row1.addWidget(title)
        row1.addStretch()
        row1.addWidget(StatusBadge(task['status']))
        row1.addWidget(PriorityBadge(task['priority']))
        body_l.addLayout(row1)

        goal = QLabel()
        full_goal = task.get('goal') or '暂无任务目标描述'
        goal_metrics = QFontMetrics(goal.font())
        goal.setText(goal_metrics.elidedText(full_goal, Qt.ElideRight, 560))
        goal.setToolTip(full_goal)
        goal.setWordWrap(True)
        goal.setStyleSheet('color:#6B7280;')
        body_l.addWidget(goal)

        progress = QProgressBar()
        progress.setRange(0, 100)
        progress.setValue(int(task.get('progress') or 0))
        progress.setFormat(f"进度 {int(task.get('progress') or 0)}%")
        body_l.addWidget(progress)

        due_date = task.get('due_date')
        left_text = '-'
        overdue_text = '否'
        if due_date:
            remain = days_until(due_date, today_str())
            left_text = f'{remain} 天'
            if remain < 0 and task['status'] not in ('已完成', '已归档'):
                overdue_text = '是'

        date_line = QLabel(
            f"开始：{task.get('start_date') or '-'}    截止：{task.get('due_date') or '-'}    剩余：{left_text}    逾期：{overdue_text}"
        )
        date_line.setStyleSheet('font-size:12px;color:#6B7280;')
        body_l.addWidget(date_line)

        actions = QHBoxLayout()
        gen_btn = ActionButton('生成今日任务')
        stage_btn = SecondaryButton('阶段')
        log_btn = SecondaryButton('日志')
        edit_btn = SecondaryButton('编辑')
        archive_btn = SecondaryButton('归档')
        del_btn = SecondaryButton('删除')

        gen_btn.clicked.connect(lambda: page.generate_daily(int(task['id'])))
        stage_btn.clicked.connect(lambda: page.manage_stages(int(task['id'])))
        log_btn.clicked.connect(lambda: page.manage_logs(int(task['id'])))
        edit_btn.clicked.connect(lambda: page.edit_task(int(task['id'])))
        archive_btn.clicked.connect(lambda: page.archive(int(task['id'])))
        del_btn.clicked.connect(lambda: page.delete(int(task['id'])))

        for btn in [gen_btn, stage_btn, log_btn, edit_btn, archive_btn, del_btn]:
            actions.addWidget(btn)
        actions.addStretch()
        body_l.addLayout(actions)
        layout.addWidget(body)

        wrap.addWidget(card)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.page.select_card(self.task_id)

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

    def _apply_card_style(self) -> None:
        border = '1px solid #D5E2DC' if self._selected else '1px solid #E6EFEB'
        self.card.setStyleSheet(
            f'#LongTaskCardShell{{background:{self._card_bg};border:{border};border-radius:14px;}}'
        )


class LongTasksPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        self.task_cards: list[LongTaskCard] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        self.header = PageHeader(PAGE_LONG, '跟踪需要多天或多周推进的任务')
        self.add_btn = ActionButton(BTN_ADD_LONG)
        self.refresh_btn = SecondaryButton(BTN_REFRESH_LIST)
        self.summary_label = QLabel('')
        self.summary_label.setProperty('role', 'page-subtitle')
        self.header.actions.addWidget(self.summary_label)
        self.header.add_action(self.refresh_btn)
        self.header.add_action(self.add_btn)
        root.addWidget(self.header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.scroll_host = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_host)
        self.scroll_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_layout.setSpacing(14)
        self.scroll.setWidget(self.scroll_host)
        root.addWidget(self.scroll)

        self.empty_state = EmptyState('暂无长线任务', '点击“新增长线任务”开始规划你的中长期目标。')
        root.addWidget(self.empty_state)
        self.empty_state.hide()

        self.add_btn.clicked.connect(self.add_task)
        self.refresh_btn.clicked.connect(self.refresh)

        self.refresh()

    def refresh(self):
        items = [x for x in self.task_service.list_long_tasks() if x.get('status') != '已归档']
        self.task_cards.clear()

        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        active = 0
        due_soon = 0
        overdue = 0
        for idx, task in enumerate(items):
            if task['status'] in ('已完成', '已归档'):
                pass
            else:
                active += 1
            if task.get('due_date') and task['status'] not in ('已完成', '已归档'):
                left = days_until(task['due_date'], today_str())
                if left < 0:
                    overdue += 1
                elif left <= 7:
                    due_soon += 1

            card = LongTaskCard(task, self, idx)
            self.task_cards.append(card)
            self.scroll_layout.addWidget(card)
        self.scroll_layout.addStretch()

        self.summary_label.setText(f'进行中：{active} · 即将到期：{due_soon} · 已逾期：{overdue} · 总数：{len(items)}')

        has_data = len(items) > 0
        self.scroll.setVisible(has_data)
        self.empty_state.setVisible(not has_data)

    def focus_task(self, task_id: int):
        # 卡片模式下暂不做精确滚动定位，保持页面可见与操作可达。
        self.refresh()
        self.select_card(task_id)

    def select_card(self, task_id: int) -> None:
        for card in self.task_cards:
            card.set_selected(card.task_id == int(task_id))

    def add_task(self):
        dlg = LongTaskDialog(self)
        if dlg.exec():
            try:
                self.task_service.create_long_task(dlg.payload())
                self.refresh()
            except Exception as e:
                show_error(self, str(e))

    def edit_task(self, task_id: int):
        cur = self.task_service.c.long_repo.get(task_id)
        if not cur:
            show_error(self, '任务不存在')
            return
        dlg = LongTaskDialog(self, cur)
        if dlg.exec():
            try:
                self.task_service.update_long_task(task_id, dlg.payload())
                self.refresh()
            except Exception as e:
                show_error(self, str(e))

    def generate_daily(self, task_id: int):
        dlg = DailyTaskDialog(self, {'task_date': today_str(), 'status': '未开始'})
        if dlg.exec():
            try:
                self.task_service.generate_daily_from_long_task(task_id, dlg.payload())
                QMessageBox.information(self, '成功', '已生成今日任务')
            except Exception as e:
                show_error(self, str(e))

    def manage_stages(self, task_id: int):
        StageManagerDialog(self, self.task_service, task_id).exec()
        self.refresh()

    def manage_logs(self, task_id: int):
        ProgressLogDialog(self, self.task_service, task_id).exec()

    def archive(self, task_id: int):
        self.task_service.archive_long_task(task_id)
        self.refresh()

    def delete(self, task_id: int):
        if QMessageBox.question(self, '确认删除', '确定删除这条长线任务吗？') == QMessageBox.Yes:
            self.task_service.delete_long_task(task_id)
            self.refresh()
