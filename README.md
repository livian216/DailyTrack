# DailyTrack v1.1.1

DailyTrack 是一款面向个人用户的 Windows 本地任务管理软件，围绕“今日执行 + 长线推进 + 复盘沉淀”构建闭环。

## 产品定位
- 本地单机：不依赖云端账号，不强制联网。
- 轻量稳定：`Python + PySide6 + SQLite`。
- 可安装即用：支持打包与安装，不要求用户安装 Python。
- 数据可控：支持数据目录迁移、导出、备份。

## v1.1.1 关键升级
- 安装升级优化：新版安装包可检测旧版并自动触发卸载后继续安装。
- 安装过程稳健性：支持安装阶段尝试关闭运行中旧版进程，降低文件占用导致的失败概率。
- 数据目录配置持久化：数据路径配置统一落盘到 `%APPDATA%\\DailyTrackConfig\\app_config.json`。
- 兼容迁移：若检测到旧版安装目录中的 `app_config.json`，会自动迁移到新配置位置。

## 核心功能
### 1) 今天概览
- 今日任务统计卡片（总数、已完成、未完成、完成率）
- 今日完成进度
- 看板分区（高优先级未完成、7 天内到期、已逾期）

### 2) 今日待办
- 新增/编辑/完成/推迟到明天/删除
- 任务卡片展示：状态彩带、标签语义、元信息、快捷操作

### 3) 长线任务
- 新增/编辑/归档/删除
- 进度、开始/截止日期、剩余天数、逾期提示
- 可生成今日任务
- 阶段管理与进展日志（卡片化展示）

### 4) 任务回看
- 手动输入日期（`YYYY-MM-DD`）查询当日任务
- 历史任务卡片展示与选中反馈

### 5) 归档任务
- 回看已归档长线任务
- 按标题关键词搜索

### 6) 每日复盘
- 按日期加载记录
- 保存今日总结、未完成原因、明日重点

### 7) 设置/数据
- 查看并迁移数据目录
- 导出 JSON/CSV
- 备份数据库

## 项目结构
```text
DailyTrack/
├─ main.py
├─ requirements.txt
├─ dailytrack/
├─ scripts/
├─ installer/
└─ docs/
```

## 开发启动
```bat
scripts\setup_env.bat
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

### 2) 生成安装包（Inno Setup）
```bat
scripts\build_installer.bat
```
安装包输出：
```text
installer_output\DailyTrack_Setup_v1.1.1.exe
```

## 数据与隐私
- 默认数据目录：`%APPDATA%\DailyTrack\`
- 路径配置文件：`%APPDATA%\DailyTrackConfig\app_config.json`
- 卸载默认不删除用户数据目录
- 建议卸载前先导出 JSON/CSV 并备份数据库

## 升级说明（v1.1.1）
- 同一 `AppId` 下，新版安装时会检测旧版并自动卸载再安装。
- 若自动卸载失败或被取消，安装将中止并提示先手动卸载，避免半升级状态。
- 升级/重装后，软件将优先读取 `%APPDATA%\DailyTrackConfig\app_config.json`，减少“自定义目录丢失”问题。

## 常见问题
### Q1: 安装后左侧图标/Logo 不显示
请确认使用最新 `build_exe.bat` 打包（已包含 SVG 资源收集参数）。

### Q2: `ISCC.exe not found`
请安装 Inno Setup，并将 `ISCC.exe` 所在目录加入 `PATH`。

### Q3: 打包时出现 `WinError 5`
通常是目标 EXE 被占用。请关闭所有 `DailyTrack.exe` 后重试。
