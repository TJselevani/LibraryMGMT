from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QListWidget,
    QMessageBox,
    QFrame,

    QListWidgetItem,
    QTextEdit,
    QGridLayout,
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS
from datetime import datetime


class PatronSearchWidget(QFrame):
    """Reusable patron search widget"""

    patron_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.all_patrons = []
        self.selected_patron = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px;
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search patron...")
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: white;
            }}
        """
        )
        layout.addWidget(self.search_input)

        # Selected patron display
        self.selected_label = QLabel("No patron selected")
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        layout.addWidget(self.selected_label)

        # Search results
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(100)
        self.search_results.setStyleSheet(
            f"""
            QListWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
        """
        )
        layout.addWidget(self.search_results)

        # Connect signals
        self.search_input.textChanged.connect(self.filter_patrons)
        self.search_results.itemClicked.connect(self.select_patron)

    def load_patrons(self, patrons):
        self.all_patrons = patrons
        self.update_search_results()

    def filter_patrons(self):
        self.update_search_results()

    def update_search_results(self):
        search_text = self.search_input.text().lower()
        self.search_results.clear()

        if len(search_text) < 2:
            return

        for patron in self.all_patrons:
            searchable = f"{patron.first_name} {patron.last_name} {patron.patron_id} {patron.institution}".lower()

            if search_text in searchable:
                display_text = f"{patron.first_name} {patron.last_name}"
                detail_text = f"ID: {patron.patron_id} | {patron.institution}"

                item = QListWidgetItem(f"{display_text}\n{detail_text}")
                item.setData(Qt.UserRole, patron)
                self.search_results.addItem(item)

    def select_patron(self, item):
        self.selected_patron = item.data(Qt.UserRole)
        self.selected_label.setText(
            f"✓ {self.selected_patron.first_name} {self.selected_patron.last_name} "
            f"(ID: {self.selected_patron.patron_id})"
        )
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                border: 1px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
        """
        )
        self.search_results.clear()
        self.search_input.clear()
        self.patron_selected.emit(self.selected_patron)


class BookSearchWidget(QFrame):
    """Custom widget for book search with availability checking"""

    book_selected = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.all_books = []
        self.selected_book = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px;
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(8, 8, 8, 8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("📖 Search book...")
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: white;
            }}
        """
        )
        layout.addWidget(self.search_input)

        # Selected book display
        self.selected_label = QLabel("No book selected")
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        layout.addWidget(self.selected_label)

        # Search results
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(120)
        self.search_results.setStyleSheet(
            f"""
            QListWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
        """
        )
        layout.addWidget(self.search_results)

        # Connect signals
        self.search_input.textChanged.connect(self.filter_books)
        self.search_results.itemClicked.connect(self.select_book)

    def load_books(self, books):
        self.all_books = books
        self.update_search_results()

    def filter_books(self):
        self.update_search_results()

    def update_search_results(self):
        search_text = self.search_input.text().lower()
        self.search_results.clear()

        if len(search_text) < 2:
            return

        for book in self.all_books:
            searchable = f"{book.title} {book.author} {book.accession_no} {book.class_name or ''}".lower()

            if search_text in searchable:
                # Check availability status
                availability_icon = (
                    "✅" if getattr(book, "is_available", True) else "❌"
                )
                availability_text = (
                    "Available"
                    if getattr(book, "is_available", True)
                    else "Not Available"
                )

                display_text = f"{availability_icon} {book.title}"
                detail_text = f"By: {book.author} | {availability_text}"

                item = QListWidgetItem(f"{display_text}\n{detail_text}")
                item.setData(Qt.UserRole, book)

                # Style unavailable books differently
                if not getattr(book, "is_available", True):
                    item.setBackground(Qt.lightGray)
                    item.setToolTip(
                        "This book is currently not available for borrowing"
                    )

                self.search_results.addItem(item)

    def select_book(self, item):
        self.selected_book = item.data(Qt.UserRole)

        # Check if book is available
        is_available = getattr(self.selected_book, "is_available", True)
        if not is_available:
            QMessageBox.warning(
                self,
                "Book Not Available",
                f"'{self.selected_book.title}' is currently not available for borrowing.",
            )
            return

        self.selected_label.setText(
            f"✓ {self.selected_book.title} " f"(Acc: {self.selected_book.accession_no})"
        )
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('secondary_container', '#E8F5E8')};
                border: 1px solid {COLORS.get('secondary', '#2E7D32')};
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_secondary_container', '#1B5E20')};
            }}
        """
        )
        self.search_results.clear()
        self.search_input.clear()
        self.book_selected.emit(self.selected_book)


