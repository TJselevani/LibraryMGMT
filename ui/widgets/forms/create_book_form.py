from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFrame,
    QCheckBox,
    QGridLayout,
    QComboBox,
)
from PyQt5.QtCore import pyqtSignal
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


class MaterialInputField(QFrame):
    """Compact Material Design styled input field"""

    def __init__(
        self, label_text, placeholder_text="", field_type="text", required=True
    ):
        super().__init__()
        self.label_text = label_text
        self.placeholder_text = placeholder_text
        self.field_type = field_type
        self.required = required
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 8)
        layout.setSpacing(6)

        # Field label
        self.label = QLabel(self.label_text + (" *" if self.required else ""))
        self.label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 2px;
            }}
        """
        )
        layout.addWidget(self.label)

        # Input field
        if self.field_type == "combo":
            self.input_field = QComboBox()
        else:
            self.input_field = QLineEdit()
            self.input_field.setPlaceholderText(self.placeholder_text)

        # Common styling for input fields
        input_style = f"""
            QLineEdit, QComboBox {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: {COLORS.get('surface', '#FFFFFF')};
                color: {COLORS.get('on_surface', '#000000')};
                min-height: 16px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: {COLORS.get('surface', '#FFFFFF')};
                outline: none;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS.get('primary', '#1976D2')};
                margin-right: 5px;
            }}
        """
        self.input_field.setStyleSheet(input_style)
        layout.addWidget(self.input_field)

        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet(
            f"""
            QLabel {{
                color: {COLORS.get('error', '#D32F2F')};
                font-size: 11px;
                font-weight: 500;
                margin-top: 2px;
            }}
        """
        )
        self.error_label.hide()
        layout.addWidget(self.error_label)

    def get_value(self):
        """Get the current value of the input field"""
        if isinstance(self.input_field, QComboBox):
            return self.input_field.currentText()
        return self.input_field.text().strip()

    def set_value(self, value):
        """Set the value of the input field"""
        if isinstance(self.input_field, QComboBox):
            index = self.input_field.findText(value)
            if index >= 0:
                self.input_field.setCurrentIndex(index)
        else:
            self.input_field.setText(value)

    def add_items(self, items):
        """Add items to combo box"""
        if isinstance(self.input_field, QComboBox):
            self.input_field.addItems(items)

    def set_error(self, error_message):
        """Show error message"""
        if error_message:
            self.error_label.setText(error_message)
            self.error_label.show()
            self.input_field.setStyleSheet(
                f"""
                QLineEdit, QComboBox {{
                    border: 2px solid {COLORS.get('error', '#D32F2F')};
                    border-radius: 8px;
                    padding: 12px 16px;
                    font-size: 14px;
                    background-color: {COLORS.get('error_container', '#FFEBEE')};
                    color: {COLORS.get('on_surface', '#000000')};
                    min-height: 16px;
                }}
            """
            )
        else:
            self.clear_error()

    def clear_error(self):
        """Clear error message"""
        self.error_label.hide()
        input_style = f"""
            QLineEdit, QComboBox {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: {COLORS.get('surface', '#FFFFFF')};
                color: {COLORS.get('on_surface', '#000000')};
                min-height: 16px;
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: {COLORS.get('surface', '#FFFFFF')};
                outline: none;
            }}
        """
        self.input_field.setStyleSheet(input_style)


class AddBookForm(QWidget):
    """Compact Material Design styled Add Book form with 2 columns"""

    book_added = pyqtSignal()

    def __init__(self, books_controller, on_cancel, on_success):
        super().__init__()
        self.books_controller = books_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)

        self.setStyleSheet(f"background-color: {COLORS.get('background', '#FAFAFA')};")

        # Header section
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)

        # Form section
        form_frame = self.create_form_section()
        main_layout.addWidget(form_frame)

        # Action buttons
        action_frame = self.create_action_section()
        main_layout.addWidget(action_frame)

    def create_header(self):
        """Create compact header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.get('primary', '#1976D2')}, 
                    stop:1 {COLORS.get('primary_variant', '#1565C0')});
                border-radius: 16px;
                padding: 20px 24px;
            }}
        """
        )

        header_layout = QHBoxLayout(header_frame)

        # Left side - Title and subtitle
        left_layout = QVBoxLayout()

        title = QLabel("Add New Book")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                margin-bottom: 4px;
            }}
        """
        )
        left_layout.addWidget(title)

        subtitle = QLabel("Enter book details to add to library collection")
        subtitle.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                opacity: 0.9;
            }}
        """
        )
        left_layout.addWidget(subtitle)

        header_layout.addLayout(left_layout)
        header_layout.addStretch()

        return header_frame

    def create_form_section(self):
        """Create compact 2-column form section"""
        form_frame = QFrame()
        form_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('outline_variant', '#E0E0E0')};
                border-radius: 16px;
                padding: 24px;
            }}
        """
        )

        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(16)

        # Section title
        section_title = QLabel("Book Information")
        section_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 18px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
                padding-bottom: 6px;
                border-bottom: 2px solid {COLORS.get('primary_container', '#E3F2FD')};
            }}
        """
        )
        form_layout.addWidget(section_title)

        # Create form fields in a 2-column grid
        fields_layout = QGridLayout()
        fields_layout.setSpacing(16)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        # Row 0: Title (spans both columns)
        self.title_field = MaterialInputField(
            "Book Title", "Enter the book title", required=True
        )
        fields_layout.addWidget(self.title_field, 0, 0, 1, 2)

        # Row 1: Author and Class Name
        self.author_field = MaterialInputField(
            "Author", "Enter author's name", required=True
        )
        fields_layout.addWidget(self.author_field, 1, 0)

        self.class_name_field = MaterialInputField(
            "Class/Subject", "e.g., Mathematics", required=False
        )
        fields_layout.addWidget(self.class_name_field, 1, 1)

        # Row 2: Accession Number and ISBN
        self.accession_no_field = MaterialInputField(
            "Accession Number", "Unique identifier", required=True
        )
        fields_layout.addWidget(self.accession_no_field, 2, 0)

        self.isbn_field = MaterialInputField("ISBN", "10 or 13 digits", required=False)
        fields_layout.addWidget(self.isbn_field, 2, 1)

        form_layout.addLayout(fields_layout)

        # Options section
        options_layout = QHBoxLayout()

        # Availability checkbox
        self.availability_checkbox = QCheckBox("Available for borrowing")
        self.availability_checkbox.setChecked(True)
        self.availability_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: 14px;
                color: {COLORS.get('on_surface', '#000000')};
                font-weight: 500;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                background-color: {COLORS.get('surface', '#FFFFFF')};
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS.get('primary', '#1976D2')};
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        options_layout.addWidget(self.availability_checkbox)
        options_layout.addStretch()

        form_layout.addLayout(options_layout)

        return form_frame

    def create_action_section(self):
        """Create compact action buttons section"""
        action_frame = QFrame()
        action_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('outline_variant', '#E0E0E0')};
                border-radius: 12px;
                padding: 16px 20px;
            }}
        """
        )

        action_layout = QHBoxLayout(action_frame)
        action_layout.setSpacing(12)

        # Clear button
        clear_btn = MaterialButton("Clear", button_type="text")
        clear_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS.get('on_surface_variant', '#666666')};
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 500;
                min-width: 80px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )

        # Cancel button
        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        cancel_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: transparent;
                color: {COLORS.get('primary', '#1976D2')};
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 8px;
                padding: 10px 24px;
                font-size: 14px;
                font-weight: 600;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
            }}
        """
        )

        # Save button
        save_btn = MaterialButton("Save Book", button_type="filled")
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS.get('primary', '#1976D2')}, 
                    stop:1 {COLORS.get('primary_variant', '#1565C0')});
                color: {COLORS.get('on_primary', '#FFFFFF')};
                border: none;
                border-radius: 8px;
                padding: 12px 32px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS.get('primary_variant', '#1565C0')}, 
                    stop:1 {COLORS.get('primary', '#1976D2')});
            }}
        """
        )

        # Add buttons to layout
        action_layout.addWidget(clear_btn)
        action_layout.addStretch()
        action_layout.addWidget(cancel_btn)
        action_layout.addWidget(save_btn)

        # Connect button signals
        clear_btn.clicked.connect(self.clear_form)
        cancel_btn.clicked.connect(self.on_cancel)
        save_btn.clicked.connect(self.save_book)

        return action_frame

    def clear_form(self):
        """Clear all form fields"""
        self.title_field.set_value("")
        self.author_field.set_value("")
        self.class_name_field.set_value("")
        self.accession_no_field.set_value("")
        self.isbn_field.set_value("")
        self.availability_checkbox.setChecked(True)
        self.clear_all_errors()

    def clear_all_errors(self):
        """Clear all error messages from form fields"""
        self.title_field.clear_error()
        self.author_field.clear_error()
        self.class_name_field.clear_error()
        self.accession_no_field.clear_error()
        self.isbn_field.clear_error()

    def validate_form(self):
        """Validate form data and show errors"""
        is_valid = True
        self.clear_all_errors()

        # Validate title
        if not self.title_field.get_value():
            self.title_field.set_error("Book title is required")
            is_valid = False

        # Validate author
        if not self.author_field.get_value():
            self.author_field.set_error("Author name is required")
            is_valid = False

        # Validate accession number
        if not self.accession_no_field.get_value():
            self.accession_no_field.set_error("Accession number is required")
            is_valid = False

        # Validate ISBN format if provided
        isbn = self.isbn_field.get_value()
        if isbn and len(isbn.replace("-", "")) not in [10, 13]:
            self.isbn_field.set_error("ISBN must be 10 or 13 digits")
            is_valid = False

        return is_valid

    def save_book(self):
        """Save the book after validation"""
        if not self.validate_form():
            return

        # Collect form data
        data = {
            "title": self.title_field.get_value(),
            "author": self.author_field.get_value(),
            "class_name": self.class_name_field.get_value() or None,
            "accession_no": self.accession_no_field.get_value(),
            "isbn": self.isbn_field.get_value() or None,
            "is_available": self.availability_checkbox.isChecked(),
        }

        try:
            result = self.books_controller.create(data)

            if result["success"]:
                QMessageBox.information(
                    self,
                    "Success",
                    f"Book '{data['title']}' has been added successfully!",
                )
                self.clear_form()
                self.book_added.emit()
                self.on_success()
            else:
                QMessageBox.warning(self, "Error", result["message"])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save book: {str(e)}")
