from __future__ import annotations

APP_FONT_FAMILY = 'Microsoft YaHei UI'
APP_FONT_FALLBACK = 'Segoe UI'
APP_BASE_FONT_SIZE = 13

COLORS = {
    'primary': '#2F80ED',
    'primary_hover': '#1F6FD6',
    'primary_pressed': '#1A5EB4',
    'primary_soft': '#E8F4FF',
    'background': '#F4FBF8',
    'surface': '#FFFFFF',
    'surface_muted': '#F3FBF7',
    'text': '#1F2937',
    'text_muted': '#6B7280',
    'text_weak': '#9CA3AF',
    'border': '#DCEEE6',
    'hover': '#EAF7F1',
    'success': '#14B86A',
    'success_soft': '#ECFDF3',
    'warning': '#F59E0B',
    'warning_soft': '#FFFBEB',
    'danger': '#DC2626',
    'danger_soft': '#FEF2F2',
    'disabled': '#D1D5DB',
}

SPACING = {
    'page_padding': 20,
    'section_gap': 16,
    'control_gap': 10,
    'card_padding': 16,
}

SIZES = {
    'window_width': 1200,
    'window_height': 780,
    'window_min_width': 1024,
    'window_min_height': 680,
    'nav_width': 220,
    'button_height': 34,
    'input_height': 34,
    'table_row_height': 40,
    'dialog_width': 520,
}

RADII = {
    'card': 12,
    'input': 8,
    'button': 8,
    'pill': 10,
}

STATUS_TEXT = {
    '未开始': '未开始',
    '进行中': '进行中',
    '已完成': '已完成',
    '已推迟': '已推迟',
    '已取消': '已取消',
    '已暂停': '已暂停',
    '已归档': '已归档',
}

STATUS_STYLE = {
    '未开始': ('#6B7280', '#F3F4F6'),
    '进行中': ('#2563EB', '#EAF1FF'),
    '已完成': ('#16A34A', '#ECFDF3'),
    '已推迟': ('#B45309', '#FFFBEB'),
    '已取消': ('#6B7280', '#F3F4F6'),
    '已暂停': ('#B45309', '#FFFBEB'),
    '已归档': ('#6B7280', '#F3F4F6'),
}

PRIORITY_STYLE = {
    '高': ('#B91C1C', '#FEF2F2'),
    '中': ('#1D4ED8', '#EAF1FF'),
    '低': ('#6B7280', '#F3F4F6'),
}

# NAV_ITEMS are defined in ui/texts.py to avoid scattered literals/encoding drift.
