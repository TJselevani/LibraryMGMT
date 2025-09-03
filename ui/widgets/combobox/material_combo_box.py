from utils.constants import COLORS
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QComboBox


class MaterialComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setMinimumHeight(48)
        self.setFont(QFont("Segoe UI", 10))
        self.setStyleSheet(
            f"""
            MaterialComboBox {{
                background-color: {COLORS['surface']};
                border: 2px solid {COLORS['outline']};
                border-radius: 8px;
                padding: 12px 16px;
                color: {COLORS['on_surface']};
            }}
            MaterialComboBox:focus {{
                border: 2px solid {COLORS['primary']};
            }}
            MaterialComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            MaterialComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['on_surface_variant']};
                margin-right: 10px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['outline']};
                border-radius: 8px;
                selection-background-color: {COLORS['primary_light']};
                padding: 8px;
            }}
        """
        )
