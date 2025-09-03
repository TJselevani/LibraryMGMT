from PyQt5.QtWidgets import (
    QPushButton,
    QGraphicsDropShadowEffect,
)
from utils.constants import COLORS
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve


# Custom Material Design Button
class MaterialButton(QPushButton):
    def __init__(self, text="", icon="", button_type="elevated", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.icon_text = icon
        self.setup_ui()
        self.setup_animation()

    def setup_ui(self):
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 9, QFont.Medium))

        if self.button_type == "elevated":
            self.setStyleSheet(
                f"""
                MaterialButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 24px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1.25px;
                }}
                MaterialButton:hover {{
                    background-color: {COLORS['primary_dark']};
                }}
                MaterialButton:pressed {{
                    background-color: {COLORS['primary_dark']};
                }}
            """
            )
        elif self.button_type == "outlined":
            self.setStyleSheet(
                f"""
                MaterialButton {{
                    background-color: transparent;
                    color: {COLORS['primary']};
                    border: 1px solid {COLORS['primary']};
                    border-radius: 20px;
                    padding: 8px 24px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1.25px;
                }}
                MaterialButton:hover {{
                    background-color: rgba(25, 118, 210, 0.08);
                }}
            """
            )
        elif self.button_type == "text":
            self.setStyleSheet(
                f"""
                MaterialButton {{
                    background-color: transparent;
                    color: {COLORS['primary']};
                    border: none;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1.25px;
                }}
                MaterialButton:hover {{
                    background-color: rgba(25, 118, 210, 0.08);
                }}
            """
            )

        # Add shadow effect for elevated buttons
        if self.button_type == "elevated":
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 60))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)

    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
