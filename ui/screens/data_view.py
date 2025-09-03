from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTabWidget,
    QTableWidgetItem,
    QHeaderView,
    QSizePolicy,
)
from PyQt5.QtGui import QColor
from ui.widgets.table.material_table import MaterialTable
from utils.constants import COLORS

from controllers.patrons_controller import PatronsController
from controllers.books_controller import BooksController
from controllers.borrowed_books_controller import BorrowedBooksController
from controllers.payments_controller import PaymentController
from controllers.users_controller import UsersController


class LibraryDataView(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.patrons_controller = PatronsController(self.db_manager)
        self.books_controller = BooksController(self.db_manager)
        self.borrowed_books_controller = BorrowedBooksController(self.db_manager)
        self.payment_controller = PaymentController(self.db_manager)
        self.users_controller = UsersController(self.db_manager)
        self.setup_ui()
        self.load_all_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # Tabs
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # Each tab has a MaterialTable
        self.tables = {}
        for name in ["Users", "Patrons", "Payments", "Books", "Borrowed Books"]:
            table = MaterialTable()
            table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            self.tabs.addTab(table, name)
            self.tables[name] = table

    def load_all_data(self):
        users = self.users_controller.get_all()
        patrons = self.patrons_controller.get_all()
        payments = self.payment_controller.get_all()
        books = self.books_controller.get_all()
        borrowedBooks = self.borrowed_books_controller.get_all()

        self.load_users(users)
        self.load_patrons(patrons)
        self.load_payments(payments)
        self.load_books(books)
        self.load_borrowed_books(borrowedBooks)

    # -------------------
    # Table population
    # -------------------
    def load_users(self, users):
        table = self.tables["Users"]
        table.setRowCount(len(users))
        table.setColumnCount(6)
        headers = ["ID", "Username", "Email", "Phone", "Role", "Active"]
        table.setHorizontalHeaderLabels(headers)

        for row, user in enumerate(users):
            table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            table.setItem(row, 1, QTableWidgetItem(user.username))
            table.setItem(row, 2, QTableWidgetItem(user.email))
            table.setItem(row, 3, QTableWidgetItem(user.phone_number))
            table.setItem(row, 4, QTableWidgetItem(user.role.value))
            active_item = QTableWidgetItem("Yes" if user.is_active else "No")
            active_item.setForeground(
                QColor(COLORS["success"] if user.is_active else COLORS["error"])
            )
            table.setItem(row, 5, active_item)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_patrons(self, patrons):
        table = self.tables["Patrons"]
        table.setRowCount(len(patrons))
        table.setColumnCount(6)
        headers = ["Patron ID", "First", "Last", "Institution", "Grade", "Phone"]
        table.setHorizontalHeaderLabels(headers)

        for row, p in enumerate(patrons):
            table.setItem(row, 0, QTableWidgetItem(p.patron_id or ""))
            table.setItem(row, 1, QTableWidgetItem(p.first_name or ""))
            table.setItem(row, 2, QTableWidgetItem(p.last_name or ""))
            table.setItem(row, 3, QTableWidgetItem(p.institution or ""))
            table.setItem(row, 4, QTableWidgetItem(p.grade_level or ""))
            table.setItem(row, 5, QTableWidgetItem(p.phone_number or ""))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_payments(self, payments):
        table = self.tables["Payments"]
        table.setRowCount(len(payments))
        table.setColumnCount(5)
        headers = ["ID", "User ID", "Type", "Amount", "Date"]
        table.setHorizontalHeaderLabels(headers)

        for row, p in enumerate(payments):
            table.setItem(row, 0, QTableWidgetItem(str(p.payment_id)))
            table.setItem(row, 1, QTableWidgetItem(str(p.user_id)))
            # Ensure payment_type is displayed as string
            # payment_type_text = (
            #     p.payment_type.value
            #     if hasattr(p.payment_type, "value")
            #     else str(p.payment_type or "")
            # )
            payment_type_text = (
                p.payment_item.display_name.lower()
                if p.payment_item and p.payment_item.display_name
                else "unknown"
            )
            table.setItem(row, 2, QTableWidgetItem(payment_type_text))
            table.setItem(row, 3, QTableWidgetItem(str(p.amount_paid or "")))
            table.setItem(row, 4, QTableWidgetItem(str(p.payment_date or "")))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_books(self, books):
        table = self.tables["Books"]
        table.setRowCount(len(books))
        table.setColumnCount(4)
        headers = ["ID", "Title", "Author", "Accession No."]
        table.setHorizontalHeaderLabels(headers)

        for row, b in enumerate(books):
            table.setItem(row, 0, QTableWidgetItem(str(b.book_id)))
            table.setItem(row, 1, QTableWidgetItem(b.title or ""))
            table.setItem(row, 2, QTableWidgetItem(b.author or ""))
            table.setItem(row, 3, QTableWidgetItem(b.accession_no or ""))

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def load_borrowed_books(self, borrowed_books):
        table = self.tables["Borrowed Books"]
        table.setRowCount(len(borrowed_books))
        table.setColumnCount(6)
        headers = [
            "Borrow ID",
            "User ID",
            "Book ID",
            "Borrow Date",
            "Return Date",
            "Returned",
        ]
        table.setHorizontalHeaderLabels(headers)

        for row, bb in enumerate(borrowed_books):
            table.setItem(row, 0, QTableWidgetItem(str(bb.borrow_id)))
            table.setItem(row, 1, QTableWidgetItem(str(bb.user_id)))
            table.setItem(row, 2, QTableWidgetItem(str(bb.book_id)))
            table.setItem(row, 3, QTableWidgetItem(str(bb.borrow_date or "")))
            table.setItem(row, 4, QTableWidgetItem(str(bb.return_date or "")))
            returned_item = QTableWidgetItem("Yes" if bb.returned else "No")
            returned_item.setForeground(
                QColor(COLORS["success"] if bb.returned else COLORS["error"])
            )
            table.setItem(row, 5, returned_item)

        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
