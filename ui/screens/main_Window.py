from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QMessageBox,
    QAction,
)
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtCore import QTimer

from ui.screens.users_view import UsersView
from controllers.patrons_controller import PatronsController
from utils.constants import COLORS
from ui.widgets.buttons.material_button import MaterialButton
from ui.widgets.cards.material_card import MaterialStatCard
from ui.widgets.navigation.sidebar import MaterialNavigationRail
from ui.widgets.section.material_section import MaterialSection
from ui.widgets.forms.create_patron_form import AddPatronForm
from ui.screens.data_view import LibraryDataView
from ui.screens.composite_data_view import CompositeDataView
from ui.common.patrons import PatronsView


class MainWindow(QMainWindow):
    def __init__(self, auth_service, user_info):
        super().__init__()
        self.auth_service = auth_service
        self.patrons_controller = PatronsController(self.auth_service.db_manager)
        self.user_info = user_info
        self.logout_requested = False

        # Setup session refresh timer (refresh every 30 minutes)
        self.session_timer = QTimer()
        self.session_timer.timeout.connect(self.refresh_session)
        self.session_timer.start(30 * 60 * 1000)  # 30 minutes in milliseconds

        self.setup_window()
        self.setup_menu_bar()
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

    def setup_menu_bar(self):
        """Setup menu bar with user account options"""
        menubar = self.menuBar()

        # Account menu
        account_menu = menubar.addMenu("Account")

        # User info action (disabled, just shows current user)
        user_action = QAction(f"Logged in as: {self.user_info['full_name']}", self)
        user_action.setEnabled(False)
        account_menu.addAction(user_action)

        account_menu.addSeparator()

        # Change password action
        change_password_action = QAction("Change Password", self)
        change_password_action.triggered.connect(self.show_change_password_dialog)
        account_menu.addAction(change_password_action)

        account_menu.addSeparator()

        # Logout action
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.handle_logout)
        account_menu.addAction(logout_action)

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
        users = self.patrons_controller.get_all()
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
        self.users_table = PatronsView(self.auth_service.db_manager)
        users_table_section = MaterialSection("Today's Users", self.users_table)
        self.content_layout.addWidget(users_table_section)

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
        import_btn = MaterialButton("Import Data", button_type="outlined")
        export_btn = MaterialButton("Export Data", button_type="outlined")
        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(import_btn)
        actions_layout.addWidget(export_btn)
        actions_layout.addStretch()
        self.content_layout.addLayout(actions_layout)

        # Hook up button
        add_btn.clicked.connect(self.show_add_user_form)

        # Users table
        self.users_table = UsersView(self.auth_service.db_manager)
        users_section = MaterialSection("All Users", self.users_table)
        self.content_layout.addWidget(users_section)

    # In your main window class, replace the show_users method with this:

    def show_composite_data_view(self):
        """Show the composite data management view"""
        self.clear_content()

        # Create the composite view
        self.composite_view = CompositeDataView(self.auth_service.db_manager)

        # Connect the add signal to handle different view types
        self.composite_view.add_requested.connect(self.handle_add_request)

        # Add to content layout
        self.content_layout.addWidget(self.composite_view)

    def handle_add_request(self, view_type):
        """Handle add button clicks from composite view"""
        if view_type == "Users":
            self.show_add_user_form()
        elif view_type == "Patrons":
            self.show_add_patron_form()  # You'll need to create this
        elif view_type == "Books":
            self.show_add_book_form()  # You'll need to create this
        elif view_type == "Borrowed Books":
            self.show_add_borrowed_book_form()  # You'll need to create this
        elif view_type == "Payments":
            self.show_add_payment_form()  # You'll need to create this

    # Optional: Update your navigation menu to use the new composite view
    def update_navigation_menu(self):
        """Update your existing navigation to use the composite view"""
        # Replace individual menu items with a single "Data Management" item
        # or keep separate items that all call show_composite_data_view() but
        # with different default views

        # Example 1: Single menu item approach
        data_management_action = QAction("Data Management", self)
        data_management_action.triggered.connect(self.show_composite_data_view)

        # Example 2: Separate menu items that switch to specific views
        users_action = QAction("Users", self)
        users_action.triggered.connect(lambda: self.show_specific_data_view("Users"))

        patrons_action = QAction("Patrons", self)
        patrons_action.triggered.connect(
            lambda: self.show_specific_data_view("Patrons")
        )

        books_action = QAction("Books", self)
        books_action.triggered.connect(lambda: self.show_specific_data_view("Books"))

    def show_specific_data_view(self, view_type):
        """Show composite view with a specific view selected"""
        self.show_composite_data_view()
        # Switch to the requested view after creation
        if hasattr(self, "composite_view"):
            self.composite_view.switch_view(view_type)

    # Optional: Add methods to refresh data from parent window
    def refresh_composite_data(self):
        """Refresh the composite view data"""
        if hasattr(self, "composite_view"):
            self.composite_view.refresh_current_view()

    # If you want to get selected items from the current table
    def get_selected_data_items(self):
        """Get selected items from the composite view"""
        if hasattr(self, "composite_view"):
            return self.composite_view.get_selected_items()
        return []

    def show_library_data(self):
        self.clear_content()

        # Page title + toggle buttons
        title_layout = QHBoxLayout()

        title = QLabel("Library Data Management")
        title.setFont(QFont("Segoe UI", 32, QFont.Light))
        title.setStyleSheet(f"color: {COLORS['on_surface']}; margin-bottom: 8px;")
        title_layout.addWidget(title)
        title_layout.addStretch()

        # Navigation buttons (toggle between sections)
        patrons_btn = MaterialButton("Patrons", button_type="text")
        users_btn = MaterialButton("Users", button_type="text")
        books_btn = MaterialButton("Books", button_type="text")
        payments_btn = MaterialButton("Payments", button_type="text")
        borrowed_btn = MaterialButton("Borrowed", button_type="text")

        for btn in [patrons_btn, users_btn, books_btn, payments_btn, borrowed_btn]:
            btn.setFont(QFont("Segoe UI", 12))
            title_layout.addWidget(btn)

        self.content_layout.addLayout(title_layout)

        # Subtitle
        subtitle = QLabel(
            "Manage all core library data: users, patrons, books, and transactions."
        )
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(
            f"color: {COLORS['on_surface_variant']}; margin-bottom: 24px;"
        )
        self.content_layout.addWidget(subtitle)

        # Action buttons
        actions_layout = QHBoxLayout()
        add_btn = MaterialButton("Add New", button_type="elevated")
        import_btn = MaterialButton("Import Data", button_type="outlined")
        export_btn = MaterialButton("Export Data", button_type="outlined")
        actions_layout.addWidget(add_btn)
        actions_layout.addWidget(import_btn)
        actions_layout.addWidget(export_btn)
        actions_layout.addStretch()
        self.content_layout.addLayout(actions_layout)

        # Data view widget (with tabs for Users, Patrons, Books, etc.)
        self.data_view = LibraryDataView(self.auth_service.db_manager)
        self.content_layout.addWidget(self.data_view, stretch=1)

        # Connect nav buttons to switch tabs
        patrons_btn.clicked.connect(lambda: self.data_view.tabs.setCurrentIndex(1))
        users_btn.clicked.connect(lambda: self.data_view.tabs.setCurrentIndex(0))
        books_btn.clicked.connect(lambda: self.data_view.tabs.setCurrentIndex(3))
        payments_btn.clicked.connect(lambda: self.data_view.tabs.setCurrentIndex(2))
        borrowed_btn.clicked.connect(lambda: self.data_view.tabs.setCurrentIndex(4))

        # Hook Add button so it’s context-aware
        def handle_add():
            current_tab = self.data_view.tabs.tabText(
                self.data_view.tabs.currentIndex()
            )
            if current_tab == "Users":
                self.show_add_user_form()
            elif current_tab == "Patrons":
                self.show_add_patron_form()
            elif current_tab == "Books":
                self.show_add_book_form()
            # Extend similarly for Payments and Borrowed Books

        add_btn.clicked.connect(handle_add)

    def show_data(self):
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

        # Data table
        self.users_table = LibraryDataView(self.auth_service.db_manager)
        users_section = MaterialSection("Library Data", self.users_table)
        self.content_layout.addWidget(users_section)

    def show_add_user_form(self):
        self.clear_content()

        def go_back():
            self.show_users()

        def on_success():
            self.show_users()

        form = AddPatronForm(
            patrons_controller=self.patrons_controller,
            on_cancel=go_back,
            on_success=on_success,
        )
        self.content_layout.addWidget(form)

    def refresh_session(self):
        """Refresh the current session to extend its lifetime"""
        if self.auth_service.current_session:
            result = self.auth_service.refresh_session()
            if not result["success"]:
                # Session refresh failed, probably expired
                self.handle_session_expired()

    def handle_session_expired(self):
        """Handle when session has expired"""
        self.session_timer.stop()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("Session Expired")
        msg.setText("Your session has expired. Please log in again.")
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec_()

        self.logout_requested = True
        self.close()

    def handle_logout(self):
        """Handle logout menu action"""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.auth_service.logout()
            self.logout_requested = True
            self.close()

    def show_change_password_dialog(self):
        """Show change password dialog"""
        # You can implement a proper dialog here
        # For now, just show a message box
        QMessageBox.information(
            self,
            "Change Password",
            "Change password functionality would be implemented here.",
        )

    def closeEvent(self, event):
        """Handle window close event"""
        if self.session_timer:
            self.session_timer.stop()
        event.accept()

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
