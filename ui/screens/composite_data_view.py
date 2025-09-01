import csv
import json
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidgetItem,
    QHeaderView,
    QFrame,
    QSizePolicy,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import pyqtSignal
from datetime import datetime

from controllers.patrons_controller import PatronsController
from controllers.books_controller import BooksController
from controllers.borrowed_books_controller import BorrowedBooksController
from controllers.payments_controller import PaymentController
from controllers.users_controller import UsersController

from ui.widgets.table.material_table import MaterialTable
from ui.widgets.TextField.material_line_edit import MaterialLineEdit
from ui.widgets.combobox.material_combo_box import MaterialComboBox
from ui.widgets.buttons.material_button import MaterialButton
from ui.widgets.section.material_section import MaterialSection
from utils.constants import COLORS


class CompositeDataView(QWidget):
    # Signal to communicate with parent when add button is clicked
    add_requested = pyqtSignal(str)  # Emits the current view type

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager

        # Initialize controllers
        self.patrons_controller = PatronsController(db_manager)
        self.books_controller = BooksController(db_manager)
        self.borrowed_books_controller = BorrowedBooksController(db_manager)
        self.payment_controller = PaymentController(db_manager)
        self.users_controller = UsersController(db_manager)

        # Current view state
        self.current_view = "Users"
        self.view_configs = {
            "Users": {
                "title": "Users Management",
                "subtitle": "Manage library staff and administrators.",
                "headers": ["ID", "Username", "Email", "Phone", "Role", "Active"],
                "filters": ["All Users", "Active", "Inactive", "Admins", "Staff"],
                "data_key": "users_data",
            },
            "Patrons": {
                "title": "Patrons Management",
                "subtitle": "Manage library members and their information.",
                "headers": [
                    "Patron ID",
                    "First Name",
                    "Last Name",
                    "Gender",
                    "DOB",
                    "Institution",
                    "Grade",
                    "Residence",
                    "Phone",
                    "Membership",
                ],
                "filters": ["All Patrons", "Active", "Inactive", "Recent", "Students"],
                "data_key": "patrons_data",
            },
            "Books": {
                "title": "Books Management",
                "subtitle": "Manage library book inventory and catalog.",
                "headers": [
                    "Book ID",
                    "Title",
                    "Author",
                    "Accession No.",
                    "ISBN",
                    "Category",
                    "Status",
                    "Location",
                ],
                "filters": [
                    "All Books",
                    "Available",
                    "Borrowed",
                    "Reserved",
                    "Damaged",
                ],
                "data_key": "books_data",
            },
            "Borrowed Books": {
                "title": "Borrowed Books Management",
                "subtitle": "Track and manage book borrowing activities.",
                "headers": [
                    "Borrow ID",
                    "User ID",
                    "Book ID",
                    "Book Title",
                    "Borrow Date",
                    "Due Date",
                    "Return Date",
                    "Status",
                ],
                "filters": ["All Borrows", "Active", "Overdue", "Returned", "Today"],
                "data_key": "borrowed_books_data",
            },
            "Payments": {
                "title": "Payments Management",
                "subtitle": "Track membership fees and penalty payments.",
                "headers": [
                    "Payment ID",
                    "User ID",
                    "User Name",
                    "Type",
                    "Amount",
                    "Date",
                    "Status",
                ],
                "filters": [
                    "All Payments",
                    "Membership",
                    "Penalties",
                    "Recent",
                    "Pending",
                ],
                "data_key": "payments_data",
            },
        }

        # Data storage
        self.users_data = []
        self.patrons_data = []
        self.books_data = []
        self.borrowed_books_data = []
        self.payments_data = []

        self.setup_ui()
        self.load_all_data()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        self.setLayout(layout)

        # Title + Navigation buttons (in one row)
        title_layout = QHBoxLayout()

        self.title_label = QLabel("Library Data Management")
        self.title_label.setFont(QFont("Segoe UI", 32, QFont.Light))
        self.title_label.setStyleSheet(
            f"color: {COLORS['on_surface']}; margin-bottom: 8px;"
        )
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()

        # Create view selector buttons (inline with title)
        self.create_view_selector(title_layout)

        layout.addLayout(title_layout)

        # Subtitle
        self.subtitle_label = QLabel(
            "Manage all core library data: users, patrons, books, and transactions."
        )
        self.subtitle_label.setFont(QFont("Segoe UI", 14))
        self.subtitle_label.setStyleSheet(
            f"color: {COLORS['on_surface_variant']}; margin-bottom: 24px;"
        )
        layout.addWidget(self.subtitle_label)

        # Action buttons
        self.create_action_buttons(layout)

        # Search and filter section
        self.create_search_section(layout)

        # Table section
        self.create_table_section(layout)

        # Initialize with Users view
        self.update_view_content()

    def create_view_selector(self, layout):
        """Create inline navigation buttons (styled like tabs)"""

        self.view_buttons = {}
        view_names = ["Users", "Patrons", "Books", "Payments", "Borrowed Books"]

        for view_name in view_names:
            btn = MaterialButton(view_name, button_type="text")
            btn.setFont(QFont("Segoe UI", 12))
            btn.setCheckable(True)

            # Default inactive style (muted text)
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    color: {COLORS['on_surface_variant']};
                    font-weight: 500;
                    border-radius: 6px;
                    padding: 6px 12px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS.get('surface_variant', '#f0f0f0')};
                }}
                QPushButton:checked {{
                    color: {COLORS['primary']};
                    background-color: {COLORS.get('primary_container', COLORS['surface_variant'])};
                    font-weight: 600;
                }}
            """
            )

            btn.clicked.connect(lambda checked, name=view_name: self.switch_view(name))
            self.view_buttons[view_name] = btn
            layout.addWidget(btn)

        # Set Users as default active
        self.view_buttons["Users"].setChecked(True)

    def create_action_buttons(self, layout):
        """Create the action buttons section"""
        actions_layout = QHBoxLayout()

        self.add_btn = MaterialButton("Add New Item", button_type="elevated")
        self.import_btn = MaterialButton("Import Data", button_type="outlined")
        self.export_btn = MaterialButton("Export Data", button_type="outlined")

        # Connect import/export buttons
        self.import_btn.clicked.connect(self.import_data)
        self.export_btn.clicked.connect(self.export_data)

        # Connect add button to signal
        self.add_btn.clicked.connect(lambda: self.add_requested.emit(self.current_view))

        actions_layout.addWidget(self.add_btn)
        actions_layout.addWidget(self.import_btn)
        actions_layout.addWidget(self.export_btn)
        actions_layout.addStretch()

        layout.addLayout(actions_layout)

    def create_search_section(self, layout):
        """Create the search and filter section"""
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
        self.search_input = MaterialLineEdit("Search...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.filter_table)

        # Filter dropdown
        self.filter_combo = MaterialComboBox()
        self.filter_combo.setFixedWidth(150)
        self.filter_combo.currentTextChanged.connect(self.filter_table)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.filter_combo)
        search_layout.addStretch()

        layout.addWidget(search_frame)

    def create_table_section(self, layout):
        """Create the table section"""
        self.table = MaterialTable()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Wrap in MaterialSection
        self.table_section = MaterialSection("", self.table)
        layout.addWidget(self.table_section, stretch=1)

    def switch_view(self, view_name):
        """Switch to a different view"""
        # Update button states
        for name, btn in self.view_buttons.items():
            btn.setChecked(name == view_name)

        self.current_view = view_name
        self.update_view_content()

    def update_view_content(self):
        """Update the content based on current view"""
        config = self.view_configs[self.current_view]

        # Update title and subtitle
        self.title_label.setText(config["title"])
        self.subtitle_label.setText(config["subtitle"])

        # Update add button text
        self.add_btn.setText(f"Add New {self.current_view.rstrip('s')}")

        # Update search placeholder
        self.search_input.setPlaceholderText(f"Search {config['title'].lower()}...")

        # Update filter options
        self.filter_combo.clear()
        self.filter_combo.addItems(config["filters"])

        # Update table section title
        self.table_section.setTitle(f"All {self.current_view}")

        # Load and populate table data
        self.populate_current_table()

    def load_all_data(self):
        """Load all data from controllers"""
        self.users_data = self.users_controller.get_all()
        self.patrons_data = self.patrons_controller.get_all()
        self.books_data = self.books_controller.get_all()
        self.borrowed_books_data = self.borrowed_books_controller.get_all()
        self.payments_data = self.payment_controller.get_all()

    def get_current_data(self):
        """Get data for current view"""
        data_key = self.view_configs[self.current_view]["data_key"]
        return getattr(self, data_key, [])

    def populate_current_table(self):
        """Populate table based on current view"""
        data = self.get_current_data()
        config = self.view_configs[self.current_view]

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(config["headers"]))
        self.table.setHorizontalHeaderLabels(config["headers"])

        if self.current_view == "Users":
            self.populate_users_table(data)
        elif self.current_view == "Patrons":
            self.populate_patrons_table(data)
        elif self.current_view == "Books":
            self.populate_books_table(data)
        elif self.current_view == "Borrowed Books":
            self.populate_borrowed_books_table(data)
        elif self.current_view == "Payments":
            self.populate_payments_table(data)

        # Set column resize modes
        self.set_column_resize_modes()

    def populate_users_table(self, users):
        """Populate users table"""
        for row, user in enumerate(users):
            self.table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.table.setItem(row, 1, QTableWidgetItem(user.username or ""))
            self.table.setItem(row, 2, QTableWidgetItem(user.email or ""))
            self.table.setItem(row, 3, QTableWidgetItem(user.phone_number or ""))
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    user.role.value if hasattr(user.role, "value") else str(user.role)
                ),
            )

            # Active status with color coding
            active_item = QTableWidgetItem("Yes" if user.is_active else "No")
            active_item.setForeground(
                QColor(COLORS["success"] if user.is_active else COLORS["error"])
            )
            active_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 5, active_item)

    def populate_patrons_table(self, patrons):
        """Populate patrons table"""
        for row, patron in enumerate(patrons):
            # Patron ID with styling
            item = QTableWidgetItem(str(patron.patron_id))
            item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            item.setForeground(QColor(COLORS["primary"]))
            self.table.setItem(row, 0, item)

            self.table.setItem(row, 1, QTableWidgetItem(patron.first_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(patron.last_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(patron.gender or ""))

            dob_text = str(patron.date_of_birth) if patron.date_of_birth else "N/A"
            self.table.setItem(row, 4, QTableWidgetItem(dob_text))

            self.table.setItem(row, 5, QTableWidgetItem(patron.institution or "N/A"))
            self.table.setItem(row, 6, QTableWidgetItem(patron.grade_level or "N/A"))
            self.table.setItem(row, 7, QTableWidgetItem(patron.residence or "N/A"))
            self.table.setItem(row, 8, QTableWidgetItem(patron.phone_number or "N/A"))

            # Membership status with color coding
            membership = patron.membership_status or "Unknown"
            membership_item = QTableWidgetItem(membership.value if membership else "")

            if membership == "active":
                membership_item.setForeground(QColor(COLORS["success"]))
                membership_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            elif membership == "inactive":
                membership_item.setForeground(QColor(COLORS["error"]))
            elif membership == "pending":
                membership_item.setForeground(QColor(COLORS["warning"]))
            else:
                membership_item.setForeground(QColor(COLORS["on_surface_variant"]))

            self.table.setItem(row, 9, membership_item)

    def populate_books_table(self, books):
        """Populate books table"""
        for row, book in enumerate(books):
            self.table.setItem(row, 0, QTableWidgetItem(str(book.book_id)))
            self.table.setItem(row, 1, QTableWidgetItem(book.title or ""))
            self.table.setItem(row, 2, QTableWidgetItem(book.author or ""))
            self.table.setItem(row, 3, QTableWidgetItem(book.accession_no or ""))
            self.table.setItem(
                row, 4, QTableWidgetItem(getattr(book, "isbn", "") or "")
            )
            self.table.setItem(
                row, 5, QTableWidgetItem(getattr(book, "category", "") or "")
            )

            # Status with color coding
            status = getattr(book, "status", "Available") or "Available"
            status_item = QTableWidgetItem(status)

            if status.lower() == "available":
                status_item.setForeground(QColor(COLORS["success"]))
            elif status.lower() == "borrowed":
                status_item.setForeground(QColor(COLORS["warning"]))
            elif status.lower() == "reserved":
                status_item.setForeground(QColor(COLORS["primary"]))
            else:
                status_item.setForeground(QColor(COLORS["error"]))

            self.table.setItem(row, 6, status_item)
            self.table.setItem(
                row, 7, QTableWidgetItem(getattr(book, "location", "") or "")
            )

    def populate_borrowed_books_table(self, borrowed_books):
        """Populate borrowed books table"""
        for row, bb in enumerate(borrowed_books):
            self.table.setItem(row, 0, QTableWidgetItem(str(bb.borrow_id)))
            self.table.setItem(row, 1, QTableWidgetItem(str(bb.user_id)))
            self.table.setItem(row, 2, QTableWidgetItem(str(bb.book_id)))
            self.table.setItem(
                row, 3, QTableWidgetItem(getattr(bb, "book_title", "") or "")
            )
            self.table.setItem(row, 4, QTableWidgetItem(str(bb.borrow_date or "")))
            self.table.setItem(
                row, 5, QTableWidgetItem(str(getattr(bb, "due_date", "") or ""))
            )
            self.table.setItem(row, 6, QTableWidgetItem(str(bb.return_date or "")))

            # Status with color coding
            status = "Returned" if bb.returned else "Active"
            if hasattr(bb, "due_date") and bb.due_date and not bb.returned:
                # Check if overdue (simplified - you might want to use proper date comparison)
                status = "Overdue"

            status_item = QTableWidgetItem(status)
            if status == "Returned":
                status_item.setForeground(QColor(COLORS["success"]))
            elif status == "Overdue":
                status_item.setForeground(QColor(COLORS["error"]))
            else:
                status_item.setForeground(QColor(COLORS["warning"]))

            self.table.setItem(row, 7, status_item)

    def populate_payments_table(self, payments):
        """Populate payments table"""
        for row, payment in enumerate(payments):
            self.table.setItem(row, 0, QTableWidgetItem(str(payment.payment_id)))

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(str(payment.patron.patron_id)),
            )
            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(payment.patron.first_name + " " + payment.patron.last_name)
                ),
            )

            # Ensure payment_type is displayed as string
            payment_type = (
                payment.payment_item.display_name.lower()
                if payment.payment_item and payment.payment_item.display_name
                else "unknown"
            )
            self.table.setItem(row, 3, QTableWidgetItem(payment_type))

            # Amount with currency formatting
            amount_text = (
                f"${payment.amount_paid:.2f}" if payment.amount_paid else "N/A"
            )
            self.table.setItem(row, 4, QTableWidgetItem(amount_text))

            self.table.setItem(
                row, 5, QTableWidgetItem(str(payment.payment_date or ""))
            )

            # Status with color coding
            # Ensure the payment status is updated correctly
            payment.update_status()

            status = (
                payment.status.value
                if hasattr(payment.status, "value")
                else str(payment.status)
            )
            status_item = QTableWidgetItem(status)

            if status.lower() == "completed":
                status_item.setForeground(QColor(COLORS["success"]))
            elif status.lower() == "pending":
                status_item.setForeground(QColor(COLORS["warning"]))
            elif status.lower() == "partial":
                status_item.setForeground(QColor(COLORS["info"]))
            else:
                status_item.setForeground(QColor(COLORS["error"]))

            self.table.setItem(row, 6, status_item)

    def set_column_resize_modes(self):
        """Set appropriate column resize modes for current view"""
        header = self.table.horizontalHeader()

        if self.current_view == "Users":
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Username
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # Email
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Phone
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Role
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Active

        elif self.current_view == "Patrons":
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Patron ID
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # First Name
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Last Name
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Gender
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # DOB
            header.setSectionResizeMode(5, QHeaderView.Stretch)  # Institution
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Grade
            header.setSectionResizeMode(7, QHeaderView.Stretch)  # Residence
            header.setSectionResizeMode(8, QHeaderView.ResizeToContents)  # Phone
            header.setSectionResizeMode(9, QHeaderView.ResizeToContents)  # Membership

        elif self.current_view == "Books":
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Book ID
            header.setSectionResizeMode(1, QHeaderView.Stretch)  # Title
            header.setSectionResizeMode(2, QHeaderView.Stretch)  # Author
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Accession No
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # ISBN
            header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Category
            header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Status
            header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Location

        else:
            # Default: stretch all columns
            header.setSectionResizeMode(QHeaderView.Stretch)

        # Adjust row heights
        for row in range(self.table.rowCount()):
            self.table.setRowHeight(row, 50)

    def filter_table(self):
        """Filter table based on search and filter criteria"""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_combo.currentText()

        all_data = self.get_current_data()
        filtered_data = []

        for item in all_data:
            # Apply search filter
            if search_text and not self.matches_search(item, search_text):
                continue

            # Apply type filter
            if filter_type != f"All {self.current_view}" and not self.matches_filter(
                item, filter_type
            ):
                continue

            filtered_data.append(item)

        # Update the table with filtered data
        self.update_table_with_data(filtered_data)

    def matches_search(self, item, search_text):
        """Check if item matches search criteria"""
        if self.current_view == "Users":
            searchable = (
                f"{item.username} {item.email} {item.phone_number or ''}".lower()
            )
        elif self.current_view == "Patrons":
            searchable = f"{item.first_name} {item.last_name} {item.phone_number or ''} {item.institution or ''}".lower()
        elif self.current_view == "Books":
            searchable = f"{item.title} {item.author} {item.accession_no or ''}".lower()
        elif self.current_view == "Borrowed Books":
            searchable = f"{item.borrow_id} {item.user_id} {item.book_id}".lower()
        elif self.current_view == "Payments":
            searchable = (
                f"{item.payment_id} {item.user_id} {item.payment_type or ''}".lower()
            )
        else:
            return True

        return search_text in searchable

    def matches_filter(self, item, filter_type):
        """Check if item matches filter criteria"""
        if self.current_view == "Users":
            if filter_type == "Active":
                return item.is_active
            elif filter_type == "Inactive":
                return not item.is_active
            elif filter_type == "Admins":
                return str(item.role).lower() == "admin"
            elif filter_type == "Staff":
                return str(item.role).lower() == "staff"

        elif self.current_view == "Patrons":
            membership = item.membership_status.value or ""
            if filter_type == "Active":
                return membership == "active"
            elif filter_type == "Inactive":
                return membership == "inactive"
            elif filter_type == "Recent":
                return membership in ["pending", "new"]
            elif filter_type == "Students":
                return bool(item.institution)

        elif self.current_view == "Books":
            status = getattr(item, "status", "available").lower()
            if filter_type == "Available":
                return status == "available"
            elif filter_type == "Borrowed":
                return status == "borrowed"
            elif filter_type == "Reserved":
                return status == "reserved"
            elif filter_type == "Damaged":
                return status == "damaged"

        elif self.current_view == "Borrowed Books":
            if filter_type == "Active":
                return not item.returned
            elif filter_type == "Returned":
                return item.returned
            elif filter_type == "Overdue":
                # Simplified overdue check - implement proper date logic
                return not item.returned and hasattr(item, "due_date")

        elif self.current_view == "Payments":
            payment_type = (
                item.payment_item.name.lower()
                if item.payment_item.name and item.payment_item.name
                else "unknown"
            )

            if filter_type == "Membership":
                return "membership" in payment_type
            elif filter_type == "Penalties":
                return "penalty" in payment_type or "fine" in payment_type
            elif filter_type == "Recent":
                # TODO: implement date-based filtering for recent
                return True
            elif filter_type == "Pending":
                status = str(getattr(item, "status", "")).lower()
                return status == "pending"

        return True

    def update_table_with_data(self, data):
        """Update table with specific data set"""
        config = self.view_configs[self.current_view]

        self.table.setRowCount(len(data))
        self.table.setColumnCount(len(config["headers"]))
        self.table.setHorizontalHeaderLabels(config["headers"])

        if self.current_view == "Users":
            self.populate_users_table(data)
        elif self.current_view == "Patrons":
            self.populate_patrons_table(data)
        elif self.current_view == "Books":
            self.populate_books_table(data)
        elif self.current_view == "Borrowed Books":
            self.populate_borrowed_books_table(data)
        elif self.current_view == "Payments":
            self.populate_payments_table(data)

        self.set_column_resize_modes()

    def refresh_current_view(self):
        """Refresh the current view data"""
        self.load_all_data()
        self.populate_current_table()

    def get_selected_items(self):
        """Get currently selected items from table"""
        selected_rows = set()
        for item in self.table.selectedItems():
            selected_rows.add(item.row())

        current_data = self.get_current_data()
        return [current_data[row] for row in selected_rows if row < len(current_data)]

    def import_data(self):
        """Import data based on current view"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Import {self.current_view} Data",
            "",
            "CSV Files (*.csv);;JSON Files (*.json);;All Files (*)",
        )

        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                self.import_csv(file_path)
            elif file_path.endswith(".json"):
                self.import_json(file_path)
            else:
                QMessageBox.warning(self, "Warning", "Unsupported file format!")
                return

            # Refresh the view after import
            self.load_all_data()
            self.populate_current_table()

            QMessageBox.information(
                self, "Success", f"{self.current_view} data imported successfully!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to import data: {str(e)}")

    def export_data(self):
        """Export current view data"""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            f"Export {self.current_view} Data",
            f"{self.current_view.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "CSV Files (*.csv);;JSON Files (*.json)",
        )

        if not file_path:
            return

        try:
            current_data = self.get_current_data()

            if "CSV" in selected_filter:
                self.export_csv(file_path, current_data)
            elif "JSON" in selected_filter:
                self.export_json(file_path, current_data)

            QMessageBox.information(
                self, "Success", f"{self.current_view} data exported successfully!"
            )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export data: {str(e)}")

    def import_csv(self, file_path):
        """Import data from CSV file"""
        with open(file_path, "r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            if self.current_view == "Users":
                self.import_users_csv(reader)
            elif self.current_view == "Patrons":
                self.import_patrons_csv(reader)
            elif self.current_view == "Books":
                self.import_books_csv(reader)
            elif self.current_view == "Payments":
                self.import_payments_csv(reader)

    def import_json(self, file_path):
        """Import data from JSON file"""
        with open(file_path, "r", encoding="utf-8") as jsonfile:
            data = json.load(jsonfile)

            if self.current_view == "Users":
                self.import_users_json(data)
            elif self.current_view == "Patrons":
                self.import_patrons_json(data)
            elif self.current_view == "Books":
                self.import_books_json(data)
            elif self.current_view == "Payments":
                self.import_payments_json(data)

    def export_csv(self, file_path, data):
        """Export data to CSV file"""
        if not data:
            return

        # config = self.view_configs[self.current_view]

        with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = self.get_export_fieldnames()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for item in data:
                row_data = self.convert_item_to_dict(item)
                writer.writerow(row_data)

    def export_json(self, file_path, data):
        """Export data to JSON file"""
        export_data = []

        for item in data:
            item_dict = self.convert_item_to_dict(item)
            export_data.append(item_dict)

        with open(file_path, "w", encoding="utf-8") as jsonfile:
            json.dump(export_data, jsonfile, indent=2, default=str)

    def get_export_fieldnames(self):
        """Get fieldnames for CSV export based on current view"""
        if self.current_view == "Users":
            return ["id", "username", "email", "phone_number", "role", "is_active"]
        elif self.current_view == "Patrons":
            return [
                "patron_id",
                "first_name",
                "last_name",
                "gender",
                "date_of_birth",
                "institution",
                "grade_level",
                "residence",
                "phone_number",
                "membership_status",
            ]
        elif self.current_view == "Books":
            return [
                "book_id",
                "title",
                "author",
                "accession_no",
                "isbn",
                "category",
                "status",
                "location",
            ]
        elif self.current_view == "Borrowed Books":
            return [
                "borrow_id",
                "user_id",
                "book_id",
                "borrow_date",
                "due_date",
                "return_date",
                "returned",
            ]
        elif self.current_view == "Payments":
            return [
                "payment_id",
                "user_id",
                "payment_type",
                "amount",
                "payment_date",
                "status",
            ]
        return []

    def convert_item_to_dict(self, item):
        """Convert database model to dictionary for export"""
        if self.current_view == "Users":
            return {
                "id": item.id,
                "username": item.username,
                "email": item.email,
                "phone_number": item.phone_number,
                "role": (
                    item.role.value if hasattr(item.role, "value") else str(item.role)
                ),
                "is_active": item.is_active,
            }
        elif self.current_view == "Patrons":
            return {
                "patron_id": item.patron_id,
                "first_name": item.first_name,
                "last_name": item.last_name,
                "gender": item.gender,
                "date_of_birth": item.date_of_birth,
                "institution": item.institution,
                "grade_level": item.grade_level,
                "residence": item.residence,
                "phone_number": item.phone_number,
                "membership_status": item.membership_status,
            }
        elif self.current_view == "Books":
            return {
                "book_id": item.book_id,
                "title": item.title,
                "author": item.author,
                "accession_no": item.accession_no,
                "isbn": getattr(item, "isbn", ""),
                "category": getattr(item, "category", ""),
                "status": getattr(item, "status", "Available"),
                "location": getattr(item, "location", ""),
            }
        elif self.current_view == "Borrowed Books":
            return {
                "borrow_id": item.borrow_id,
                "user_id": item.user_id,
                "book_id": item.book_id,
                "borrow_date": item.borrow_date,
                "due_date": getattr(item, "due_date", ""),
                "return_date": item.return_date,
                "returned": item.returned,
            }
        elif self.current_view == "Payments":
            return {
                "payment_id": item.payment_id,
                "user_id": item.user_id,
                "payment_type": item.payment_type,
                "amount": item.amount,
                "payment_date": item.payment_date,
                "status": getattr(item, "status", "Completed"),
            }
        return {}

    def import_users_csv(self, reader):
        """Import users from CSV reader"""
        for row in reader:
            # Implement user creation logic using your users_controller
            # Example:
            # self.users_controller.create_user(
            #     username=row.get('username'),
            #     email=row.get('email'),
            #     phone_number=row.get('phone_number'),
            #     role=row.get('role'),
            #     is_active=row.get('is_active', 'true').lower() == 'true'
            # )
            pass

    def import_patrons_csv(self, reader):
        """Import patrons from CSV reader"""
        for row in reader:
            # Implement patron creation logic using your patrons_controller
            # Example:
            # self.patrons_controller.create_patron(
            #     patron_id=row.get('patron_id'),
            #     first_name=row.get('first_name'),
            #     last_name=row.get('last_name'),
            #     # ... other fields
            # )
            pass

    def import_books_csv(self, reader):
        """Import books from CSV reader"""
        for row in reader:
            # Implement book creation logic using your books_controller
            pass

    def import_payments_csv(self, reader):
        """Import payments from CSV reader"""
        for row in reader:
            # Implement payment creation logic using your payments_controller
            pass

    # Similar methods for JSON imports...
    def import_users_json(self, data):
        """Import users from JSON data"""
        for item in data:
            # Implement user creation from JSON
            pass

    def import_patrons_json(self, data):
        """Import patrons from JSON data"""
        for item in data:
            # Implement patron creation from JSON
            pass

    def import_books_json(self, data):
        """Import books from JSON data"""
        for item in data:
            # Implement book creation from JSON
            pass

    def import_payments_json(self, data):
        """Import payments from JSON data"""
        for item in data:
            # Implement payment creation from JSON
            pass
