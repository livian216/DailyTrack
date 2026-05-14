from __future__ import annotations

from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.task_service import TaskService
from dailytrack.utils.date_utils import today_str


class ReviewPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        root = QVBoxLayout(self)
        title = QLabel("每日复盘")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#7c3aed;")
        root.addWidget(title)
        form = QFormLayout()
        self.date_edit = QLineEdit(today_str())
        self.date_edit.setPlaceholderText("YYYY-MM-DD")
        self.stats = QLabel("")
        form.addRow("日期", self.date_edit)
        form.addRow("统计", self.stats)
        root.addLayout(form)
        root.addWidget(QLabel("今日总结"))
        self.summary = QPlainTextEdit()
        root.addWidget(self.summary)
        root.addWidget(QLabel("未完成原因"))
        self.unfinished = QPlainTextEdit()
        root.addWidget(self.unfinished)
        root.addWidget(QLabel("明日重点"))
        self.tomorrow = QPlainTextEdit()
        root.addWidget(self.tomorrow)
        b = QHBoxLayout()
        self.save_btn = QPushButton("保存复盘")
        self.refresh_btn = QPushButton("刷新统计")
        b.addWidget(self.save_btn); b.addWidget(self.refresh_btn); b.addStretch()
        root.addLayout(b)
        view = QHBoxLayout()
        view.addWidget(QLabel("回看日期"))
        self.view_date_edit = QLineEdit()
        self.view_date_edit.setPlaceholderText("输入要回看的日期，如 2026-05-01")
        self.view_btn = QPushButton("查看复盘")
        view.addWidget(self.view_date_edit); view.addWidget(self.view_btn)
        root.addLayout(view)
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
            QMessageBox.information(self, "提示", "请先输入日期（YYYY-MM-DD）")
            return
        self.date_edit.setText(value)
        self.load()

    def load(self) -> None:
        try:
            d = self.selected_date()
            tasks = self.task_service.list_tasks_for_date(d)
            total = len(tasks)
            done = len([x for x in tasks if x["status"] == "已完成"])
            pending = len([x for x in tasks if x["status"] not in ("已完成", "已取消")])
            rate = 0 if total == 0 else round(done / total * 100, 1)
            self.stats.setText(f"总数：{total}，已完成：{done}，未完成：{pending}，完成率：{rate}%")
            r = self.task_service.load_review(d)
            if r:
                self.summary.setPlainText(r.get("summary") or "")
                self.unfinished.setPlainText(r.get("unfinished_reason") or "")
                self.tomorrow.setPlainText(r.get("tomorrow_focus") or "")
            else:
                self.summary.clear(); self.unfinished.clear(); self.tomorrow.clear()
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))

    def save(self) -> None:
        try:
            self.task_service.save_review(
                {
                    "review_date": self.selected_date(),
                    "summary": self.summary.toPlainText().strip(),
                    "unfinished_reason": self.unfinished.toPlainText().strip(),
                    "tomorrow_focus": self.tomorrow.toPlainText().strip(),
                }
            )
            QMessageBox.information(self, "成功", "复盘已保存")
        except Exception as e:
            QMessageBox.critical(self, "错误", str(e))