class AddBorrowedBookForm(QWidget):
    def __init__(
        self,
        books_controller,
        borrowed_books_controller,
        patrons_controller,
        on_cancel,
        on_success,
    ):
        super().__init__()
        self.books_controller = books_controller
        self.borrowed_books_controller = borrowed_books_controller
        self.patrons_controller = patrons_controller
        self.on_cancel = on_cancel
        self.on_success = on_success

        self.selected_patron = None
        self.selected_book = None
        self.setup_ui()
        self.load_patrons()
        self.load_books()

    def setup_ui(self):
        # Main layout with padding
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Set widget background
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {COLORS.get('surface', '#FAFAFA')};
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )

        # Title section - more compact
        title_frame = QFrame()
        title_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('secondary', '#2E7D32')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        title_layout = QHBoxLayout(title_frame)

        title = QLabel("📚 Borrow Book")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {COLORS.get('on_secondary', '#FFFFFF')};
                margin: 0;
            }}
        """
        )

        subtitle = QLabel("Create a new book borrowing record")
        subtitle.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS.get('on_secondary', '#FFFFFF')};
                opacity: 0.9;
            }}
        """
        )

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(subtitle)
        main_layout.addWidget(title_frame)

        # Main content area - 3 column layout
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)

        # Left Column - Patron Selection
        patron_frame = QFrame()
        patron_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        patron_layout = QVBoxLayout(patron_frame)
        patron_layout.setSpacing(12)

        patron_title = QLabel("👤 Select Patron")
        patron_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
            }}
        """
        )
        patron_layout.addWidget(patron_title)

        self.patron_search = PatronSearchWidget()
        self.patron_search.patron_selected.connect(self.on_patron_selected)
        patron_layout.addWidget(self.patron_search)

        # Middle Column - Book Selection
        book_frame = QFrame()
        book_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('secondary', '#2E7D32')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        book_layout = QVBoxLayout(book_frame)
        book_layout.setSpacing(12)

        book_title = QLabel("📖 Select Book")
        book_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('secondary', '#2E7D32')};
                margin-bottom: 8px;
            }}
        """
        )
        book_layout.addWidget(book_title)

        self.book_search = BookSearchWidget()
        self.book_search.book_selected.connect(self.on_book_selected)
        book_layout.addWidget(self.book_search)

        # Right Column - Borrowing Details
        details_frame = QFrame()
        details_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('tertiary', '#7B1FA2')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        details_layout = QVBoxLayout(details_frame)
        details_layout.setSpacing(12)

        details_title = QLabel("📅 Borrowing Details")
        details_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('tertiary', '#7B1FA2')};
                margin-bottom: 8px;
            }}
        """
        )
        details_layout.addWidget(details_title)

        # Date inputs
        dates_grid = QGridLayout()
        dates_grid.setSpacing(12)

        # Borrow date
        borrow_label = QLabel("Borrow Date")
        borrow_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        dates_grid.addWidget(borrow_label, 0, 0)

        self.borrow_date = QDateEdit()
        self.borrow_date.setCalendarPopup(True)
        self.borrow_date.setDate(QDate.currentDate())
        self.borrow_date.setStyleSheet(
            f"""
            QDateEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-height: 16px;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
        """
        )
        dates_grid.addWidget(self.borrow_date, 1, 0)

        # Due date
        due_label = QLabel("Due Date")
        due_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        dates_grid.addWidget(due_label, 0, 1)

        self.due_date = QDateEdit()
        self.due_date.setCalendarPopup(True)
        self.due_date.setDate(QDate.currentDate().addDays(14))
        self.due_date.setStyleSheet(
            f"""
            QDateEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-height: 16px;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
        """
        )
        dates_grid.addWidget(self.due_date, 1, 1)

        details_layout.addLayout(dates_grid)

        # Borrowing period info
        self.period_info = QLabel("📋 Period: 14 days")
        self.period_info.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('tertiary_container', '#F3E5F5')};
                border: 1px solid {COLORS.get('tertiary', '#7B1FA2')};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: {COLORS.get('on_tertiary_container', '#4A148C')};
            }}
        """
        )
        details_layout.addWidget(self.period_info)

        # Notes section
        notes_label = QLabel("Notes (Optional)")
        notes_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        details_layout.addWidget(notes_label)

        self.notes = QTextEdit()
        self.notes.setMaximumHeight(60)
        self.notes.setPlaceholderText("Add notes...")
        self.notes.setStyleSheet(
            f"""
            QTextEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: white;
            }}
            QTextEdit:focus {{
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
        """
        )
        details_layout.addWidget(self.notes)

        # Add stretch to push content to top
        details_layout.addStretch()

        # Add columns to content layout
        content_layout.addWidget(patron_frame)
        content_layout.addWidget(book_frame)
        content_layout.addWidget(details_frame)

        main_layout.addWidget(content_frame)

        # Action buttons section - compact
        button_frame = QFrame()
        button_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border-top: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                margin-top: 8px;
            }}
        """
        )
        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch()

        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        save_btn = MaterialButton("📚 Create Borrow Record", button_type="elevated")
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.get('secondary', '#2E7D32')};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('secondary_variant', '#1B5E20')};
            }}
        """
        )

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        main_layout.addWidget(button_frame)

        # Connect signals
        cancel_btn.clicked.connect(self.on_cancel)
        save_btn.clicked.connect(self.save_borrowed_book)
        self.borrow_date.dateChanged.connect(self.update_due_date)

    def load_patrons(self):
        """Load all patrons from the database"""
        try:
            self.all_patrons = self.patrons_controller.get_all()
            self.patron_search.load_patrons(self.all_patrons)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load patrons: {str(e)}")

    def load_books(self):
        """Load all books from the database"""
        try:
            self.all_books = self.books_controller.get_all()
            self.book_search.load_books(self.all_books)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {str(e)}")

    def on_patron_selected(self, patron):
        """Handle patron selection"""
        self.selected_patron = patron
        self.update_borrowing_info()

    def on_book_selected(self, book):
        """Handle book selection"""
        self.selected_book = book
        self.update_borrowing_info()

    def update_due_date(self):
        """Update due date when borrow date changes"""
        borrow_date = self.borrow_date.date()
        due_date = borrow_date.addDays(14)  # 14 days borrowing period
        self.due_date.setDate(due_date)

        # Update period info
        days = borrow_date.daysTo(due_date)
        self.period_info.setText(
            f"📋 Period: {days} days (Due: {due_date.toString('MMM dd')})"
        )

    def update_borrowing_info(self):
        """Update borrowing information display"""
        if self.selected_patron and self.selected_book:
            # Check if patron has active membership for certain book types
            if hasattr(self.selected_patron, "membership_status"):
                if self.selected_patron.membership_status != "active":
                    # Show warning for non-members
                    self.period_info.setText("⚠️ Patron doesn't have active membership")
                    self.period_info.setStyleSheet(
                        f"""
                        QLabel {{
                            background-color: {COLORS.get('error_container', '#FFEBEE')};
                            border: 1px solid {COLORS.get('error', '#D32F2F')};
                            border-radius: 6px;
                            padding: 8px;
                            font-size: 12px;
                            color: {COLORS.get('on_error_container', '#C62828')};
                        }}
                    """
                    )

    def validate_form(self) -> list[str]:
        """Validate form data before saving"""
        errors = []

        if not self.selected_patron:
            errors.append("Please select a patron")

        if not self.selected_book:
            errors.append("Please select a book")

        # Check if book is available
        if self.selected_book and not getattr(self.selected_book, "is_available", True):
            errors.append(
                f"Book '{self.selected_book.title}' is not available for borrowing"
            )

        # ✅ Convert QDate -> datetime.date
        borrow_date = self.borrow_date.date().toPyDate()
        due_date = self.due_date.date().toPyDate()

        # Validate dates
        if due_date <= borrow_date:
            errors.append("Due date must be after borrow date")

        # Check if borrow date is not in the future
        today = datetime.now().date()
        if borrow_date > today:
            errors.append("Borrow date cannot be in the future")

        # Check reasonable borrowing period (not more than 30 days)
        borrowing_days = (due_date - borrow_date).days
        if borrowing_days > 30:
            errors.append("Borrowing period cannot exceed 30 days")

        return errors

    def save_borrowed_book(self):
        """Save borrowing record with comprehensive validation"""
        # Validate form
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fix the following issues:\n\n"
                + "\n".join(f"• {error}" for error in errors),
            )
            return

        # Prepare borrowing data
        borrow_data = {
            "user_id": self.selected_patron.user_id,
            "book_id": self.selected_book.book_id,
            "borrow_date": self.borrow_date.date().toString("yyyy-MM-dd"),
            "due_date": self.due_date.date().toString("yyyy-MM-dd"),
            "returned": False,
            "notes": (
                self.notes.toPlainText().strip()
                if self.notes.toPlainText().strip()
                else None
            ),
        }

        # Save through controller
        try:
            result = self.borrowed_books_controller.create(borrow_data)
            if result.get("success", False):
                # Show success message with book and patron info
                success_msg = (
                    f"Book borrowed successfully!\n\n"
                    f"📖 Book: {self.selected_book.title}\n"
                    f"👤 Patron: {self.selected_patron.first_name} {self.selected_patron.last_name}\n"
                    f"📅 Due Date: {self.due_date.date().toString('MMM dd, yyyy')}"
                )
                QMessageBox.information(self, "Success", success_msg)
                self.on_success()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    result.get("message", "Failed to create borrow record"),
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def reset_form(self):
        """Reset form to initial state"""
        self.selected_patron = None
        self.selected_book = None

        # Reset patron search
        self.patron_search.selected_patron = None
        self.patron_search.selected_label.setText("No patron selected")
        self.patron_search.search_input.clear()
        self.patron_search.search_results.clear()

        # Reset book search
        self.book_search.selected_book = None
        self.book_search.selected_label.setText("No book selected")
        self.book_search.search_input.clear()
        self.book_search.search_results.clear()

        # Reset dates
        self.borrow_date.setDate(QDate.currentDate())
        self.due_date.setDate(QDate.currentDate().addDays(14))

        # Reset notes
        self.notes.clear()

        # Reset period info
        self.period_info.setText("📋 Period: 14 days")
        self.period_info.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('tertiary_container', '#F3E5F5')};
                border: 1px solid {COLORS.get('tertiary', '#7B1FA2')};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                color: {COLORS.get('on_tertiary_container', '#4A148C')};
            }}
        """
        )

    def check_patron_borrowing_limits(self) -> bool:
        """Check if patron has reached borrowing limits"""
        if not self.selected_patron:
            return False

        try:
            # Get current borrowed books count for this patron
            current_borrows = self.borrowed_books_controller.get_active_borrows_count(
                self.selected_patron.user_id
            )

            # Set borrowing limits based on patron type
            limits = {"pupil": 3, "student": 5, "adult": 7}

            patron_limit = limits.get(self.selected_patron.grade_level.lower(), 3)

            if current_borrows >= patron_limit:
                QMessageBox.warning(
                    self,
                    "Borrowing Limit Reached",
                    f"Patron has reached the borrowing limit of {patron_limit} books.\n"
                    f"Current borrowed books: {current_borrows}\n\n"
                    "Please return some books before borrowing new ones.",
                )
                return False

            return True

        except Exception as e:
            print(f"Error checking borrowing limits: {e}")
            return True  # Allow borrowing if we can't check limits
