from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from dailytrack.ui.theme import PRIORITY_STYLE, STATUS_STYLE


class SectionCard(QFrame):
    def __init__(self, title: str | None = None, parent=None):
        super().__init__(parent)
        self.setProperty('card', True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(10)
        if title:
            head = QLabel(title)
            head.setProperty('role', 'page-subtitle')
            head.setStyleSheet('font-size:16px;font-weight:700;color:#1F2937;')
            layout.addWidget(head)
        self.body_layout = layout


class PageHeader(QWidget):
    def __init__(self, title: str, subtitle: str = '', parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(12)
        left = QVBoxLayout()
        left.setSpacing(2)
        label_title = QLabel(title)
        label_title.setProperty('role', 'page-title')
        label_subtitle = QLabel(subtitle)
        label_subtitle.setProperty('role', 'page-subtitle')
        left.addWidget(label_title)
        if subtitle:
            left.addWidget(label_subtitle)
        root.addLayout(left)
        root.addStretch()
        self.actions = QHBoxLayout()
        self.actions.setSpacing(8)
        root.addLayout(self.actions)

    def add_action(self, button: QPushButton) -> None:
        self.actions.addWidget(button)


class MetricCard(QFrame):
    def __init__(self, title: str, value: str = '-', hint: str = ''):
        super().__init__()
        self.setProperty('card', True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(2)
        self.title = QLabel(title)
        self.title.setStyleSheet('font-size:12px;color:#6B7280;')
        self.value = QLabel(value)
        self.value.setStyleSheet('font-size:28px;font-weight:700;color:#1F2937;')
        self.hint = QLabel(hint)
        self.hint.setStyleSheet('font-size:12px;color:#9CA3AF;')
        layout.addWidget(self.title)
        layout.addWidget(self.value)
        if hint:
            layout.addWidget(self.hint)

    def set_value(self, value: str) -> None:
        self.value.setText(value)


class PillBadge(QLabel):
    def __init__(self, text: str, fg: str, bg: str):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(
            f'padding:2px 10px;border-radius:10px;font-size:12px;font-weight:600;color:{fg};background:{bg};'
        )


class StatusBadge(PillBadge):
    def __init__(self, text: str):
        fg, bg = STATUS_STYLE.get(text, ('#6B7280', '#F3F4F6'))
        super().__init__(text, fg, bg)


class PriorityBadge(PillBadge):
    def __init__(self, text: str):
        fg, bg = PRIORITY_STYLE.get(text, ('#6B7280', '#F3F4F6'))
        super().__init__(f'优先级: {text}', fg, bg)


class EmptyState(QFrame):
    def __init__(self, title: str, description: str):
        super().__init__()
        self.setProperty('card', True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(6)
        t = QLabel(title)
        t.setStyleSheet('font-size:15px;font-weight:700;color:#1F2937;')
        d = QLabel(description)
        d.setWordWrap(True)
        d.setStyleSheet('font-size:13px;color:#6B7280;')
        layout.addWidget(t)
        layout.addWidget(d)


class ActionButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)


class SecondaryButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setProperty('variant', 'secondary')
        self.style().polish(self)


class DangerButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setProperty('variant', 'danger')
        self.style().polish(self)
