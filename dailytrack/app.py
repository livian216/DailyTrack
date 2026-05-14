from __future__ import annotations

import sys
import traceback

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from dailytrack.config import load_path_config
from dailytrack.services.task_service import ServiceContainer
from dailytrack.ui.main_window import MainWindow


def _build_stylesheet() -> str:
    return """
    QWidget {
        font-family: "Microsoft YaHei UI";
        font-size: 13px;
        color: #1f2937;
        background: #f4f6f8;
    }
    QMainWindow {
        background: #f4f6f8;
    }
    QListWidget {
        border: 1px solid #dbe1e7;
        border-radius: 8px;
        background: #ffffff;
    }
    QListWidget::item {
        padding: 10px 12px;
        border-radius: 6px;
    }
    QListWidget::item:selected {
        background: #e6f0ff;
        color: #0f4fa8;
        font-weight: 600;
    }
    QPushButton {
        background: #1f6feb;
        color: #ffffff;
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
        font-weight: 600;
    }
    QPushButton:hover { background: #195dc6; }
    QPushButton:pressed { background: #124da7; }
    QLineEdit, QPlainTextEdit, QTableWidget, QGroupBox, QProgressBar {
        background: #ffffff;
    }
    QTableWidget {
        gridline-color: #e5e7eb;
        border: 1px solid #dbe1e7;
        border-radius: 8px;
    }
    QHeaderView::section {
        background: #eef3f8;
        color: #223047;
        border: none;
        border-bottom: 1px solid #dbe1e7;
        padding: 8px;
        font-weight: 700;
    }
    """


def run() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont("Microsoft YaHei UI", 10))
    app.setStyleSheet(_build_stylesheet())
    try:
        path_config = load_path_config()
        container = ServiceContainer.build(path_config)
        window = MainWindow(container)
        window.show()
        sys.exit(app.exec())
    except Exception as exc:
        QMessageBox.critical(None, "启动失败", f"{exc}\n\n{traceback.format_exc()}")
        raise
