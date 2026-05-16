from __future__ import annotations

# Centralized UI copy to avoid encoding drift and scattered literals.
APP_SUBTITLE = '每日计划与长线任务跟踪'
VERSION_LABEL = '版本'

PAGE_DASHBOARD = '今天概览'
PAGE_DAILY = '今日待办'
PAGE_LONG = '长线任务'
PAGE_REVIEW = '每日复盘'
PAGE_SETTINGS = '设置/数据'
PAGE_DAILY_HISTORY = '任务回看'
PAGE_LONG_ARCHIVE = '归档任务'

BTN_REFRESH_STATS = '刷新统计'
BTN_REFRESH_LIST = '刷新列表'
BTN_ADD_DAILY = '新增今日任务'
BTN_ADD_LONG = '新增长线任务'
BTN_ACTION = '操作'
BTN_EDIT = '编辑'
BTN_DONE = '完成'
BTN_POSTPONE = '推迟到明天'
BTN_DELETE = '删除'
BTN_SAVE = '保存'
BTN_CANCEL = '取消'

BOARD_HIGH = '高优先级未完成'
BOARD_UPCOMING = '7天内到期任务'
BOARD_OVERDUE = '已逾期任务'

NAV_ITEMS = [
    (PAGE_DASHBOARD, 'home'),
    (PAGE_DAILY, 'today'),
    (PAGE_LONG, 'target'),
    (PAGE_DAILY_HISTORY, 'history'),
    (PAGE_LONG_ARCHIVE, 'archive'),
    (PAGE_REVIEW, 'review'),
    (PAGE_SETTINGS, 'settings'),
]
