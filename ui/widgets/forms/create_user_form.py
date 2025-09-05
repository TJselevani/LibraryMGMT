from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QFrame,
    QGridLayout,
    QComboBox,
)
from PyQt5.QtCore import pyqtSignal
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


class MaterialInputField(QFrame):
    """Material Design styled input field"""

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
        elif self.field_type == "password":
            self.input_field = QLineEdit()
            self.input_field.setEchoMode(QLineEdit.Password)
            self.input_field.setPlaceholderText(self.placeholder_text)
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
            QLineEdit::placeholder {{
                color: {COLORS.get('on_surface_variant', '#666666')};
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


class AddUserForm(QWidget):
    """Material Design styled Add User form with 2 columns"""

    user_added = pyqtSignal()

    def __init__(self, users_controller, on_cancel, on_success):
        super().__init__()
        self.users_controller = users_controller
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
        """Create header section"""
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

        title = QLabel("Add New User")
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

        subtitle = QLabel("Create a new user account with access permissions")
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

        # Right side - User icon or stats
        user_icon = QLabel("👤")
        user_icon.setStyleSheet(
            f"""
            QLabel {{
                font-size: 32px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 24px;
                padding: 8px 12px;
                margin-left: 16px;
            }}
        """
        )
        header_layout.addWidget(user_icon)

        return header_frame

    def create_form_section(self):
        """Create 2-column form section"""
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
        form_layout.setSpacing(20)

        # Personal Information Section
        personal_section = self.create_personal_section()
        form_layout.addWidget(personal_section)

        # Account Information Section
        account_section = self.create_account_section()
        form_layout.addWidget(account_section)

        return form_frame

    def create_personal_section(self):
        """Create personal information section"""
        section_frame = QFrame()
        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(16)

        # Section title
        section_title = QLabel("Personal Information")
        section_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
                padding-bottom: 6px;
                border-bottom: 2px solid {COLORS.get('primary_container', '#E3F2FD')};
            }}
        """
        )
        section_layout.addWidget(section_title)

        # Create form fields in a 2-column grid
        fields_layout = QGridLayout()
        fields_layout.setSpacing(16)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        # Row 0: Full Name (spans both columns)
        self.full_name_field = MaterialInputField(
            "Full Name", "Enter full name", required=True
        )
        fields_layout.addWidget(self.full_name_field, 0, 0, 1, 2)

        # Row 1: Email and Phone Number
        self.email_field = MaterialInputField(
            "Email Address", "user@example.com", required=True
        )
        fields_layout.addWidget(self.email_field, 1, 0)

        self.phone_field = MaterialInputField(
            "Phone Number", "+254 xxx xxx xxx", required=False
        )
        fields_layout.addWidget(self.phone_field, 1, 1)

        section_layout.addLayout(fields_layout)
        return section_frame

    def create_account_section(self):
        """Create account information section"""
        section_frame = QFrame()
        section_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface_variant', '#F8F9FA')};
                border: 1px solid {COLORS.get('outline_variant', '#E8EAED')};
                border-radius: 12px;
                padding: 20px;
                margin-top: 8px;
            }}
        """
        )

        section_layout = QVBoxLayout(section_frame)
        section_layout.setSpacing(16)

        # Section title
        section_title = QLabel("Account Credentials")
        section_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
                padding-bottom: 6px;
                border-bottom: 2px solid {COLORS.get('primary_container', '#E3F2FD')};
            }}
        """
        )
        section_layout.addWidget(section_title)

        # Create form fields in a 2-column grid
        fields_layout = QGridLayout()
        fields_layout.setSpacing(16)
        fields_layout.setColumnStretch(0, 1)
        fields_layout.setColumnStretch(1, 1)

        # Row 0: Username and Role
        self.username_field = MaterialInputField(
            "Username", "Enter username", required=True
        )
        fields_layout.addWidget(self.username_field, 0, 0)

        self.role_field = MaterialInputField(
            "User Role", field_type="combo", required=True
        )
        self.role_field.add_items(["Assistant", "Librarian", "Admin"])
        fields_layout.addWidget(self.role_field, 0, 1)

        # Row 1: Password (spans both columns for better UX)
        self.password_field = MaterialInputField(
            "Password", "Enter secure password", field_type="password", required=True
        )
        fields_layout.addWidget(self.password_field, 1, 0, 1, 2)

        section_layout.addLayout(fields_layout)

        # Password requirements note
        password_note = QLabel(
            "• Password should be at least 8 characters long\n• Include letters, numbers, and special characters"
        )
        password_note.setStyleSheet(
            f"""
            QLabel {{
                font-size: 12px;
                color: {COLORS.get('on_surface_variant', '#666666')};
                background-color: {COLORS.get('info_container', '#E3F2FD')};
                border: 1px solid {COLORS.get('info', '#2196F3')};
                border-radius: 8px;
                padding: 8px 12px;
                margin-top: 8px;
            }}
        """
        )
        section_layout.addWidget(password_note)

        return section_frame

    def create_action_section(self):
        """Create action buttons section"""
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
        save_btn = MaterialButton("Create User", button_type="filled")
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
        save_btn.clicked.connect(self.save_user)

        return action_frame

    def clear_form(self):
        """Clear all form fields"""
        self.full_name_field.set_value("")
        self.email_field.set_value("")
        self.phone_field.set_value("")
        self.username_field.set_value("")
        self.password_field.set_value("")
        self.role_field.set_value("Assistant")
        self.clear_all_errors()

    def clear_all_errors(self):
        """Clear all error messages from form fields"""
        self.full_name_field.clear_error()
        self.email_field.clear_error()
        self.phone_field.clear_error()
        self.username_field.clear_error()
        self.password_field.clear_error()
        self.role_field.clear_error()

    def validate_form(self):
        """Validate form data and show errors"""
        is_valid = True
        self.clear_all_errors()

        # Validate full name
        if not self.full_name_field.get_value():
            self.full_name_field.set_error("Full name is required")
            is_valid = False

        # Validate email
        email = self.email_field.get_value()
        if not email:
            self.email_field.set_error("Email is required")
            is_valid = False
        elif "@" not in email or "." not in email:
            self.email_field.set_error("Please enter a valid email address")
            is_valid = False

        # Validate username
        username = self.username_field.get_value()
        if not username:
            self.username_field.set_error("Username is required")
            is_valid = False
        elif len(username) < 3:
            self.username_field.set_error("Username must be at least 3 characters")
            is_valid = False

        # Validate password
        password = self.password_field.get_value()
        if not password:
            self.password_field.set_error("Password is required")
            is_valid = False
        elif len(password) < 8:
            self.password_field.set_error("Password must be at least 8 characters")
            is_valid = False

        # Validate phone number format if provided
        phone = self.phone_field.get_value()
        if (
            phone
            and not phone.replace("+", "").replace(" ", "").replace("-", "").isdigit()
        ):
            self.phone_field.set_error("Please enter a valid phone number")
            is_valid = False

        return is_valid

    def save_user(self):
        """Save the user after validation"""
        if not self.validate_form():
            return

        # Collect form data
        data = {
            "username": self.username_field.get_value(),
            "email": self.email_field.get_value(),
            "phone_number": self.phone_field.get_value() or None,
            "password": self.password_field.get_value(),
            "full_name": self.full_name_field.get_value(),
            "role": self.role_field.get_value().upper(),
        }

        try:
            result = self.users_controller.create(data)

            if result["success"]:
                # Show success message with Material Design styling
                msg = QMessageBox(self)
                msg.setWindowTitle("Success")
                msg.setText("User Created Successfully!")
                msg.setInformativeText(
                    f"User '{data['username']}' has been created with {data['role'].lower()} privileges."
                )
                msg.setIcon(QMessageBox.Information)
                msg.setStyleSheet(
                    f"""
                    QMessageBox {{
                        background-color: {COLORS.get('surface', '#FFFFFF')};
                        color: {COLORS.get('on_surface', '#000000')};
                    }}
                    QMessageBox QPushButton {{
                        background-color: {COLORS.get('primary', '#1976D2')};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 16px;
                        font-weight: 600;
                        min-width: 80px;
                    }}
                    QMessageBox QPushButton:hover {{
                        background-color: {COLORS.get('primary_variant', '#1565C0')};
                    }}
                """
                )
                msg.exec_()

                # Clear form and emit success signal
                self.clear_form()
                self.user_added.emit()
                self.on_success()

            else:
                # Show error message
                QMessageBox.warning(self, "Error", result["message"])

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create user: {str(e)}")
