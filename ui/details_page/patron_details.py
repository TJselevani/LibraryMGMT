from enum import Enum
import sys
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QTableWidgetItem,
    QPushButton,
    QScrollArea,
    QTableWidget,
    QAbstractItemView,
    QApplication,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from datetime import datetime, date

from db.models import MembershipStatus


class MaterialCard(QFrame):
    """A Material Design-style card widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(
            """
            MaterialCard {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            }
        """
        )
        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(10)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.shadow.setOffset(0, 2)
        self.setGraphicsEffect(self.shadow)


class MaterialButton(QPushButton):
    """A Material Design-style button"""

    def __init__(self, text, button_type="contained", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self._setup_style()

    def _setup_style(self):
        if self.button_type == "contained":
            self.setStyleSheet(
                """
                MaterialButton {
                    background-color: #1976d2;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 10px 24px;
                    font-weight: 500;
                    font-size: 14px;
                }
                MaterialButton:hover {
                    background-color: #1565c0;
                }
                MaterialButton:pressed {
                    background-color: #0d47a1;
                }
            """
            )
        elif self.button_type == "outlined":
            self.setStyleSheet(
                """
                MaterialButton {
                    background-color: transparent;
                    color: #1976d2;
                    border: 1px solid #1976d2;
                    border-radius: 4px;
                    padding: 10px 24px;
                    font-weight: 500;
                    font-size: 14px;
                }
                MaterialButton:hover {
                    background-color: #e3f2fd;
                }
                MaterialButton:pressed {
                    background-color: #bbdefb;
                }
            """
            )


class InfoRow(QWidget):
    """A widget for displaying key-value information pairs"""

    def __init__(self, label, value, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Label
        label_widget = QLabel(label)
        label_widget.setStyleSheet(
            """
            color: #666;
            font-weight: 500;
            font-size: 14px;
        """
        )
        label_widget.setFixedWidth(150)

        # Value
        value_widget = QLabel(str(value))
        value_widget.setStyleSheet(
            """
            color: #333;
            font-size: 14px;
        """
        )
        value_widget.setWordWrap(True)

        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        layout.addStretch()


class PatronProfilePage(QWidget):
    """Main patron profile page widget"""

    def __init__(self, patron_controller, patron=None, parent=None):
        super().__init__(parent)
        self.patron_controller = patron_controller
        self.patron = patron
        self._init_ui()
        if patron:
            self._load_patron_data()

    def _init_ui(self):
        self.setWindowTitle("Patron Profile")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(
            """
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
        """
        )

        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Header
        self._create_header(main_layout)

        # Content area with scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameStyle(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)

        # Profile cards
        self._create_profile_cards(content_layout)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_header(self, layout):
        """Create the page header"""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        # Title
        title = QLabel("Patron Profile")
        title.setStyleSheet(
            """
            font-size: 28px;
            font-weight: 600;
            color: #333;
            margin-bottom: 5px;
        """
        )

        # Subtitle
        self.subtitle = QLabel("Loading patron information...")
        self.subtitle.setStyleSheet(
            """
            font-size: 16px;
            color: #666;
        """
        )

        title_layout = QVBoxLayout()
        title_layout.addWidget(title)
        title_layout.addWidget(self.subtitle)

        # Action buttons
        button_layout = QHBoxLayout()

        self.edit_btn = MaterialButton("Edit Profile", "contained")
        self.edit_btn.clicked.connect(self._edit_profile)

        self.delete_btn = MaterialButton("Delete Patron", "outlined")
        self.delete_btn.setStyleSheet(
            """
            MaterialButton {
                background-color: transparent;
                color: #d32f2f;
                border: 1px solid #d32f2f;
                border-radius: 4px;
                padding: 10px 24px;
                font-weight: 500;
                font-size: 14px;
            }
            MaterialButton:hover {
                background-color: #ffebee;
            }
        """
        )
        self.delete_btn.clicked.connect(self._delete_patron)

        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addStretch()

        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        header_layout.addLayout(button_layout)

        layout.addWidget(header)

    def _create_profile_cards(self, layout):
        """Create all profile information cards"""
        # Top row - Personal Info and Status
        top_row = QHBoxLayout()

        # Personal Information Card
        personal_card = self._create_personal_info_card()
        top_row.addWidget(personal_card, 2)

        # Status Card
        status_card = self._create_status_card()
        top_row.addWidget(status_card, 1)

        layout.addLayout(top_row)

        # Bottom row - Activities
        bottom_row = QHBoxLayout()

        # Payment History Card
        payments_card = self._create_payments_card()
        bottom_row.addWidget(payments_card)

        # Borrowed Books Card
        books_card = self._create_borrowed_books_card()
        bottom_row.addWidget(books_card)

        layout.addLayout(bottom_row)

    def _create_personal_info_card(self):
        """Create personal information card"""
        card = MaterialCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        # Card header
        header = QLabel("Personal Information")
        header.setStyleSheet(
            """
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        """
        )
        layout.addWidget(header)

        # Info rows container
        info_container = QWidget()
        self.personal_info_layout = QVBoxLayout(info_container)
        self.personal_info_layout.setSpacing(5)

        layout.addWidget(info_container)
        layout.addStretch()

        return card

    def _create_status_card(self):
        """Create status and membership card"""
        card = MaterialCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        # Card header
        header = QLabel("Status & Membership")
        header.setStyleSheet(
            """
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 15px;
        """
        )
        layout.addWidget(header)

        # Status indicator
        self.status_indicator = QLabel()
        self.status_indicator.setAlignment(Qt.AlignCenter)
        self.status_indicator.setStyleSheet(
            """
            padding: 10px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin-bottom: 15px;
        """
        )
        layout.addWidget(self.status_indicator)

        # Status info container
        status_container = QWidget()
        self.status_info_layout = QVBoxLayout(status_container)
        self.status_info_layout.setSpacing(5)

        layout.addWidget(status_container)
        layout.addStretch()

        # Action buttons
        btn_layout = QHBoxLayout()
        self.activate_btn = MaterialButton("Activate", "contained")
        self.deactivate_btn = MaterialButton("Deactivate", "outlined")

        self.activate_btn.clicked.connect(self._activate_patron)
        self.deactivate_btn.clicked.connect(self._deactivate_patron)

        btn_layout.addWidget(self.activate_btn)
        btn_layout.addWidget(self.deactivate_btn)
        layout.addLayout(btn_layout)

        return card

    def _create_payments_card(self):
        """Create payment history card"""
        card = MaterialCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        # Card header
        header_layout = QHBoxLayout()
        header = QLabel("Payment History")
        header.setStyleSheet(
            """
            font-size: 18px;
            font-weight: 600;
            color: #333;
        """
        )

        self.payments_count = QLabel("(0 payments)")
        self.payments_count.setStyleSheet("color: #666; font-size: 14px;")

        header_layout.addWidget(header)
        header_layout.addWidget(self.payments_count)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Payments table
        self.payments_table = QTableWidget()
        self.payments_table.setColumnCount(4)
        self.payments_table.setHorizontalHeaderLabels(
            ["Date", "Item", "Amount", "Status"]
        )

        # Style the table
        self.payments_table.setStyleSheet(
            """
            QTableWidget {
                border: none;
                background-color: transparent;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px;
                border: none;
                font-weight: 600;
                color: #333;
            }
        """
        )

        self.payments_table.horizontalHeader().setStretchLastSection(True)
        self.payments_table.verticalHeader().setVisible(False)
        self.payments_table.setAlternatingRowColors(True)
        self.payments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.payments_table.setMaximumHeight(300)

        layout.addWidget(self.payments_table)

        return card

    def _create_borrowed_books_card(self):
        """Create borrowed books card"""
        card = MaterialCard()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)

        # Card header
        header_layout = QHBoxLayout()
        header = QLabel("Borrowed Books")
        header.setStyleSheet(
            """
            font-size: 18px;
            font-weight: 600;
            color: #333;
        """
        )

        self.books_count = QLabel("(0 books)")
        self.books_count.setStyleSheet("color: #666; font-size: 14px;")

        header_layout.addWidget(header)
        header_layout.addWidget(self.books_count)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        # Books table
        self.books_table = QTableWidget()
        self.books_table.setColumnCount(5)
        self.books_table.setHorizontalHeaderLabels(
            ["Title", "Author", "Borrowed", "Due", "Status"]
        )

        # Style the table
        self.books_table.setStyleSheet(
            """
            QTableWidget {
                border: none;
                background-color: transparent;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #f5f5f5;
                padding: 10px;
                border: none;
                font-weight: 600;
                color: #333;
            }
        """
        )

        self.books_table.horizontalHeader().setStretchLastSection(True)
        self.books_table.verticalHeader().setVisible(False)
        self.books_table.setAlternatingRowColors(True)
        self.books_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.books_table.setMaximumHeight(300)

        layout.addWidget(self.books_table)

        return card

    def _load_patron_data(self):
        """Load patron data into the UI"""
        if not self.patron:
            return

        # Update header
        self.subtitle.setText(
            f"{self.patron.first_name} {self.patron.last_name} - {self.patron.patron_id}"
        )

        # Load personal information
        self._populate_personal_info()

        # Load status information
        self._populate_status_info()

        # Load payment history
        self._populate_payments()

        # Load borrowed books
        self._populate_borrowed_books()

    def _populate_personal_info(self):
        """Populate personal information section"""
        # Clear existing info
        for i in reversed(range(self.personal_info_layout.count())):
            self.personal_info_layout.itemAt(i).widget().setParent(None)

        # Add info rows
        info_data = [
            ("Full Name", f"{self.patron.first_name} {self.patron.last_name}"),
            ("Patron ID", self.patron.patron_id),
            ("Phone Number", getattr(self.patron, "phone_number", "N/A")),
            ("Email", getattr(self.patron, "email", "N/A")),
            ("Date of Birth", getattr(self.patron, "date_of_birth", "N/A")),
            ("Institution", getattr(self.patron, "institution", "N/A")),
            ("Grade Level", getattr(self.patron, "grade_level", "N/A")),
            ("Address", getattr(self.patron, "address", "N/A")),
        ]

        for label, value in info_data:
            if value and str(value) != "N/A":
                self.personal_info_layout.addWidget(InfoRow(label, value))

    def _populate_status_info(self):
        """Populate status information section"""
        status = getattr(self.patron, "membership_status", MembershipStatus.INACTIVE)
        if isinstance(status, Enum):
            status_str = status.value  # use `.value` instead of `.title()`
        else:
            status_str = str(status)

        # Update status indicator
        if status_str == "active":
            self.status_indicator.setText("ACTIVE")
            self.status_indicator.setStyleSheet(
                self.status_indicator.styleSheet()
                + "background-color: #4caf50; color: white;"
            )
            self.activate_btn.setEnabled(False)
            self.deactivate_btn.setEnabled(True)
        else:
            self.status_indicator.setText("INACTIVE")
            self.status_indicator.setStyleSheet(
                self.status_indicator.styleSheet()
                + "background-color: #f44336; color: white;"
            )
            self.activate_btn.setEnabled(True)
            self.deactivate_btn.setEnabled(False)

        # Clear existing status info
        for i in reversed(range(self.status_info_layout.count())):
            self.status_info_layout.itemAt(i).widget().setParent(None)

        # Add status info
        join_date = getattr(self.patron, "join_date", None)
        if join_date:
            self.status_info_layout.addWidget(InfoRow("Member Since", join_date))

        # Get membership fee if available
        try:
            fee = self.patron_controller.get_membership_fee(self.patron.user_id)
            if fee:
                self.status_info_layout.addWidget(InfoRow("Membership Fee", f"${fee}"))
        except Exception:
            pass

    def _populate_payments(self):
        """Populate payment history table"""
        payments = getattr(self.patron, "payments", [])
        self.payments_count.setText(f"({len(payments)} payments)")

        self.payments_table.setRowCount(len(payments))

        for row, payment in enumerate(payments):
            # Date
            payment_date = getattr(payment, "payment_date", "N/A")
            if isinstance(payment_date, (date, datetime)):
                payment_date = payment_date.strftime("%Y-%m-%d")

            self.payments_table.setItem(row, 0, QTableWidgetItem(str(payment_date)))

            # Item
            item_name = "N/A"
            if hasattr(payment, "payment_item") and payment.payment_item:
                item_name = getattr(payment.payment_item, "name", "N/A")
            self.payments_table.setItem(row, 1, QTableWidgetItem(item_name))

            # Amount
            amount = getattr(payment, "amount", 0)
            self.payments_table.setItem(row, 2, QTableWidgetItem(f"${amount}"))

            # Status
            status = getattr(payment, "status", "N/A")
            # Convert Enum to string if needed
            if isinstance(status, Enum):
                status = status.value  # or str(status.value)
            self.payments_table.setItem(row, 3, QTableWidgetItem(str(status)))

    def _populate_borrowed_books(self):
        """Populate borrowed books table"""
        borrowed_books = getattr(self.patron, "borrowed_books", [])
        self.books_count.setText(f"({len(borrowed_books)} books)")

        self.books_table.setRowCount(len(borrowed_books))

        for row, borrowed_book in enumerate(borrowed_books):
            # Title and Author
            title = "N/A"
            author = "N/A"
            if hasattr(borrowed_book, "book") and borrowed_book.book:
                title = getattr(borrowed_book.book, "title", "N/A")
                author = getattr(borrowed_book.book, "author", "N/A")

            self.books_table.setItem(row, 0, QTableWidgetItem(title))
            self.books_table.setItem(row, 1, QTableWidgetItem(author))

            # Borrowed date
            borrowed_date = getattr(borrowed_book, "borrowed_date", "N/A")
            if isinstance(borrowed_date, (date, datetime)):
                borrowed_date = borrowed_date.strftime("%Y-%m-%d")
            self.books_table.setItem(row, 2, QTableWidgetItem(str(borrowed_date)))

            # Due date
            due_date = getattr(borrowed_book, "due_date", "N/A")
            if isinstance(due_date, (date, datetime)):
                due_date = due_date.strftime("%Y-%m-%d")
            self.books_table.setItem(row, 3, QTableWidgetItem(str(due_date)))

            # Status
            returned = getattr(borrowed_book, "returned", False)
            status = "Returned" if returned else "Borrowed"

            status_item = QTableWidgetItem(status)
            if not returned:
                # Check if overdue
                if hasattr(borrowed_book, "due_date") and borrowed_book.due_date:
                    if isinstance(borrowed_book.due_date, (date, datetime)):
                        if (
                            borrowed_book.due_date.date() < date.today()
                            if isinstance(borrowed_book.due_date, datetime)
                            else borrowed_book.due_date < date.today()
                        ):
                            status = "Overdue"
                            status_item.setForeground(QColor("#d32f2f"))

            self.books_table.setItem(row, 4, status_item)

    def set_patron(self, patron):
        """Set a new patron and refresh the display"""
        self.patron = patron
        self._load_patron_data()

    def _edit_profile(self):
        """Handle edit profile button click"""
        QMessageBox.information(
            self,
            "Edit Profile",
            "Edit profile functionality would be implemented here.",
        )

    def _delete_patron(self):
        """Handle delete patron button click"""
        if not self.patron:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete patron {self.patron.first_name} {self.patron.last_name}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            result = self.patron_controller.delete_patron(self.patron.user_id)
            if result["success"]:
                QMessageBox.information(self, "Success", result["message"])
                self.close()
            else:
                QMessageBox.warning(self, "Error", result["message"])

    def _activate_patron(self):
        """Handle activate patron button click"""
        if not self.patron:
            return

        result = self.patron_controller.activate_patron(self.patron.user_id)
        if result["success"]:
            self.patron = result["patron"]
            self._populate_status_info()
            QMessageBox.information(self, "Success", "Patron activated successfully.")
        else:
            QMessageBox.warning(self, "Error", result["message"])

    def _deactivate_patron(self):
        """Handle deactivate patron button click"""
        if not self.patron:
            return

        result = self.patron_controller.deactivate_patron(self.patron.user_id)
        if result["success"]:
            self.patron = result["patron"]
            self._populate_status_info()
            QMessageBox.information(self, "Success", "Patron deactivated successfully.")
        else:
            QMessageBox.warning(self, "Error", result["message"])


# Example usage and demo
def main():
    app = QApplication(sys.argv)

    # Mock data for demonstration
    class MockPatron:
        def __init__(self):
            self.user_id = 1
            self.patron_id = "AB123"
            self.first_name = "John"
            self.last_name = "Doe"
            self.phone_number = "+1234567890"
            self.email = "john.doe@example.com"
            self.date_of_birth = date(1990, 5, 15)
            self.institution = "Central High School"
            self.grade_level = "12"
            self.address = "123 Main St, City, State 12345"
            self.membership_status = MembershipStatus.ACTIVE
            self.join_date = date(2023, 1, 15)
            self.payments = []
            self.borrowed_books = []

    class MockController:
        def get_membership_fee(self, user_id):
            return 25.00

        def delete_patron(self, user_id):
            return {"success": True, "message": "Patron deleted successfully"}

        def activate_patron(self, user_id):
            patron = MockPatron()
            return {"success": True, "patron": patron}

        def deactivate_patron(self, user_id):
            patron = MockPatron()
            patron.membership_status = MembershipStatus.INACTIVE
            return {"success": True, "patron": patron}

    # Create and show the profile page
    mock_patron = MockPatron()
    mock_controller = MockController()

    profile_page = PatronProfilePage(mock_controller, mock_patron)
    profile_page.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
