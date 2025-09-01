from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtGui import QFont, QColor  # , QPalette

# from PyQt5.QtCore import Qt
from controllers.patrons_controller import PatronsController
from ui.widgets.table.material_table import MaterialTable
from ui.widgets.TextField.material_line_edit import MaterialLineEdit
from ui.widgets.combobox.material_combo_box import MaterialComboBox
from utils.constants import COLORS


class PatronsView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.patrons_controller = PatronsController(db_manager)
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Search and filter section
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

        # Search input
        self.search_input = MaterialLineEdit("Search users...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_table)

        # Filter dropdown
        self.filter_combo = MaterialComboBox()
        self.filter_combo.addItems(["All Users", "MALE", "FEMALE", "Recent"])
        self.filter_combo.setFixedWidth(150)
        self.filter_combo.currentTextChanged.connect(self.filter_table)

        # Add to layout
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.filter_combo)
        search_layout.addStretch()

        layout.addWidget(search_frame)

        # Table
        self.table = MaterialTable()

        # Make the table expand vertically
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Add with stretch factor = 1 so it takes all remaining space
        layout.addWidget(self.table, stretch=1)

    def load_users(self):
        users = self.patrons_controller.get_all()
        self.users_data = users  # Store for filtering
        self.populate_table(users)

    def populate_table(self, users):
        self.table.setRowCount(len(users))
        self.table.setColumnCount(14)

        headers = [
            "Patron ID",
            "First Name",
            "Last Name",
            "Gender",
            "DOB",
            "Institution",
            "Grade",
            "Residence",
            "Phone",
            "Membership Status",
            "Membership Type",
            "Start Date",
            "Expiry Date",
            "Borrowed Books",
        ]
        self.table.setHorizontalHeaderLabels(headers)

        header = self.table.horizontalHeader()
        for i in range(len(headers)):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

        for row_idx, user in enumerate(users):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(user.patron_id)))
            self.table.setItem(row_idx, 1, QTableWidgetItem(user.first_name or ""))
            self.table.setItem(row_idx, 2, QTableWidgetItem(user.last_name or ""))
            self.table.setItem(row_idx, 3, QTableWidgetItem(user.gender or ""))
            self.table.setItem(
                row_idx,
                4,
                QTableWidgetItem(
                    str(user.date_of_birth) if user.date_of_birth else "N/A"
                ),
            )
            self.table.setItem(row_idx, 5, QTableWidgetItem(user.institution or "N/A"))
            self.table.setItem(row_idx, 6, QTableWidgetItem(user.grade_level or "N/A"))
            self.table.setItem(row_idx, 7, QTableWidgetItem(user.residence or "N/A"))
            self.table.setItem(row_idx, 8, QTableWidgetItem(user.phone_number or "N/A"))

            # Membership Status
            membership = (
                user.membership_status.value if user.membership_status else "Unknown"
            )
            membership_item = QTableWidgetItem(membership)
            if membership == "active":
                membership_item.setForeground(QColor(COLORS["success"]))
                membership_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            elif membership == "inactive":
                membership_item.setForeground(QColor(COLORS["error"]))
            elif membership == "expired":
                membership_item.setForeground(QColor(COLORS["warning"]))
            self.table.setItem(row_idx, 9, membership_item)

            # Membership Type
            self.table.setItem(
                row_idx, 10, QTableWidgetItem(user.membership_type or "N/A")
            )

            # Membership Start & Expiry
            self.table.setItem(
                row_idx,
                11,
                QTableWidgetItem(
                    str(user.membership_start_date)
                    if user.membership_start_date
                    else "N/A"
                ),
            )
            self.table.setItem(
                row_idx,
                12,
                QTableWidgetItem(
                    str(user.membership_expiry_date)
                    if user.membership_expiry_date
                    else "N/A"
                ),
            )

            # Borrowed Books (titles)
            borrowed_titles = (
                ", ".join(b.book.title for b in user.borrowed_books) or "None"
            )
            self.table.setItem(row_idx, 13, QTableWidgetItem(borrowed_titles))

        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 50)

    def filter_table(self):
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentText()

        filtered_users = []

        for user in self.users_data:
            # Apply search filter
            if search_text:
                searchable_text = f"{user.first_name} {user.last_name} {user.gender}  {user.phone_number or ''} {user.institution or ''}".lower()
                if search_text not in searchable_text:
                    continue

            # Apply membership filter
            if filter_type != "All Users":
                membership = user.membership_status or ""
                if filter_type == "Active" and membership != "active":
                    continue
                elif filter_type == "Inactive" and membership != "inactive":
                    continue
                elif filter_type == "Recent" and membership not in ["pending", "new"]:
                    continue

            filtered_users.append(user)

        # Repopulate table with filtered data
        self.populate_table(filtered_users)
