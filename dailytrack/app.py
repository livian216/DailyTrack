from __future__ import annotations

import sys
import traceback

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QMessageBox

from dailytrack.config import load_path_config
from dailytrack.services.task_service import ServiceContainer
from dailytrack.ui.main_window import MainWindow
from dailytrack.ui.styles import build_app_stylesheet
from dailytrack.ui.theme import APP_BASE_FONT_SIZE, APP_FONT_FAMILY


def run() -> None:
    app = QApplication(sys.argv)
    app.setFont(QFont(APP_FONT_FAMILY, APP_BASE_FONT_SIZE))
    app.setStyleSheet(build_app_stylesheet())
    try:
        path_config = load_path_config()
        container = ServiceContainer.build(path_config)
        window = MainWindow(container)
        window.show()
        sys.exit(app.exec())
    except Exception as exc:
        QMessageBox.critical(None, '启动失败', f'{exc}\n\n{traceback.format_exc()}')
        raise
