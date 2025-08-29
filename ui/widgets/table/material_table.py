from PyQt5.QtWidgets import (
    QTableWidget,
    QHeaderView,
)
from utils.constants import COLORS


class MaterialTable(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        # Table styling
        self.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                alternate-background-color: {COLORS['surface_variant']};
                border: none;
                border-radius: 8px;
                gridline-color: {COLORS['outline']};
                font-family: "Segoe UI";
                font-size: 10pt;
                color: {COLORS['on_surface']};
            }}
                   
            QTableWidget::item {{
                padding: 12px 16px;
                border: none;
                border-bottom: 1px solid {COLORS['outline']};
            }}
            
            QTableWidget::item:selected {{
                background-color: {COLORS['primary_light']};
                color: white;
            }}
            
            QTableWidget::item:hover {{
                background-color: {COLORS['surface_variant']};
            }}
            
            QHeaderView::section {{
                background-color: {COLORS['surface']};
                color: {COLORS['on_surface']};
                font-weight: 600;
                font-size: 11pt;
                border: none;
                border-bottom: 2px solid {COLORS['primary']};
                padding: 16px;
                text-align: left;
            }}
            
            QHeaderView::section:horizontal {{
                border-right: 1px solid {COLORS['outline']};
            }}
            
            QScrollBar:vertical {{
                background-color: {COLORS['surface_variant']};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            
            QScrollBar::handle:vertical {{
                background-color: {COLORS['primary']};
                border-radius: 6px;
                min-height: 30px;
                margin: 2px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background-color: {COLORS['primary']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
        """
        )

        # Table behavior
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QTableWidget.SingleSelection)
        self.setSortingEnabled(True)
        self.setShowGrid(False)

        # Header configuration
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
