from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    # QTableWidgetItem,
    # QHeaderView,
)

# from PyQt5.QtGui import QFont, QColor
from ui.widgets.table.material_table import MaterialTable
from ui.widgets.TextField.material_line_edit import MaterialLineEdit
from ui.widgets.combobox.material_combo_box import MaterialComboBox
from utils.constants import COLORS


class EntityView(QWidget):
    def __init__(self, controller, search_placeholder="Search...", filters=None):
        super().__init__()
        self.controller = controller
        self.search_placeholder = search_placeholder
        self.filters = filters or ["All"]

        self.data = []
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)

        # --- Search + Filter ---
        search_frame = QFrame()
        search_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 8px;
                border: 1px solid {COLORS['outline']};
                padding: 16px;
            }}
        """
        )
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(10, 10, 10, 10)
        search_layout.setSpacing(16)

        self.search_input = MaterialLineEdit(self.search_placeholder)
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_table)

        self.filter_combo = MaterialComboBox()
        self.filter_combo.addItems(self.filters)
        self.filter_combo.setFixedWidth(150)
        self.filter_combo.currentTextChanged.connect(self.filter_table)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.filter_combo)
        search_layout.addStretch()
        layout.addWidget(search_frame)

        # --- Table ---
        self.table = MaterialTable()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.table, stretch=1)

    def load_data(self):
        """Fetch all data from the controller"""
        self.data = self.controller.get_all()
        self.populate_table(self.data)

    def populate_table(self, items):
        """Implemented by subclasses to define headers + row formatting"""
        raise NotImplementedError

    def filter_table(self):
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentText()
        filtered = []

        for item in self.data:
            if self.matches_search(item, search_text) and self.matches_filter(
                item, filter_type
            ):
                filtered.append(item)

        self.populate_table(filtered)

    def matches_search(self, item, text):
        """Override per-entity for searchable fields"""
        return True if not text else False

    def matches_filter(self, item, filter_type):
        """Override per-entity for filter logic"""
        return True
