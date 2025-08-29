from PyQt5.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QSizePolicy,
)
from PyQt5.QtGui import QFont
from utils.constants import COLORS
from ui.widgets.cards.material_card import MaterialCard


# Material Design Section
class MaterialSection(MaterialCard):
    def __init__(self, title, widget=None, action_button=None):
        super().__init__()
        self.setup_content(title, widget, action_button)

    def setup_content(self, title, widget, action_button):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(16)

        # Header
        header = QHBoxLayout()

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Medium))
        title_label.setStyleSheet(f"color: {COLORS['on_surface']};")

        header.addWidget(title_label)
        header.addStretch()

        if action_button:
            header.addWidget(action_button)

        layout.addLayout(header)

        if widget:
            widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(widget, stretch=1)  # let widget take remaining space
            # layout.addWidget(widget)

        self.setLayout(layout)
