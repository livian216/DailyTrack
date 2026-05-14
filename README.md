# DailyTrack

DailyTrack 是一款面向个人用户的 Windows 本地任务管理软件，聚焦“今日执行 + 长线推进 + 每日复盘”的闭环。

适合需要在本地持续追踪工作、学习、写作、项目推进进度的用户使用。

## 产品定位

- 本地单机：不依赖云端账号，不强制联网
- 轻量稳定：基于 Python + PySide6 + SQLite
- 可安装即用：提供 Windows 安装包，普通用户无需安装 Python
- 数据可控：支持自定义数据目录、导出与备份

## 核心功能

### 1. 首页总览
- 今日任务总数、已完成、未完成、高优先级未完成统计卡片
- 今日完成率进度条
- 三类看板：
  - 高优先级未完成
  - 7天内到期任务
  - 已逾期任务
- 看板任务支持双击跳转到对应页面定位查看

### 2. 今日待办
- 新增 / 编辑 / 完成 / 推迟到明天 / 删除
- 支持优先级、状态、预计耗时（小时+分钟）、备注
- 长文本支持悬停 tooltip 查看完整内容

### 3. 长线任务
- 新增 / 编辑 / 归档 / 删除
- 进度、开始日期、截止日期、逾期识别
- 从长线任务生成今日任务
- 阶段管理（增改删）
- 进展日志（查看历史 + 新增）

### 4. 每日复盘
- 指定日期查看当日任务完成统计
- 保存：今日总结、未完成原因、明日重点
- 输入日期快速回看历史复盘

### 5. 设置与数据
- 查看当前数据目录与数据库路径
- 自定义数据目录迁移（支持迁移后清理旧目录）
- 导出 JSON / CSV
- 备份数据库

## 技术栈

- Python 3
- PySide6
- SQLite（sqlite3）
- PyInstaller
- Inno Setup

## 项目结构

```text
DailyTrack/
├── main.py
├── requirements.txt
├── dailytrack/
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── repositories/
│   ├── services/
│   └── ui/
├── scripts/
│   ├── setup_env.bat
│   ├── run_dev.bat
│   ├── build_exe.bat
│   ├── build_installer.bat
│   └── clean_build.bat
├── installer/
│   └── DailyTrack.iss
└── docs/
```

## 快速开始（开发者）

### 1) 创建环境并安装依赖

```bat
scripts\setup_env.bat
```

### 2) 启动开发版

```bat
scripts\run_dev.bat
```

## 打包发布

### 1) 生成可执行目录（one-folder）

```bat
scripts\build_exe.bat
```

产物目录：

```text
dist\DailyTrack\
```

### 2) 生成安装包（需已安装 Inno Setup）

```bat
scripts\build_installer.bat
```

安装包输出：

```text
installer_output\DailyTrack_Setup_v1.0.0.exe
```

## 普通用户安装方式

1. 双击 `DailyTrack_Setup_v1.0.0.exe`
2. 按安装向导完成安装
3. 双击桌面 `DailyTrack` 图标
4. 开始使用

## 数据与隐私

- 用户数据默认保存在 `%APPDATA%\DailyTrack\`
- 支持迁移到自定义目录
- 卸载软件默认不删除用户数据目录
- 建议卸载前先在软件内导出 JSON/CSV 并备份数据库

## 常见问题

### Q1: `ISCC.exe not found`
请安装 Inno Setup，并将 `ISCC.exe` 所在目录加入 PATH。

### Q2: 切换数据目录后看不到数据
请确认迁移成功提示并重启软件后再检查。

### Q3: 文本太长显示不全
可将鼠标悬停在单元格上查看完整内容 tooltip。
