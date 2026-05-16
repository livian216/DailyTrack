# Development Notes (v1.1.0)

## 1. 当前版本概览
DailyTrack v1.1.0 已完成从 v1.0.0 到产品化 UI 的二阶段升级：
- 统一主题/样式/组件体系
- 任务卡片化与悬浮交互反馈
- 历史回看与归档检索页面
- SVG 图标与品牌 Logo 体系
- 文案与编码稳定性增强

## 2. 架构与分层
- `repositories/`：SQLite CRUD
- `services/`：业务规则与流程编排
- `ui/`：PySide6 界面、页面交互、卡片组件
- `utils/`：日期、文件、通用辅助
- 入口：`main.py -> dailytrack/app.py`

## 3. 关键行为约定
### 3.1 今日任务
- 今日待办主页面默认显示“未完成/进行中/已推迟”等活动任务。
- 状态为“已完成”的任务从今日待办主页面隐藏，但仍保留数据库记录，可在“任务回看”页面按日期查看。
- 点击“推迟到明天”时：
  - 原任务状态更新为“已推迟”（仍属于原日期）
  - 自动在次日复制一条“未开始”任务

### 3.2 长线任务
- 主页面默认显示非归档长线任务。
- 状态为“已归档”的任务从主页面隐藏，进入“归档任务”页面查看与搜索。

### 3.3 历史与归档页面
- `任务回看`：手动输入 `YYYY-MM-DD` 查询当日任务。
- `归档任务`：按标题关键词检索归档长线任务。

## 4. UI 与资源约定
### 4.1 图标策略
- 统一使用本地 SVG：`dailytrack/ui/resources/icons/`
- 导航图标、品牌 Logo、窗口图标都从该目录加载。

### 4.2 卡片交互
- 卡片内部不额外加重边框装饰。
- 通过“状态彩带 + 选中悬浮阴影”表达层级与焦点。

### 4.3 文案管理
- 集中在 `dailytrack/ui/texts.py`，避免页面散落字符串造成编码漂移。

## 5. 打包与安装
### 5.1 EXE 打包
- 使用 `scripts/build_exe.bat`
- 关键参数包含：
  - `--add-data "dailytrack\ui\resources\icons;dailytrack\ui\resources\icons"`
  - `--hidden-import PySide6.QtSvg`
  - `--hidden-import PySide6.QtSvgWidgets`

### 5.2 安装包打包
- 使用 `scripts/build_installer.bat`
- 安装器脚本：`installer/DailyTrack.iss`
- 当前版本产物名：`DailyTrack_Setup_v1.1.0.exe`

### 5.3 常见打包风险
- `WinError 5`（资源写入失败）：通常是 `DailyTrack.exe` 被占用，需关闭进程后重试。
- 安装器编译报错：需检查 `DailyTrack.iss` 字符串与编码是否完整。

## 6. 清理策略
- 默认清理：`scripts/clean_build.bat`
  - 清理 `build`、`__pycache__`、`*.pyc`、`*.spec`、测试临时文件
  - 保留 `dist` 与 `installer_output`
- 全量清理：`scripts/clean_build.bat --all`
  - 在默认基础上清理 `dist` 与 `installer_output`

## 7. 后续建议
- 增加打包后自动校验资源存在的步骤（例如检查 `dist\DailyTrack\dailytrack\ui\resources\icons`）。
- 增加轻量 UI 回归清单（导航图标、Logo、卡片交互、历史页检索）。
