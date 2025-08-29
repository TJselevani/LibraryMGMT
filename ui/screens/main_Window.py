from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
)
from PyQt5.QtGui import QFont, QPalette, QColor

from ui.screens.users_view import UsersView
from controllers.users_controller import get_all_users
from utils.constants import COLORS
from ui.widgets.buttons.material_button import MaterialButton
from ui.widgets.cards.material_card import MaterialStatCard
from ui.widgets.navigation.sidebar import MaterialNavigationRail
from ui.widgets.section.material_section import MaterialSection


# Main Window with Material Design
class MainWindow(QMainWindow):
    def __init__(self, auth_service, user_info):
        super().__init__()
        self.auth_service = auth_service
        self.user_info = user_info
        self.setup_window()
        self.setup_ui()
        self.show_home()

    def setup_window(self):
        self.setWindowTitle(
            f"Library Management System - Welcome {self.user_info['full_name']}"
        )
        self.setGeometry(200, 100, 1400, 900)

        # Set application palette for Material Design colors
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLORS["background"]))
        palette.setColor(QPalette.WindowText, QColor(COLORS["on_surface"]))
        self.setPalette(palette)

    def setup_ui(self):
        # Central widget
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.central.setStyleSheet(f"background-color: {COLORS['background']};")

        main_layout = QHBoxLayout(self.central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigation Rail (Sidebar)
        self.nav_rail = MaterialNavigationRail(self)
        main_layout.addWidget(self.nav_rail)

        # Content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(32, 32, 32, 32)
        self.content_layout.setSpacing(24)
        self.content_area.setLayout(self.content_layout)

        # Make content area scrollable
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.content_area)
        scroll.setStyleSheet(
            """
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: transparent;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: rgba(0, 0, 0, 0.5);
            }
        """
        )
        main_layout.addWidget(scroll, 1)

    def show_home(self):
        self.clear_content()
        users = get_all_users()
        total_users = len(users)

        # Page title
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 32, QFont.Light))
        title.setStyleSheet(f"color: {COLORS['on_surface']}; margin-bottom: 8px;")
        self.content_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel(
            "Welcome back! Here's what's happening in your library today."
        )
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(
            f"color: {COLORS['on_surface_variant']}; margin-bottom: 24px;"
        )
        self.content_layout.addWidget(subtitle)

        # Statistics cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)

        stats_layout.addWidget(
            MaterialStatCard("Total Users", total_users, "👥", COLORS["primary"])
        )
        stats_layout.addWidget(
            MaterialStatCard("Borrowed Books", 123, "📖", COLORS["success"])
        )
        stats_layout.addWidget(
            MaterialStatCard("Overdue Books", 12, "⚠️", COLORS["warning"])
        )
        stats_layout.addWidget(
            MaterialStatCard("New Members", 8, "✨", COLORS["secondary"])
        )

        self.content_layout.addLayout(stats_layout)

        # Users section
        add_user_btn = MaterialButton("Add User", button_type="elevated")
        users_section = MaterialSection("Recent Users", None, add_user_btn)
        self.content_layout.addWidget(users_section)

        # Users table
        self.users_table = UsersView()
        users_table_section = MaterialSection("Today's Users", self.users_table)
        self.content_layout.addWidget(users_table_section)

        # Add stretch at the end
        # self.content_layout.addStretch()

    def show_users(self):
        self.clear_content()

        # Page title
        title = QLabel("Users Management")
        title.setFont(QFont("Segoe UI", 32, QFont.Light))
        title.setStyleSheet(f"color: {COLORS['on_surface']}; margin-bottom: 8px;")
        self.content_layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Manage library members and their information.")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(
            f"color: {COLORS['on_surface_variant']}; margin-bottom: 24px;"
        )
        self.content_layout.addWidget(subtitle)

        # Action buttons
        actions_layout = QHBoxLayout()
        add_btn = MaterialButton("Add New User", button_type="elevated")
        export_btn = MaterialButton("Export Data", button_type="outlined")
        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(export_btn)
        actions_layout.addStretch()
        self.content_layout.addLayout(actions_layout)

        # Users table
        self.users_table = UsersView()
        users_section = MaterialSection("All Users", self.users_table)
        self.content_layout.addWidget(users_section)

        # Add stretch
        # self.content_layout.addStretch()

    def clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)

            # If item is a widget, delete it
            if item.widget():
                item.widget().deleteLater()

            # If item is a layout, clear its children too
            elif item.layout():
                self.clear_layout(item.layout())

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())
        layout.deleteLater()
