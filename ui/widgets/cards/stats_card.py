from PyQt5.QtWidgets import QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


# ---------------- Styled Stat Card ----------------
class StatCard(QFrame):
    def __init__(self, icon, title, value):
        super().__init__()
        self.setStyleSheet(
            """
            QFrame {
                border-radius: 12px;
                background-color: #2f2f2f;
                padding: 10px;
                color: white;
            }
        """
        )
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 28))
        val_label = QLabel(str(value))
        val_label.setFont(QFont("Arial", 22, QFont.Bold))
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))

        layout.addWidget(icon_label)
        layout.addWidget(val_label)
        layout.addWidget(title_label)
        self.setLayout(layout)
