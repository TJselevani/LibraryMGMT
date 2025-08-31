from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
)


from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


class AddBookForm(QWidget):
    def __init__(self, books_controller, on_cancel, on_success):
        super().__init__()
        self.books_controller = books_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("Add Book")
        title.setStyleSheet(f"font-size: 28px; color: {COLORS['on_surface']};")
        layout.addWidget(title)

        self.title_field = QLineEdit()
        self.title_field.setPlaceholderText("Title")

        self.author = QLineEdit()
        self.author.setPlaceholderText("Author")

        self.class_name = QLineEdit()
        self.class_name.setPlaceholderText("Class Name")

        self.accession_no = QLineEdit()
        self.accession_no.setPlaceholderText("Accession No")

        layout.addWidget(self.title_field)
        layout.addWidget(self.author)
        layout.addWidget(self.class_name)
        layout.addWidget(self.accession_no)

        buttons = QHBoxLayout()
        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        save_btn = MaterialButton("Save Book", button_type="elevated")
        buttons.addWidget(cancel_btn)
        buttons.addWidget(save_btn)
        layout.addLayout(buttons)

        cancel_btn.clicked.connect(self.on_cancel)
        save_btn.clicked.connect(self.save_book)

    def save_book(self):
        data = {
            "title": self.title_field.text().strip(),
            "author": self.author.text().strip(),
            "class_name": self.class_name.text().strip(),
            "accession_no": self.accession_no.text().strip(),
        }

        result = self.books_controller.create(data)

        if result["success"]:
            QMessageBox.information(self, "Success", result["message"])
            self.on_success()
        else:
            QMessageBox.warning(self, "Error", result["message"])
