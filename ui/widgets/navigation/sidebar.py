from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from utils.constants import COLORS
from app.main_window import ViewType  # ✅ import your enum


class MaterialNavigationRail(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.active_button = None
        self.setup_ui()

    def setup_ui(self):
        self.setFixedWidth(80)
        self.setStyleSheet(
            f"""
            MaterialNavigationRail {{
                background-color: {COLORS['surface']};
                border-right: 1px solid {COLORS['outline']};
            }}
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        # Navigation items
        self.home_btn = self.create_nav_button("🏠", "Home", active=True)
        self.dash_btn = self.create_nav_button("🏠", "Dashboard")
        self.users_btn = self.create_nav_button("👤", "Users")
        self.books_btn = self.create_nav_button("📚", "Books")
        self.settings_btn = self.create_nav_button("⚙️", "Settings")

        # ✅ Use navigate_to with proper ViewTypes
        self.home_btn.clicked.connect(lambda: self.parent.navigate_to(ViewType.HOME))
        self.dash_btn.clicked.connect(
            lambda: self.parent.navigate_to(ViewType.DASHBOARD)
        )
        self.users_btn.clicked.connect(
            lambda: self.parent.navigate_to(ViewType.ALL_TABLES)
        )
        self.books_btn.clicked.connect(
            lambda: self.parent.navigate_to(ViewType.LIBRARY_DATA)
        )
        self.settings_btn.clicked.connect(
            lambda: self.parent.navigate_to(ViewType.USERS)
        )

        layout.addWidget(self.home_btn)
        layout.addWidget(self.dash_btn)
        layout.addWidget(self.users_btn)
        layout.addWidget(self.books_btn)
        layout.addWidget(self.settings_btn)
        layout.addStretch()

        self.setLayout(layout)

    def create_nav_button(self, icon, tooltip, active=False):
        btn = QPushButton()
        btn.setFixedSize(56, 56)
        btn.setToolTip(tooltip)
        btn.setFont(QFont("Segoe UI", 20))

        if active:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 28px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['primary_dark']};
                }}
            """
            )
            self.active_button = btn
        else:
            btn.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['on_surface_variant']};
                    border: none;
                    border-radius: 28px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface_variant']};
                    color: {COLORS['on_surface']};
                }}
            """
            )

        btn.setText(icon)

        # Active state tracking
        btn.clicked.connect(lambda: self.set_active_button(btn))

        return btn

    def set_active_button(self, button):
        if self.active_button:
            self.active_button.setStyleSheet(
                f"""
                QPushButton {{
                    background-color: transparent;
                    color: {COLORS['on_surface_variant']};
                    border: none;
                    border-radius: 28px;
                }}
                QPushButton:hover {{
                    background-color: {COLORS['surface_variant']};
                    color: {COLORS['on_surface']};
                }}
            """
            )

        button.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 28px;
            }}
            QPushButton:hover {{
                background-color: {COLORS['primary_dark']};
            }}
        """
        )
        self.active_button = button
