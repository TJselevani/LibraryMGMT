from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    # QDateEdit,
    QComboBox,
    QMessageBox,
)

# from PyQt5.QtCore import QDate
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


class AddUserForm(QWidget):
    def __init__(self, users_controller, on_cancel, on_success):
        super().__init__()
        self.users_controller = users_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Add New User")
        title.setStyleSheet(f"font-size: 28px; color: {COLORS['on_surface']};")
        layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.email = QLineEdit()
        self.email.setPlaceholderText("Email")

        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Phone Number")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.full_name = QLineEdit()
        self.full_name.setPlaceholderText("Full Name")

        self.role = QComboBox()
        self.role.addItems(["assistant", "librarian", "admin"])

        layout.addWidget(self.username)
        layout.addWidget(self.email)
        layout.addWidget(self.phone_number)
        layout.addWidget(self.password)
        layout.addWidget(self.full_name)
        layout.addWidget(QLabel("Role:"))
        layout.addWidget(self.role)

        buttons = QHBoxLayout()
        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        save_btn = MaterialButton("Save User", button_type="elevated")
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

    def save_user(self):
        data = {
            "username": self.username.text().strip(),
            "email": self.email.text().strip(),
            "phone_number": self.phone_number.text().strip(),
            "password": self.password.text().strip(),
            "full_name": self.full_name.text().strip(),
            "role": self.role.currentText().upper(),
        }

        result = self.users_controller.create(data)

        if result["success"]:
            QMessageBox.information(self, "Success", result["message"])
            self.on_success()
        else:
            QMessageBox.warning(self, "Error", result["message"])
