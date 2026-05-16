from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from dailytrack.config import DAILY_PRIORITIES, DAILY_STATUSES, LONG_STATUSES, STAGE_STATUSES
from dailytrack.ui.theme import SIZES


def _build_dialog_layout(dialog: QDialog, title: str) -> QFormLayout:
    dialog.setWindowTitle(title)
    dialog.setMinimumWidth(SIZES['dialog_width'])
    form = QFormLayout(dialog)
    form.setSpacing(10)
    return form


class DailyTaskDialog(QDialog):
    def __init__(self, parent=None, data: dict | None = None):
        super().__init__(parent)
        form = _build_dialog_layout(self, '今日任务')

        self.title_edit = QLineEdit(data.get('title', '') if data else '')
        self.desc_edit = QPlainTextEdit(data.get('description', '') if data else '')
        self.desc_edit.setMinimumHeight(100)

        self.priority = QComboBox()
        self.priority.addItems(DAILY_PRIORITIES)
        self.priority.setCurrentText(data.get('priority', '中') if data else '中')

        self.status = QComboBox()
        self.status.addItems(DAILY_STATUSES)
        self.status.setCurrentText(data.get('status', '未开始') if data else '未开始')

        total_minutes = int(data.get('estimated_minutes') or 0) if data else 0
        self.hours = QSpinBox()
        self.hours.setRange(0, 999)
        self.hours.setValue(total_minutes // 60)
        self.minutes = QSpinBox()
        self.minutes.setRange(0, 59)
        self.minutes.setValue(total_minutes % 60)

        self.date_edit = QLineEdit(data.get('task_date', '') if data else '')
        self.date_edit.setPlaceholderText('YYYY-MM-DD')

        form.addRow('标题', self.title_edit)
        form.addRow('备注', self.desc_edit)
        form.addRow('优先级', self.priority)
        form.addRow('状态', self.status)
        form.addRow('预计耗时(小时)', self.hours)
        form.addRow('预计耗时(分钟)', self.minutes)
        form.addRow('任务日期', self.date_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText('保存')
        buttons.button(QDialogButtonBox.Cancel).setText('取消')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def payload(self) -> dict:
        return {
            'title': self.title_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'priority': self.priority.currentText(),
            'status': self.status.currentText(),
            'estimated_minutes': self.hours.value() * 60 + self.minutes.value(),
            'task_date': self.date_edit.text().strip(),
        }


class LongTaskDialog(QDialog):
    def __init__(self, parent=None, data: dict | None = None):
        super().__init__(parent)
        form = _build_dialog_layout(self, '长线任务')

        self.title_edit = QLineEdit(data.get('title', '') if data else '')
        self.goal_edit = QPlainTextEdit(data.get('goal', '') if data else '')
        self.goal_edit.setMinimumHeight(100)

        self.priority = QComboBox()
        self.priority.addItems(DAILY_PRIORITIES)
        self.priority.setCurrentText(data.get('priority', '中') if data else '中')

        self.status = QComboBox()
        self.status.addItems(LONG_STATUSES)
        self.status.setCurrentText(data.get('status', '未开始') if data else '未开始')

        self.progress = QSpinBox()
        self.progress.setRange(0, 100)
        self.progress.setValue(int(data.get('progress') or 0) if data else 0)

        self.start_date = QLineEdit(data.get('start_date', '') if data else '')
        self.start_date.setPlaceholderText('YYYY-MM-DD')
        self.due_date = QLineEdit(data.get('due_date', '') if data else '')
        self.due_date.setPlaceholderText('YYYY-MM-DD')

        form.addRow('标题', self.title_edit)
        form.addRow('目标', self.goal_edit)
        form.addRow('优先级', self.priority)
        form.addRow('状态', self.status)
        form.addRow('进度(0-100)', self.progress)
        form.addRow('开始日期', self.start_date)
        form.addRow('截止日期', self.due_date)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText('保存')
        buttons.button(QDialogButtonBox.Cancel).setText('取消')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def payload(self) -> dict:
        return {
            'title': self.title_edit.text().strip(),
            'goal': self.goal_edit.toPlainText().strip(),
            'priority': self.priority.currentText(),
            'status': self.status.currentText(),
            'progress': self.progress.value(),
            'start_date': self.start_date.text().strip() or None,
            'due_date': self.due_date.text().strip() or None,
        }


class StageDialog(QDialog):
    def __init__(self, parent=None, data: dict | None = None):
        super().__init__(parent)
        form = _build_dialog_layout(self, '阶段')

        self.title_edit = QLineEdit(data.get('title', '') if data else '')
        self.desc_edit = QPlainTextEdit(data.get('description', '') if data else '')
        self.desc_edit.setMinimumHeight(80)

        self.status = QComboBox()
        self.status.addItems(STAGE_STATUSES)
        self.status.setCurrentText(data.get('status', '未开始') if data else '未开始')

        self.sort_order = QSpinBox()
        self.sort_order.setRange(0, 9999)
        self.sort_order.setValue(int(data.get('sort_order') or 0) if data else 0)

        form.addRow('标题', self.title_edit)
        form.addRow('描述', self.desc_edit)
        form.addRow('状态', self.status)
        form.addRow('排序', self.sort_order)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText('保存')
        buttons.button(QDialogButtonBox.Cancel).setText('取消')
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def payload(self) -> dict:
        return {
            'title': self.title_edit.text().strip(),
            'description': self.desc_edit.toPlainText().strip(),
            'status': self.status.currentText(),
            'sort_order': self.sort_order.value(),
        }


def show_error(parent: QWidget, text: str) -> None:
    QMessageBox.critical(parent, '错误', text)
