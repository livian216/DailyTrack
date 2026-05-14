from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.task_service import TaskService
from dailytrack.ui.dialogs import DailyTaskDialog, LongTaskDialog, StageDialog, show_error
from dailytrack.utils.date_utils import days_until, today_str


PRIORITY_COLOR = {"高": "#dc2626", "中": "#d97706", "低": "#16a34a"}
STATUS_COLOR = {"未开始": "#64748b", "进行中": "#2563eb", "已完成": "#16a34a", "已暂停": "#d97706", "已归档": "#6b7280"}


class StageManagerDialog(QDialog):
    def __init__(self, parent, task_service: TaskService, long_task_id: int):
        super().__init__(parent)
        self.task_service = task_service
        self.long_task_id = long_task_id
        self.setWindowTitle("阶段管理")
        self.resize(760, 420)
        root = QVBoxLayout(self)
        bar = QHBoxLayout()
        a = QPushButton("新增阶段")
        b = QPushButton("编辑阶段")
        c = QPushButton("删除阶段")
        d = QPushButton("刷新")
        for x in [a, b, c, d]:
            bar.addWidget(x)
        bar.addStretch()
        root.addLayout(bar)
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["ID", "标题", "状态", "排序", "描述"])
        root.addWidget(self.table)
        a.clicked.connect(self.add_stage)
        b.clicked.connect(self.edit_stage)
        c.clicked.connect(self.delete_stage)
        d.clicked.connect(self.refresh)
        self.refresh()

    def _sid(self):
        r = self.table.currentRow()
        return None if r < 0 else int(self.table.item(r, 0).text())

    def refresh(self):
        rows = self.task_service.list_stages(self.long_task_id)
        self.table.setRowCount(len(rows))
        for i, s in enumerate(rows):
            self.table.setItem(i, 0, QTableWidgetItem(str(s["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(s["title"]))
            self.table.setItem(i, 2, QTableWidgetItem(s["status"]))
            self.table.setItem(i, 3, QTableWidgetItem(str(s["sort_order"])))
            self.table.setItem(i, 4, QTableWidgetItem(s.get("description") or ""))

    def add_stage(self):
        dlg = StageDialog(self)
        if dlg.exec():
            p = dlg.payload()
            p["long_task_id"] = self.long_task_id
            self.task_service.create_stage(p)
            self.refresh()

    def edit_stage(self):
        sid = self._sid()
        if sid is None:
            return
        r = self.table.currentRow()
        dlg = StageDialog(self, {
            "title": self.table.item(r, 1).text(),
            "status": self.table.item(r, 2).text(),
            "sort_order": int(self.table.item(r, 3).text()),
            "description": self.table.item(r, 4).text(),
        })
        if dlg.exec():
            self.task_service.update_stage(sid, dlg.payload())
            self.refresh()

    def delete_stage(self):
        sid = self._sid()
        if sid is None:
            return
        if QMessageBox.question(self, "确认删除", "确定删除该阶段吗？") == QMessageBox.Yes:
            self.task_service.delete_stage(sid)
            self.refresh()


class ProgressLogDialog(QDialog):
    def __init__(self, parent, task_service: TaskService, long_task_id: int):
        super().__init__(parent)
        self.task_service = task_service
        self.long_task_id = long_task_id
        self.setWindowTitle("进展日志")
        self.resize(820, 540)
        root = QVBoxLayout(self)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["ID", "日期", "内容"])
        root.addWidget(self.table)
        f = QFormLayout()
        self.date_edit = QLineEdit(today_str())
        self.date_edit.setPlaceholderText("YYYY-MM-DD")
        self.content_edit = QPlainTextEdit()
        f.addRow("日志日期", self.date_edit)
        f.addRow("日志内容", self.content_edit)
        root.addLayout(f)
        bar = QHBoxLayout()
        a = QPushButton("新增日志")
        b = QPushButton("刷新")
        bar.addWidget(a); bar.addWidget(b); bar.addStretch()
        root.addLayout(bar)
        a.clicked.connect(self.add_log)
        b.clicked.connect(self.refresh)
        self.refresh()

    def refresh(self):
        logs = self.task_service.list_progress_logs(self.long_task_id)
        self.table.setRowCount(len(logs))
        for i, x in enumerate(logs):
            self.table.setItem(i, 0, QTableWidgetItem(str(x["id"])))
            self.table.setItem(i, 1, QTableWidgetItem(x["log_date"]))
            self.table.setItem(i, 2, QTableWidgetItem(x["content"]))

    def add_log(self):
        content = self.content_edit.toPlainText().strip()
        if not content:
            return
        self.task_service.create_progress_log(
            {"long_task_id": self.long_task_id, "log_date": self.date_edit.text().strip(), "content": content}
        )
        self.content_edit.clear()
        self.refresh()


class LongTasksPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        root = QVBoxLayout(self)
        title = QLabel("长线任务")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f4fa8;")
        root.addWidget(title)
        top = QHBoxLayout()
        self.add_btn = QPushButton("新增长线任务")
        self.refresh_btn = QPushButton("刷新列表")
        top.addWidget(self.add_btn)
        top.addWidget(self.refresh_btn)
        top.addStretch()
        root.addLayout(top)
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels(["ID", "标题", "优先级", "状态", "进度", "开始日期", "截止日期", "剩余天数", "逾期", "操作"])
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(9, QHeaderView.ResizeToContents)
        root.addWidget(self.table)
        self.add_btn.clicked.connect(self.add_task)
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh()

    def _item(self, value: str, color: str | None = None):
        it = QTableWidgetItem(value)
        if value:
            it.setToolTip(value)
        if color:
            it.setForeground(QColor(color))
        it.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        return it

    def _set_ops(self, row: int, task_id: int):
        btn = QPushButton("操作")

        def show_menu():
            m = QMenu(btn)
            a1 = m.addAction("编辑")
            a2 = m.addAction("生成今日任务")
            a3 = m.addAction("阶段管理")
            a4 = m.addAction("进展日志")
            a5 = m.addAction("归档")
            a6 = m.addAction("删除")
            p = m.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
            if p == a1: self.edit_task(task_id)
            elif p == a2: self.generate_daily(task_id)
            elif p == a3: self.manage_stages(task_id)
            elif p == a4: self.manage_logs(task_id)
            elif p == a5: self.archive(task_id)
            elif p == a6: self.delete(task_id)

        btn.clicked.connect(show_menu)
        self.table.setCellWidget(row, 9, btn)

    def refresh(self):
        items = self.task_service.list_long_tasks()
        self.table.setRowCount(len(items))
        for r, x in enumerate(items):
            self.table.setItem(r, 0, self._item(str(x["id"])))
            self.table.setItem(r, 1, self._item(x["title"]))
            self.table.setItem(r, 2, self._item(x["priority"], PRIORITY_COLOR.get(x["priority"])))
            self.table.setItem(r, 3, self._item(x["status"], STATUS_COLOR.get(x["status"])))
            self.table.setItem(r, 4, self._item(str(x["progress"])))
            self.table.setItem(r, 5, self._item(x.get("start_date") or ""))
            self.table.setItem(r, 6, self._item(x.get("due_date") or ""))
            left = ""
            overdue = "否"
            if x.get("due_date"):
                d = days_until(x["due_date"], today_str())
                left = str(d)
                overdue = "是" if d < 0 and x["status"] not in ("已完成", "已归档") else "否"
            self.table.setItem(r, 7, self._item(left))
            self.table.setItem(r, 8, self._item(overdue, "#dc2626" if overdue == "是" else "#16a34a"))
            self._set_ops(r, int(x["id"]))

    def focus_task(self, task_id: int):
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == str(task_id):
                self.table.selectRow(row)
                self.table.scrollToItem(item, QTableWidget.PositionAtCenter)
                return

    def add_task(self):
        dlg = LongTaskDialog(self)
        if dlg.exec():
            try:
                self.task_service.create_long_task(dlg.payload()); self.refresh()
            except Exception as e:
                show_error(self, str(e))

    def edit_task(self, task_id: int):
        cur = self.task_service.c.long_repo.get(task_id)
        if not cur:
            show_error(self, "任务不存在"); return
        dlg = LongTaskDialog(self, cur)
        if dlg.exec():
            try:
                self.task_service.update_long_task(task_id, dlg.payload()); self.refresh()
            except Exception as e:
                show_error(self, str(e))

    def generate_daily(self, task_id: int):
        dlg = DailyTaskDialog(self, {"task_date": today_str(), "status": "未开始"})
        if dlg.exec():
            try:
                self.task_service.generate_daily_from_long_task(task_id, dlg.payload())
                QMessageBox.information(self, "成功", "已生成今日任务")
            except Exception as e:
                show_error(self, str(e))

    def manage_stages(self, task_id: int):
        StageManagerDialog(self, self.task_service, task_id).exec(); self.refresh()

    def manage_logs(self, task_id: int):
        ProgressLogDialog(self, self.task_service, task_id).exec()

    def archive(self, task_id: int):
        self.task_service.archive_long_task(task_id); self.refresh()

    def delete(self, task_id: int):
        if QMessageBox.question(self, "确认删除", "确定删除这条长线任务吗？") == QMessageBox.Yes:
            self.task_service.delete_long_task(task_id); self.refresh()
