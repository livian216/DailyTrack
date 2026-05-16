from __future__ import annotations

from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPlainTextEdit, QVBoxLayout, QWidget

from dailytrack.services.task_service import TaskService
from dailytrack.ui.components import ActionButton, MetricCard, PageHeader, SectionCard, SecondaryButton
from dailytrack.ui.texts import PAGE_REVIEW
from dailytrack.utils.date_utils import today_str


class ReviewPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        self.header = PageHeader(PAGE_REVIEW, '记录今天、复盘问题、明确明日重点')
        self.date_edit = QLineEdit(today_str())
        self.date_edit.setFixedWidth(140)
        self.date_edit.setPlaceholderText('YYYY-MM-DD')
        self.save_btn = ActionButton('保存复盘')
        self.refresh_btn = SecondaryButton('刷新统计')
        self.header.actions.addWidget(QLabel('日期'))
        self.header.actions.addWidget(self.date_edit)
        self.header.add_action(self.refresh_btn)
        self.header.add_action(self.save_btn)
        root.addWidget(self.header)

        stats = QHBoxLayout()
        stats.setSpacing(12)
        self.total_card = MetricCard('任务总数', '0')
        self.done_card = MetricCard('已完成', '0')
        self.pending_card = MetricCard('未完成', '0')
        self.rate_card = MetricCard('完成率', '0%')
        for card in [self.total_card, self.done_card, self.pending_card, self.rate_card]:
            stats.addWidget(card)
        root.addLayout(stats)

        form_card = SectionCard('复盘内容')
        self.summary = QPlainTextEdit()
        self.summary.setPlaceholderText('今天最重要的进展、结果与收获。')
        self.summary.setMinimumHeight(120)
        self.unfinished = QPlainTextEdit()
        self.unfinished.setPlaceholderText('未完成事项的原因与阻碍。')
        self.unfinished.setMinimumHeight(120)
        self.tomorrow = QPlainTextEdit()
        self.tomorrow.setPlaceholderText('明天最优先推进的 1-3 件事。')
        self.tomorrow.setMinimumHeight(120)

        form_card.body_layout.addWidget(QLabel('今日总结'))
        form_card.body_layout.addWidget(self.summary)
        form_card.body_layout.addWidget(QLabel('未完成原因'))
        form_card.body_layout.addWidget(self.unfinished)
        form_card.body_layout.addWidget(QLabel('明日重点'))
        form_card.body_layout.addWidget(self.tomorrow)
        root.addWidget(form_card)

        lookup = QHBoxLayout()
        lookup.addWidget(QLabel('回看日期'))
        self.view_date_edit = QLineEdit()
        self.view_date_edit.setPlaceholderText('输入要回看的日期，例如 2026-05-01')
        self.view_btn = SecondaryButton('查看复盘')
        lookup.addWidget(self.view_date_edit)
        lookup.addWidget(self.view_btn)
        root.addLayout(lookup)

        self.date_edit.returnPressed.connect(self.load)
        self.refresh_btn.clicked.connect(self.load)
        self.save_btn.clicked.connect(self.save)
        self.view_btn.clicked.connect(self.view_review_by_input)
        self.load()

    def selected_date(self) -> str:
        return self.date_edit.text().strip()

    def view_review_by_input(self) -> None:
        value = self.view_date_edit.text().strip()
        if not value:
            QMessageBox.information(self, '提示', '请先输入日期（YYYY-MM-DD）')
            return
        self.date_edit.setText(value)
        self.load()

    def load(self) -> None:
        try:
            date_text = self.selected_date()
            tasks = self.task_service.list_tasks_for_date(date_text)
            total = len(tasks)
            done = len([x for x in tasks if x['status'] == '已完成'])
            pending = len([x for x in tasks if x['status'] not in ('已完成', '已取消')])
            rate = 0 if total == 0 else round(done / total * 100, 1)

            self.total_card.set_value(str(total))
            self.done_card.set_value(str(done))
            self.pending_card.set_value(str(pending))
            self.rate_card.set_value(f'{rate}%')

            review = self.task_service.load_review(date_text)
            if review:
                self.summary.setPlainText(review.get('summary') or '')
                self.unfinished.setPlainText(review.get('unfinished_reason') or '')
                self.tomorrow.setPlainText(review.get('tomorrow_focus') or '')
            else:
                self.summary.clear()
                self.unfinished.clear()
                self.tomorrow.clear()
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def refresh(self) -> None:
        self.load()

    def save(self) -> None:
        try:
            self.task_service.save_review(
                {
                    'review_date': self.selected_date(),
                    'summary': self.summary.toPlainText().strip(),
                    'unfinished_reason': self.unfinished.toPlainText().strip(),
                    'tomorrow_focus': self.tomorrow.toPlainText().strip(),
                }
            )
            QMessageBox.information(self, '已保存', '每日复盘已保存。')
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))
