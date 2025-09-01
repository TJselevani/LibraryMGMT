# ui/screens/login_window.py
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QCheckBox,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor
from utils.constants import COLORS


class MaterialLineEdit(QLineEdit):
    """Custom QLineEdit with Material Design styling and floating label effect"""

    def __init__(self, placeholder_text="", parent=None):
        super().__init__(parent)
        self.placeholder_text = placeholder_text
        self.setup_style()

    def setup_style(self):
        self.setStyleSheet(
            f"""
            QLineEdit {{
                border: none;
                border-bottom: 2px solid {COLORS.get('outline', '#E0E0E0')};
                padding: 12px 0px 8px 0px;
                font-size: 16px;
                background-color: transparent;
                color: {COLORS.get('on_surface', '#000000')};
            }}
            QLineEdit:focus {{
                border-bottom: 2px solid {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        self.setPlaceholderText(self.placeholder_text)
        self.setMinimumHeight(40)


class MaterialButton(QPushButton):
    """Custom QPushButton with Material Design styling"""

    def __init__(self, text, button_type="filled", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.setup_style()

    def setup_style(self):
        if self.button_type == "filled":
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {COLORS.get('primary', '#1976D2')};
                    color: {COLORS.get('on_primary', '#FFFFFF')};
                    border: none;
                    border-radius: 24px;
                    padding: 12px 32px;
                    font-size: 16px;
                    font-weight: 600;
                    min-height: 24px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS.get('primary_variant', '#1565C0')};
                }}
                QPushButton:pressed {{
                    background-color: {COLORS.get('primary_dark', '#0D47A1')};
                }}
                QPushButton:disabled {{
                    background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                    color: {COLORS.get('on_surface_variant', '#999999')};
                }}
            """
            )
        elif self.button_type == "text":
            self.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS.get('primary', '#1976D2')};
                    border: none;
                    padding: 8px 16px;
                    font-size: 14px;
                    font-weight: 500;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS.get('primary_container', '#E3F2FD')};
                }}
            """
            )


class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Library Management System")
        self.setFixedSize(500, 650)
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint)

        # Set window background
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.get('primary', '#1976D2')}, 
                    stop:0.3 {COLORS.get('primary_variant', '#1565C0')},
                    stop:1 {COLORS.get('secondary', '#2E7D32')});
            }}
        """
        )

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 20)

        # Top section with branding
        # self.create_header_section(main_layout)

        # Login form card
        self.create_login_card(main_layout)

        # Footer section
        # self.create_footer_section(main_layout)

    def create_header_section(self, parent_layout):
        """Create the header section with branding"""
        header_widget = QWidget()
        header_widget.setFixedHeight(150)
        header_widget.setStyleSheet("background-color: transparent;")

        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        # Library icon/logo placeholder
        logo_label = QLabel("📚")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet(
            """
            QLabel {
                font-size: 48px;
                color: white;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 35px;
                padding: 20px;
                max-width: 70px;
                max-height: 70px;
            }
        """
        )
        logo_label.setFixedSize(70, 70)

        logo_container = QHBoxLayout()
        logo_container.addStretch()
        logo_container.addWidget(logo_label)
        logo_container.addStretch()
        header_layout.addLayout(logo_container)

        # Title
        title_label = QLabel("Library Management")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 28px;
                font-weight: 300;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                margin: 8px 0px;
            }}
        """
        )
        header_layout.addWidget(title_label)

        # Subtitle
        subtitle_label = QLabel("Streamline your library operations")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                opacity: 0.8;
            }}
        """
        )
        header_layout.addWidget(subtitle_label)

        parent_layout.addWidget(header_widget)

    def create_login_card(self, parent_layout):
        """Create the main login card"""
        # Container for card with margins
        card_container = QWidget()
        card_container.setStyleSheet("background-color: transparent;")
        container_layout = QVBoxLayout(card_container)
        container_layout.setContentsMargins(32, 20, 32, 20)

        # Main login card
        self.login_card = QFrame()
        self.login_card.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border-radius: 16px;
                border: none;
            }}
        """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.login_card.setGraphicsEffect(shadow)

        # Card layout
        card_layout = QVBoxLayout(self.login_card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(24)

        # Welcome text
        welcome_label = QLabel("Welcome Back")
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                font-weight: 600;
                color: {COLORS.get('on_surface', '#000000')};
                margin-bottom: 8px;
            }}
        """
        )
        card_layout.addWidget(welcome_label)

        signin_label = QLabel("Sign in to your account")
        signin_label.setAlignment(Qt.AlignCenter)
        signin_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS.get('on_surface_variant', '#666666')};
                margin-bottom: 16px;
            }}
        """
        )
        card_layout.addWidget(signin_label)

        # Form fields
        self.create_form_fields(card_layout)

        container_layout.addWidget(self.login_card)
        parent_layout.addWidget(card_container, 1)

    def create_form_fields(self, card_layout):
        """Create the form input fields"""
        # Username field
        username_container = QWidget()
        username_layout = QVBoxLayout(username_container)
        username_layout.setContentsMargins(2, 2, 2, 2)
        username_layout.setSpacing(8)

        username_label = QLabel("Username")
        username_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        username_layout.addWidget(username_label)

        self.username_input = MaterialLineEdit("Enter your username")
        self.username_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        username_layout.addWidget(self.username_input)
        card_layout.addWidget(username_container)

        # Password field
        password_container = QWidget()
        password_layout = QVBoxLayout(password_container)
        password_layout.setContentsMargins(0, 0, 0, 0)
        password_layout.setSpacing(8)

        password_label = QLabel("Password")
        password_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        password_layout.addWidget(password_label)

        self.password_input = MaterialLineEdit("Enter your password")
        self.password_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(self.password_input)
        card_layout.addWidget(password_container)

        # Remember me and forgot password row
        options_layout = QHBoxLayout()
        options_layout.setContentsMargins(0, 8, 0, 8)

        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: 14px;
                color: {COLORS.get('on_surface_variant', '#666666')};
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 3px;
                background-color: transparent;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS.get('primary', '#1976D2')};
                border-color: {COLORS.get('primary', '#1976D2')};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04LjMzMzMzIDAuNUw0IDE0Ljc1TDEuNjY2NjcgMi41IiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
        """
        )
        options_layout.addWidget(self.remember_checkbox)

        options_layout.addStretch()

        forgot_btn = MaterialButton("Forgot Password?", button_type="text")
        forgot_btn.clicked.connect(self.show_forgot_password)
        options_layout.addWidget(forgot_btn)

        card_layout.addLayout(options_layout)

        # Login button
        self.login_button = MaterialButton("Sign In", button_type="filled")
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)

        # Connect Enter key to login
        self.username_input.returnPressed.connect(self.handle_login)
        self.password_input.returnPressed.connect(self.handle_login)

        # Status message
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                padding: 8px;
                border-radius: 6px;
                background-color: transparent;
            }
        """
        )
        self.status_label.hide()
        card_layout.addWidget(self.status_label)

    def create_footer_section(self, parent_layout):
        """Create footer section"""
        footer_widget = QWidget()
        footer_widget.setFixedHeight(100)
        footer_widget.setStyleSheet("background-color: transparent;")

        footer_layout = QVBoxLayout(footer_widget)
        footer_layout.setContentsMargins(32, 20, 32, 20)
        footer_layout.setSpacing(8)

        # Demo credentials info
        demo_frame = QFrame()
        demo_frame.setStyleSheet(
            """
            QFrame {{
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 8px;
                padding: 12px;
            }}
        """
        )
        demo_layout = QVBoxLayout(demo_frame)
        demo_layout.setContentsMargins(16, 12, 16, 12)
        demo_layout.setSpacing(4)

        demo_title = QLabel("Demo Credentials")
        demo_title.setAlignment(Qt.AlignCenter)
        demo_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 12px;
                font-weight: 600;
                color: {COLORS.get('on_primary', '#FFFFFF')};
            }}
        """
        )
        demo_layout.addWidget(demo_title)

        demo_info = QLabel("Username: admin • Password: admin123")
        demo_info.setAlignment(Qt.AlignCenter)
        demo_info.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                opacity: 0.8;
            }}
        """
        )
        demo_layout.addWidget(demo_info)

        footer_layout.addWidget(demo_frame)
        parent_layout.addWidget(footer_widget)

    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_message("Please enter both username and password", "error")
            return

        # Disable UI during authentication
        self.set_login_state(False)

        # Attempt authentication
        result = self.auth_service.authenticate_user(username, password)

        if result["success"]:
            self.show_message("Login successful! Redirecting...", "success")
            # Small delay for UX
            QTimer.singleShot(500, lambda: self.login_successful.emit(result["user"]))
        else:
            self.show_message(result["message"], "error")
            self.password_input.clear()
            self.password_input.setFocus()
            self.set_login_state(True)

    def set_login_state(self, enabled):
        """Enable/disable login UI elements"""
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.login_button.setEnabled(enabled)

        if enabled:
            self.login_button.setText("Sign In")
        else:
            self.login_button.setText("Signing in...")

    def show_message(self, message, msg_type="info"):
        """Show status message with appropriate styling"""
        self.status_label.setText(message)
        self.status_label.show()

        if msg_type == "error":
            self.status_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 13px;
                    padding: 8px 12px;
                    border-radius: 6px;
                    background-color: {COLORS.get('error_container', '#FFEBEE')};
                    color: {COLORS.get('error', '#D32F2F')};
                    border: 1px solid {COLORS.get('error', '#D32F2F')};
                }}
            """
            )
        elif msg_type == "success":
            self.status_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 13px;
                    padding: 8px 12px;
                    border-radius: 6px;
                    background-color: {COLORS.get('success_container', '#E8F5E8')};
                    color: {COLORS.get('success', '#2E7D32')};
                    border: 1px solid {COLORS.get('success', '#2E7D32')};
                }}
            """
            )
        else:
            self.status_label.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 13px;
                    padding: 8px 12px;
                    border-radius: 6px;
                    background-color: {COLORS.get('primary_container', '#E3F2FD')};
                    color: {COLORS.get('primary', '#1976D2')};
                    border: 1px solid {COLORS.get('primary', '#1976D2')};
                }}
            """
            )

    def show_forgot_password(self):
        """Handle forgot password click"""
        from PyQt5.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Forgot Password",
            "Please contact your system administrator to reset your password.",
        )

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)
