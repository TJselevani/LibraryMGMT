from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QCheckBox,
)
from PyQt5.QtCore import Qt, pyqtSignal

# from PyQt5.QtGui import QFont, QPixmap, QIcon


class LoginWindow(QMainWindow):
    login_successful = pyqtSignal(dict)  # Signal emitted when login is successful

    def __init__(self, auth_service):
        super().__init__()
        self.auth_service = auth_service
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Library Management System - Login")
        self.setFixedSize(400, 500)
        self.setStyleSheet(self.get_stylesheet())

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Header
        header_layout = QVBoxLayout()

        # Logo/Title
        title_label = QLabel("Library Management System")
        title_label.setObjectName("title")
        title_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(title_label)

        subtitle_label = QLabel("Please sign in to continue")
        subtitle_label.setObjectName("subtitle")
        subtitle_label.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(subtitle_label)

        main_layout.addLayout(header_layout)

        # Login form
        form_frame = QFrame()
        form_frame.setObjectName("form_frame")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        # Username field
        username_label = QLabel("Username:")
        username_label.setObjectName("field_label")
        form_layout.addWidget(username_label)

        self.username_input = QLineEdit()
        self.username_input.setObjectName("input_field")
        self.username_input.setPlaceholderText("Enter your username")
        self.username_input.returnPressed.connect(self.handle_login)
        form_layout.addWidget(self.username_input)

        # Password field
        password_label = QLabel("Password:")
        password_label.setObjectName("field_label")
        form_layout.addWidget(password_label)

        self.password_input = QLineEdit()
        self.password_input.setObjectName("input_field")
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.returnPressed.connect(self.handle_login)
        form_layout.addWidget(self.password_input)

        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setObjectName("checkbox")
        form_layout.addWidget(self.remember_checkbox)

        # Login button
        self.login_button = QPushButton("Sign In")
        self.login_button.setObjectName("login_button")
        self.login_button.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_button)

        # Status label for messages
        self.status_label = QLabel("")
        self.status_label.setObjectName("status_label")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        form_layout.addWidget(self.status_label)

        main_layout.addWidget(form_frame)

        # Default credentials info
        info_label = QLabel("Default admin: username='admin', password='admin123'")
        info_label.setObjectName("info_label")
        info_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(info_label)

        # Set focus to username input
        self.username_input.setFocus()

    def handle_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text()

        if not username or not password:
            self.show_message("Please enter both username and password", "error")
            return

        # Disable login button during authentication
        self.login_button.setEnabled(False)
        self.login_button.setText("Signing in...")

        # Attempt authentication
        result = self.auth_service.authenticate_user(username, password)

        if result["success"]:
            self.show_message(result["message"], "success")
            self.login_successful.emit(result["user"])
        else:
            self.show_message(result["message"], "error")
            self.password_input.clear()
            self.password_input.setFocus()

        # Re-enable login button
        self.login_button.setEnabled(True)
        self.login_button.setText("Sign In")

    def show_message(self, message, msg_type="info"):
        """Show status message"""
        self.status_label.setText(message)
        if msg_type == "error":
            self.status_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        elif msg_type == "success":
            self.status_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.status_label.setStyleSheet("color: #3498db; font-weight: bold;")

    def get_stylesheet(self):
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            
            #title {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            
            #subtitle {
                font-size: 14px;
                color: #7f8c8d;
                margin-bottom: 20px;
            }
            
            #form_frame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            
            #field_label {
                font-size: 12px;
                font-weight: bold;
                color: #34495e;
                margin-bottom: 5px;
            }
            
            #input_field {
                padding: 12px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 14px;
                background-color: #fff;
            }
            
            #input_field:focus {
                border-color: #3498db;
                outline: none;
            }
            
            #checkbox {
                font-size: 12px;
                color: #7f8c8d;
            }
            
            #login_button {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            
            #login_button:hover {
                background-color: #2980b9;
            }
            
            #login_button:pressed {
                background-color: #21618c;
            }
            
            #login_button:disabled {
                background-color: #95a5a6;
            }
            
            #status_label {
                font-size: 12px;
                margin-top: 10px;
                padding: 8px;
                border-radius: 4px;
            }
            
            #info_label {
                font-size: 11px;
                color: #95a5a6;
                font-style: italic;
            }
        """
