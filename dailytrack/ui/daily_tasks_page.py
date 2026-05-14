from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QHeaderView,
    QHBoxLayout,
    QLabel,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from dailytrack.services.task_service import TaskService
from dailytrack.ui.dialogs import DailyTaskDialog, show_error
from dailytrack.utils.date_utils import today_str


PRIORITY_COLOR = {"高": "#dc2626", "中": "#d97706", "低": "#16a34a"}
STATUS_COLOR = {"未开始": "#64748b", "进行中": "#2563eb", "已完成": "#16a34a", "已推迟": "#d97706", "已取消": "#6b7280"}


class DailyTasksPage(QWidget):
    def __init__(self, task_service: TaskService):
        super().__init__()
        self.task_service = task_service
        root = QVBoxLayout(self)

        title = QLabel("今日任务")
        title.setStyleSheet("font-size:20px;font-weight:700;color:#0f4fa8;")
        root.addWidget(title)

        top = QHBoxLayout()
        self.add_btn = QPushButton("新增今日任务")
        self.refresh_btn = QPushButton("刷新列表")
        self.rate_label = QLabel("今日完成率：0%")
        self.rate_label.setStyleSheet("font-weight:700;color:#0f4fa8;")
        top.addWidget(self.add_btn)
        top.addWidget(self.refresh_btn)
        top.addWidget(self.rate_label)
        top.addStretch()
        root.addLayout(top)

        self.table = QTableWidget(0, 9)
        self.table.setHorizontalHeaderLabels(["ID", "标题", "备注", "优先级", "状态", "耗时(分钟)", "来源", "日期", "操作"])
        self.table.setWordWrap(True)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(8, QHeaderView.ResizeToContents)
        self.table.verticalHeader().setDefaultSectionSize(56)
        root.addWidget(self.table)

        self.add_btn.clicked.connect(self.add_task)
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh()

    def _item(self, value: str, color: str | None = None) -> QTableWidgetItem:
        item = QTableWidgetItem(value)
        item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        if value:
            item.setToolTip(value)
        if color:
            item.setForeground(QColor(color))
        return item

    def _set_ops(self, row: int, task_id: int) -> None:
        btn = QPushButton("操作")

        def show_menu():
            menu = QMenu(btn)
            a1 = menu.addAction("编辑")
            a2 = menu.addAction("完成")
            a3 = menu.addAction("推迟到明天")
            a4 = menu.addAction("删除")
            picked = menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))
            if picked == a1:
                self.edit_task(task_id)
            elif picked == a2:
                self.complete(task_id)
            elif picked == a3:
                self.postpone(task_id)
            elif picked == a4:
                self.delete(task_id)

        btn.clicked.connect(show_menu)
        self.table.setCellWidget(row, 8, btn)

    def refresh(self) -> None:
        try:
            tasks = self.task_service.list_tasks_for_date(today_str())
            self.table.setRowCount(len(tasks))
            done = 0
            for r, t in enumerate(tasks):
                self.table.setItem(r, 0, self._item(str(t["id"])))
                self.table.setItem(r, 1, self._item(t["title"]))
                self.table.setItem(r, 2, self._item(t.get("description") or ""))
                self.table.setItem(r, 3, self._item(t["priority"], PRIORITY_COLOR.get(t["priority"])))
                self.table.setItem(r, 4, self._item(t["status"], STATUS_COLOR.get(t["status"])))
                self.table.setItem(r, 5, self._item(str(t.get("estimated_minutes") or "")))
                self.table.setItem(r, 6, self._item(t.get("source_type") or "manual"))
                self.table.setItem(r, 7, self._item(t["task_date"]))
                self._set_ops(r, int(t["id"]))
                self.table.resizeRowToContents(r)
                if t["status"] == "已完成":
                    done += 1
            total = len(tasks)
            rate = 0 if total == 0 else round(done / total * 100, 1)
            self.rate_label.setText(f"今日完成率：{rate}%")
        except Exception as exc:
            show_error(self, str(exc))

    def focus_task(self, task_id: int) -> None:
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.text() == str(task_id):
                self.table.selectRow(row)
                self.table.scrollToItem(item, QTableWidget.PositionAtCenter)
                return

    def add_task(self) -> None:
        dlg = DailyTaskDialog(self, {"task_date": today_str(), "status": "未开始"})
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
        if QMessageBox.question(self, "确认删除", "确定删除这条今日任务吗？") != QMessageBox.Yes:
            return
        try:
            self.task_service.delete_daily_task(task_id)
            self.refresh()
        except Exception as exc:
            show_error(self, str(exc))
