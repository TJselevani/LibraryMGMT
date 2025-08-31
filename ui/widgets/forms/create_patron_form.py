from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QMessageBox,
)
from PyQt5.QtCore import QDate
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


class AddPatronForm(QWidget):
    def __init__(self, patrons_controller, on_cancel, on_success):
        super().__init__()
        self.patrons_controller = patrons_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        title = QLabel("Add New User")
        title.setStyleSheet(f"font-size: 28px; color: {COLORS['on_surface']};")
        layout.addWidget(title)

        # Input fields
        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("First Name")

        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Last Name")

        self.institution = QLineEdit()
        self.institution.setPlaceholderText("School/Institution")

        self.grade_level = QLineEdit()
        self.grade_level.setPlaceholderText("Grade Level")

        self.age = QLineEdit()
        self.age.setPlaceholderText("Age")

        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female", "Other"])

        self.dob = QDateEdit()
        self.dob.setCalendarPopup(True)
        self.dob.setDate(QDate.currentDate())

        self.residence = QLineEdit()
        self.residence.setPlaceholderText("Residence")

        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("Phone Number")

        layout.addWidget(self.first_name)
        layout.addWidget(self.last_name)
        layout.addWidget(self.institution)
        layout.addWidget(self.grade_level)
        layout.addWidget(self.age)
        layout.addWidget(self.gender)
        layout.addWidget(QLabel("Date of Birth:"))
        layout.addWidget(self.dob)
        layout.addWidget(self.residence)
        layout.addWidget(self.phone_number)

        # Buttons
        buttons = QHBoxLayout()
        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        save_btn = MaterialButton("Save User", button_type="elevated")
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        cancel_btn.clicked.connect(self.on_cancel)
        save_btn.clicked.connect(self.save_user)

    def save_user(self):
        data = {
            "first_name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "institution": self.institution.text().strip(),
            "grade_level": self.grade_level.text().strip(),
            "age": self.age.text().strip(),
            "gender": self.gender.currentText(),
            "date_of_birth": self.dob.date().toString("yyyy-MM-dd"),
            "residence": self.residence.text().strip(),
            "phone_number": self.phone_number.text().strip(),
            "membership_status": "PATRON",
        }

        result = self.patrons_controller.create(data)

        if result["success"]:
            QMessageBox.information(self, "Success", result["message"])
            self.on_success()
        else:
            QMessageBox.warning(self, "Error", result["message"])
