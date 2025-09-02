from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from utils.constants import COLORS


class MaterialWidget(QWidget):
    """Base widget with material design principles"""

    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.apply_material_style()

    def setup_ui(self):
        """Override to setup widget UI"""
        pass

    def apply_material_style(self):
        """Apply material design styling"""
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {COLORS.get('surface', '#ffffff')};
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )

    def show_error(self, message: str):
        """Show error message"""
        self.error_occurred.emit(message)
