from utils.constants import COLORS
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLineEdit


class MaterialLineEdit(QLineEdit):
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(48)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            f"""
            MaterialLineEdit {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['outline']};
                border-radius: 8px;
                padding: 12px 16px;
                color: {COLORS['on_surface']};
            }}
            MaterialLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
                background-color: {COLORS['surface']};
            }}
            MaterialLineEdit::placeholder {{
                color: {COLORS['on_surface_variant']};
            }}
        """
        )
