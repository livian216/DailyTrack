from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QVBoxLayout, QWidget

from dailytrack.config import APP_VERSION, DEFAULT_DATA_ROOT, PathConfig
from dailytrack.services.backup_service import BackupService
from dailytrack.services.export_service import ExportService
from dailytrack.services.path_service import PathService
from dailytrack.services.task_service import ServiceContainer
from dailytrack.ui.components import ActionButton, PageHeader, SectionCard, SecondaryButton
from dailytrack.ui.texts import PAGE_SETTINGS


class SettingsPage(QWidget):
    def __init__(self, container_provider):
        super().__init__()
        self.container_provider = container_provider
        self.backup = BackupService()

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 20, 20, 20)
        root.setSpacing(14)

        header = PageHeader(PAGE_SETTINGS, '管理数据路径、导出与备份')
        root.addWidget(header)

        self.path_card = SectionCard('数据位置')
        self.path_label = QLabel('')
        self.path_label.setWordWrap(True)
        self.db_label = QLabel('')
        self.db_label.setWordWrap(True)
        self.select_btn = ActionButton('选择新数据目录（迁移并清理旧目录）')
        self.reset_btn = SecondaryButton('恢复默认数据目录（迁移并清理旧目录）')
        self.open_btn = SecondaryButton('打开数据目录')
        for w in [self.path_label, self.db_label, self.select_btn, self.reset_btn, self.open_btn]:
            self.path_card.body_layout.addWidget(w)
        root.addWidget(self.path_card)

        self.export_card = SectionCard('数据导出')
        self.export_json_btn = ActionButton('导出全部 JSON')
        self.export_csv_btn = SecondaryButton('导出 CSV')
        self.export_card.body_layout.addWidget(self.export_json_btn)
        self.export_card.body_layout.addWidget(self.export_csv_btn)
        root.addWidget(self.export_card)

        self.backup_card = SectionCard('数据备份')
        self.backup_btn = ActionButton('备份数据库')
        self.backup_card.body_layout.addWidget(self.backup_btn)
        root.addWidget(self.backup_card)

        self.info_card = SectionCard('软件信息')
        self.version_label = QLabel(f'软件版本：v{APP_VERSION}')
        self.info_note = QLabel('DailyTrack 为本地单机任务管理软件，数据仅保存在你的设备中。')
        self.info_note.setWordWrap(True)
        self.info_card.body_layout.addWidget(self.version_label)
        self.info_card.body_layout.addWidget(self.info_note)
        root.addWidget(self.info_card)
        root.addStretch()

        self.select_btn.clicked.connect(self.select_root)
        self.reset_btn.clicked.connect(self.reset_root)
        self.open_btn.clicked.connect(self.open_dir)
        self.backup_btn.clicked.connect(self.do_backup)
        self.export_json_btn.clicked.connect(self.export_json)
        self.export_csv_btn.clicked.connect(self.export_csv)
        self.refresh_labels()

    def _container(self) -> ServiceContainer:
        return self.container_provider()

    def refresh_labels(self) -> None:
        c = self._container()
        self.path_label.setText(f'当前数据目录：\n{c.db.path_config.data_root}')
        self.db_label.setText(f'数据库路径：\n{c.db.db_path}')

    def refresh(self) -> None:
        self.refresh_labels()

    def _switch(self, new_root: Path) -> None:
        c = self._container()
        result = PathService(c.db.path_config).switch_data_root(new_root, cleanup_old_root=True)
        self.container_provider(reload_from=PathConfig(data_root=new_root))
        clean_msg = '旧目录已清理（迁移完成）。' if result.cleaned_old_root else '旧目录清理失败，请手动检查旧目录。'
        QMessageBox.information(self, '完成', f'路径已切换并迁移完成。\n{clean_msg}\n请重启软件以确保所有页面使用新路径。')
        self.refresh_labels()

    def select_root(self) -> None:
        path = QFileDialog.getExistingDirectory(self, '选择数据目录')
        if not path:
            return
        msg = (
            '将执行以下操作：\n'
            '1. 把当前目录数据迁移到新目录\n'
            '2. 尝试清理旧目录（剪切效果）\n'
            '3. 保存新路径并提示重启\n\n'
            '是否继续？'
        )
        if QMessageBox.question(self, '确认切换', msg) == QMessageBox.Yes:
            try:
                self._switch(Path(path))
            except Exception as e:
                QMessageBox.critical(self, '错误', f'切换失败：{e}')

    def reset_root(self) -> None:
        msg = (
            '将恢复默认目录并执行迁移：\n'
            '1. 迁移当前数据到默认目录\n'
            '2. 尝试清理旧目录（剪切效果）\n\n'
            '是否继续？'
        )
        if QMessageBox.question(self, '确认恢复默认', msg) != QMessageBox.Yes:
            return
        try:
            self._switch(DEFAULT_DATA_ROOT)
        except Exception as e:
            QMessageBox.critical(self, '错误', f'恢复失败：{e}')

    def open_dir(self) -> None:
        try:
            os.startfile(str(self._container().db.path_config.data_root))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开目录失败：{e}')

    def do_backup(self) -> None:
        c = self._container()
        try:
            out = self.backup.create_backup(c.db.db_path, c.db.path_config.backups_dir)
            QMessageBox.information(self, '成功', f'备份成功：{out}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'备份失败：{e}')

    def export_json(self) -> None:
        c = self._container()
        try:
            out = ExportService(c).export_json(c.db.path_config.exports_dir)
            QMessageBox.information(self, '成功', f'导出成功：{out}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败：{e}')

    def export_csv(self) -> None:
        c = self._container()
        try:
            files = ExportService(c).export_csv(c.db.path_config.exports_dir)
            QMessageBox.information(self, '成功', '导出成功：\n' + '\n'.join([str(x) for x in files]))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出失败：{e}')
