from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QGraphicsDropShadowEffect,
)
from utils.constants import COLORS
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt


# Material Design Card
class MaterialCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(
            f"""
            MaterialCard {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['outline']};
            }}
        """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


# Material Design Stat Card
class MaterialStatCard(MaterialCard):
    def __init__(self, title, value, icon="", color=COLORS["primary"]):
        super().__init__()
        self.setup_content(title, value, icon, color)

    def setup_content(self, title, value, icon, color):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        # Icon and value row
        top_row = QHBoxLayout()

        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 24))
            icon_label.setStyleSheet(f"color: {color};")
            top_row.addWidget(icon_label)

        top_row.addStretch()

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['on_surface']};")
        value_label.setAlignment(Qt.AlignRight)
        top_row.addWidget(value_label)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet(f"color: {COLORS['on_surface_variant']};")

        layout.addLayout(top_row)
        layout.addWidget(title_label)
        self.setLayout(layout)
