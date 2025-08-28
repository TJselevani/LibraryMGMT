from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFrame,
    QScrollArea,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve

from ui.users_view import UsersView
from controllers.users_controller import get_all_users


# Material Design Color Palette
COLORS = {
    "primary": "#1976D2",  # Blue 700
    "primary_dark": "#1565C0",  # Blue 800
    "primary_light": "#42A5F5",  # Blue 400
    "secondary": "#03DAC6",  # Teal A400
    "background": "#FAFAFA",  # Grey 50
    "surface": "#FFFFFF",  # White
    "surface_variant": "#F5F5F5",  # Grey 100
    "on_surface": "#212121",  # Grey 900
    "on_surface_variant": "#757575",  # Grey 600
    "outline": "#E0E0E0",  # Grey 300
    "error": "#F44336",  # Red 500
    "success": "#4CAF50",  # Green 500
    "warning": "#FF9800",  # Orange 500
}


# Custom Material Design Button
class MaterialButton(QPushButton):
    def __init__(self, text="", icon="", button_type="elevated", parent=None):
        super().__init__(text, parent)
        self.button_type = button_type
        self.icon_text = icon
        self.setup_ui()
        self.setup_animation()

    def setup_ui(self):
        self.setMinimumHeight(40)
        self.setFont(QFont("Segoe UI", 9, QFont.Medium))

        if self.button_type == "elevated":
            self.setStyleSheet(
                f"""
                MaterialButton {{
                    background-color: {COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 20px;
                    padding: 8px 24px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1.25px;
                }}
                MaterialButton:hover {{
                    background-color: {COLORS['primary_dark']};
                }}
                MaterialButton:pressed {{
                    background-color: {COLORS['primary_dark']};
                }}
            """
            )
        elif self.button_type == "outlined":
            self.setStyleSheet(
                f"""
                MaterialButton {{
                    background-color: transparent;
                    color: {COLORS['primary']};
                    border: 1px solid {COLORS['primary']};
                    border-radius: 20px;
                    padding: 8px 24px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1.25px;
                }}
                MaterialButton:hover {{
                    background-color: rgba(25, 118, 210, 0.08);
                }}
            """
            )
        elif self.button_type == "text":
            self.setStyleSheet(
                f"""
                MaterialButton {{
                    background-color: transparent;
                    color: {COLORS['primary']};
                    border: none;
                    border-radius: 20px;
                    padding: 8px 16px;
                    font-weight: 500;
                    text-transform: uppercase;
                    letter-spacing: 1.25px;
                }}
                MaterialButton:hover {{
                    background-color: rgba(25, 118, 210, 0.08);
                }}
            """
            )

        # Add shadow effect for elevated buttons
        if self.button_type == "elevated":
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(8)
            shadow.setColor(QColor(0, 0, 0, 60))
            shadow.setOffset(0, 2)
            self.setGraphicsEffect(shadow)

    def setup_animation(self):
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)


# Material Design Card
class MaterialCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        self.setFrameStyle(QFrame.NoFrame)
        self.setStyleSheet(
            f"""
            MaterialCard {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                border: 1px solid {COLORS['outline']};
            }}
        """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)


# Material Design Stat Card
class MaterialStatCard(MaterialCard):
    def __init__(self, title, value, icon="", color=COLORS["primary"]):
        super().__init__()
        self.setup_content(title, value, icon, color)

    def setup_content(self, title, value, icon, color):
        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(8)

        # Icon and value row
        top_row = QHBoxLayout()

        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Segoe UI", 24))
            icon_label.setStyleSheet(f"color: {color};")
            top_row.addWidget(icon_label)

        top_row.addStretch()

        value_label = QLabel(str(value))
        value_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        value_label.setStyleSheet(f"color: {COLORS['on_surface']};")
        value_label.setAlignment(Qt.AlignRight)
        top_row.addWidget(value_label)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12))
        title_label.setStyleSheet(f"color: {COLORS['on_surface_variant']};")

        layout.addLayout(top_row)
        layout.addWidget(title_label)
        self.setLayout(layout)


# Material Design Navigation Rail (Sidebar)
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
        self.users_btn = self.create_nav_button("👤", "Users")
        self.books_btn = self.create_nav_button("📚", "Books")
        self.settings_btn = self.create_nav_button("⚙️", "Settings")

        # Connect buttons
        self.home_btn.clicked.connect(lambda: self.parent.show_home())
        self.users_btn.clicked.connect(lambda: self.parent.show_users())

        layout.addWidget(self.home_btn)
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

        # Set icon text
        btn.setText(icon)

        # Add click handler for active state
        btn.clicked.connect(lambda: self.set_active_button(btn))

        return btn

    def set_active_button(self, button):
        # Reset previous active button
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

        # Set new active button
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


# Main Window with Material Design
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_window()
        self.setup_ui()
        self.show_home()

    def setup_window(self):
        self.setWindowTitle("Library Management System")
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
        # add_user_btn = MaterialButton("Add User", button_type="elevated")
        # users_section = MaterialSection("Recent Users", None, add_user_btn)
        # self.content_layout.addWidget(users_section)

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
