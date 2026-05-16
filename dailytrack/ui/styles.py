from __future__ import annotations

from dailytrack.ui.theme import APP_BASE_FONT_SIZE, APP_FONT_FAMILY, APP_FONT_FALLBACK, COLORS, RADII, SIZES


def build_app_stylesheet() -> str:
    return f'''
    QWidget {{
        font-family: "{APP_FONT_FAMILY}", "{APP_FONT_FALLBACK}";
        font-size: {APP_BASE_FONT_SIZE}px;
        color: {COLORS['text']};
        background: {COLORS['background']};
    }}
    QLabel, QCheckBox, QRadioButton {{
        background: transparent;
    }}
    QMainWindow {{ background: {COLORS['background']}; }}

    QLabel[role="page-title"] {{
        font-size: 24px;
        font-weight: 700;
        color: {COLORS['text']};
    }}
    QLabel[role="page-subtitle"] {{
        font-size: 13px;
        color: {COLORS['text_muted']};
    }}

    QPushButton {{
        font-family: "{APP_FONT_FAMILY}", "{APP_FONT_FALLBACK}";
        min-height: {SIZES['button_height']}px;
        padding: 0 14px;
        border-radius: {RADII['button']}px;
        border: 1px solid transparent;
        background: {COLORS['primary']};
        color: #ffffff;
        font-weight: 600;
    }}
    QPushButton:hover {{ background: {COLORS['primary_hover']}; }}
    QPushButton:pressed {{ background: {COLORS['primary_pressed']}; }}
    QPushButton:disabled {{ background: {COLORS['disabled']}; color: #ffffff; }}

    QPushButton[variant="secondary"] {{
        background: {COLORS['surface']};
        color: {COLORS['text']};
        border: 1px solid {COLORS['border']};
    }}
    QPushButton[variant="secondary"]:hover {{ background: {COLORS['hover']}; }}

    QPushButton[variant="danger"] {{
        background: {COLORS['danger_soft']};
        color: {COLORS['danger']};
        border: 1px solid #fecaca;
    }}
    QPushButton[variant="danger"]:hover {{ background: #fee2e2; }}

    QLineEdit, QComboBox, QSpinBox, QDateEdit {{
        min-height: {SIZES['input_height']}px;
        border-radius: {RADII['input']}px;
        border: 1px solid {COLORS['border']};
        background: {COLORS['surface']};
        padding: 0 10px;
        selection-background-color: {COLORS['primary']};
    }}

    QPlainTextEdit, QTextEdit {{
        border-radius: {RADII['input']}px;
        border: 1px solid {COLORS['border']};
        background: {COLORS['surface']};
        padding: 8px;
        selection-background-color: {COLORS['primary']};
    }}

    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus, QPlainTextEdit:focus, QTextEdit:focus {{
        border: 1px solid {COLORS['primary']};
    }}

    QTableWidget {{
        font-family: "{APP_FONT_FAMILY}", "{APP_FONT_FALLBACK}";
        border-radius: {RADII['card']}px;
        border: 1px solid {COLORS['border']};
        background: {COLORS['surface']};
        gridline-color: transparent;
        alternate-background-color: {COLORS['surface_muted']};
    }}
    QHeaderView::section {{
        background: {COLORS['surface_muted']};
        border: none;
        border-bottom: 1px solid {COLORS['border']};
        color: {COLORS['text_muted']};
        font-weight: 700;
        padding: 8px;
    }}

    QProgressBar {{
        border: 1px solid {COLORS['border']};
        border-radius: {RADII['pill']}px;
        background: {COLORS['surface_muted']};
        text-align: center;
        color: {COLORS['text']};
        min-height: 16px;
    }}
    QProgressBar::chunk {{
        border-radius: {RADII['pill']}px;
        background: {COLORS['primary']};
    }}

    QFrame[card="true"] {{
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADII['card']}px;
    }}

    QDialog {{ background: {COLORS['background']}; }}

    QMenu {{
        font-family: "{APP_FONT_FAMILY}", "{APP_FONT_FALLBACK}";
        background: {COLORS['surface']};
        border: 1px solid {COLORS['border']};
        padding: 6px;
    }}
    QMenu::item {{
        padding: 6px 18px;
        border-radius: 6px;
    }}
    QMenu::item:selected {{
        background: {COLORS['hover']};
        color: {COLORS['text']};
    }}
    '''
