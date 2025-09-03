"""
Production-level refactored main window with proper architecture patterns
"""

from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QMessageBox,
    QSizePolicy,
    QAction,
)
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import QTimer

# from ui.screens.patrons_view import PatronsView


from utils.constants import COLORS

from config.ui_config import ViewType, ViewConfig, AppConfig

from core.container import DependencyContainer
from core.patterns.command import NavigationCommand, FormCommand
from core.events.event_bus import EventBus
from core.state.app_state import AppState
from core.patterns.factory import ViewFactory, FormFactory, UIBuilder


# =====================================================================
# MAIN WINDOW - REFACTORED
# =====================================================================


class MainWindow(QMainWindow):
    """Refactored main window with clean architecture"""

    def __init__(self, auth_service, user_info):
        super().__init__()

        # Core dependencies
        self.container = DependencyContainer(auth_service)
        self.app_state = AppState()
        self.app_state.user_info = user_info

        # Factories
        self.view_factory = ViewFactory(self.container)
        self.form_factory = FormFactory(self.container)

        # Event system
        self.event_bus = EventBus()
        self._connect_events()

        # UI components
        self.ui_builder = UIBuilder()
        self.current_view_widget = None

        # Session management
        self.session_timer = QTimer()
        self.logout_requested = False

        # Initialize
        self._setup_window()
        self._setup_menu_bar()
        self._setup_ui()
        self._setup_session_management()

        # Start with dashboard
        self.navigate_to(ViewType.HOME)

    def _connect_events(self):
        """Connect event bus signals"""
        self.event_bus.navigation_requested.connect(self._handle_navigation)
        self.event_bus.form_requested.connect(self._handle_form_request)
        self.event_bus.session_expired.connect(self._handle_session_expired)
        self.event_bus.logout_requested.connect(self._handle_logout)

    def _setup_window(self):
        """Setup main window properties"""
        user_name = self.app_state.user_info.get("full_name", "User")
        self.setWindowTitle(f"Library Management System - Welcome {user_name}")
        self.setGeometry(*AppConfig.WINDOW_GEOMETRY)

        # Set application palette
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(COLORS["background"]))
        palette.setColor(QPalette.WindowText, QColor(COLORS["on_surface"]))
        self.setPalette(palette)

    def _setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        account_menu = menubar.addMenu("Account")

        # User info
        user_name = self.app_state.user_info.get("full_name", "User")
        user_action = QAction(f"Logged in as: {user_name}", self)
        user_action.setEnabled(False)
        account_menu.addAction(user_action)

        account_menu.addSeparator()

        # Actions
        change_password_action = QAction("Change Password", self)
        change_password_action.triggered.connect(self._show_change_password_dialog)
        account_menu.addAction(change_password_action)

        account_menu.addSeparator()

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(lambda: self.event_bus.logout_requested.emit())
        account_menu.addAction(logout_action)

    def _setup_ui(self):
        """Setup main UI structure"""
        # Central widget
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.central.setStyleSheet(f"background-color: {COLORS['background']};")

        main_layout = QHBoxLayout(self.central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Navigation rail
        from ui.widgets.navigation.sidebar import MaterialNavigationRail

        self.nav_rail = MaterialNavigationRail(self)
        main_layout.addWidget(self.nav_rail)

        # Content area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(32, 32, 32, 32)
        self.content_layout.setSpacing(24)
        self.content_area.setLayout(self.content_layout)

        # Scrollable content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.content_area)
        scroll.setStyleSheet(self._get_scroll_style())
        main_layout.addWidget(scroll, 1)

    def _setup_session_management(self):
        """Setup session management"""
        self.session_timer.timeout.connect(self._refresh_session)
        self.session_timer.start(AppConfig.SESSION_REFRESH_INTERVAL)

    def _get_scroll_style(self) -> str:
        """Get scroll area stylesheet"""
        return """
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

    # =====================================================================
    # PUBLIC API METHODS
    # =====================================================================

    def navigate_to(self, view_type: ViewType, **kwargs):
        """Public method to navigate to a view"""
        command = NavigationCommand(self, view_type, **kwargs)
        command.execute()

    def show_form(self, form_type: str, **kwargs):
        """Public method to show a form"""
        command = FormCommand(self, form_type, **kwargs)
        command.execute()

    def go_back(self) -> bool:
        """Go back to previous view"""
        previous_view = self.app_state.pop_view()
        if previous_view:
            self._navigate_to_view(previous_view)
            return True
        return False

    def refresh_data(self, controller_name: str = None):
        """Refresh data for current view"""
        self.event_bus.data_refresh_requested.emit(controller_name or "all")

    # =====================================================================
    # PRIVATE IMPLEMENTATION METHODS
    # =====================================================================

    def _navigate_to_view(self, view_type: ViewType, **kwargs):
        """Internal navigation implementation"""
        try:
            self.app_state.push_view(view_type)
            self._clear_content()

            config = AppConfig.VIEW_CONFIGS.get(view_type)
            if config:
                self._build_view_layout(config, view_type, **kwargs)
            else:
                self._build_simple_view(view_type, **kwargs)

        except Exception as e:
            self._handle_error(f"Error navigating to view: {e}")

    def _build_view_layout(self, config: ViewConfig, view_type: ViewType, **kwargs):
        """Build standard view layout"""
        # Title and subtitle
        # title = self.ui_builder.create_title(config.title)
        # subtitle = self.ui_builder.create_subtitle(config.subtitle)

        # self.content_layout.addWidget(title)
        # self.content_layout.addWidget(subtitle)

        # # Action buttons
        # if config.requires_actions and config.action_buttons:
        #     actions_layout, buttons = self.ui_builder.create_action_buttons(
        #         config.action_buttons
        #     )
        #     self.content_layout.addLayout(actions_layout)
        #     self._connect_action_buttons(buttons, view_type)

        # Main view
        try:
            view_widget = self.view_factory.create_view(view_type, **kwargs)
            if view_widget:
                if hasattr(view_widget, "add_requested"):
                    view_widget.add_requested.connect(self._handle_add_request)

                from ui.widgets.section.material_section import MaterialSection

                view_section = MaterialSection("", view_widget)
                self.content_layout.addWidget(view_section)
                self.current_view_widget = view_widget
        except Exception as e:
            self._handle_error(f"Error creating view widget: {e}")

    def _connect_action_buttons(self, buttons: list, view_type: ViewType):
        """Connect action buttons to their handlers"""
        if not buttons:
            return

        # Map button text to actions
        button_actions = {
            "Add New User": lambda: self.show_form("user"),
            "Add New": self._handle_context_aware_add,
            "Import Data": self._handle_import_data,
            "Export Data": self._handle_export_data,
        }

        for button in buttons:
            button_text = button.text()
            action = button_actions.get(button_text)
            if action:
                button.clicked.connect(action)

    def _show_form(self, form_type: str, **kwargs):
        """Show form implementation"""
        try:
            self.app_state.push_view(self.app_state.current_view)  # Save current view
            self._clear_content()

            # Standard form callbacks
            def on_cancel():
                self.go_back()

            def on_success():
                self.go_back()
                self.refresh_data()

            form_widget = self.form_factory.create_form(
                form_type, on_cancel=on_cancel, on_success=on_success, **kwargs
            )
            self.content_layout.addWidget(form_widget)

        except Exception as e:
            self._handle_error(f"Error showing form: {e}")

    # =====================================================================
    # EVENT HANDLERS
    # =====================================================================

    def _handle_navigation(self, view_type: str, kwargs: dict):
        """Handle navigation event"""
        try:
            view_enum = ViewType(view_type)
            self._navigate_to_view(view_enum, **kwargs)
        except ValueError:
            self._handle_error(f"Invalid view type: {view_type}")

    def _handle_form_request(self, form_type: str, kwargs: dict):
        """Handle form request event"""
        self._show_form(form_type, **kwargs)

    def _handle_add_request(self, view_type: str):
        """Handle add button clicks from composite views"""
        form_mapping = {
            "Users": "user",
            "Patrons": "patron",
            "Books": "book",
            "Borrowed Books": "borrowed_book",
            "Payments": "payment",
        }

        form_type = form_mapping.get(view_type)
        if form_type:
            self.show_form(form_type)

    def _handle_context_aware_add(self):
        """Handle context-aware add button"""
        # This would need to be implemented based on current view context
        pass

    def _handle_import_data(self):
        """Handle import data action"""
        QMessageBox.information(
            self, "Import Data", "Import functionality to be implemented"
        )

    def _handle_export_data(self):
        """Handle export data action"""
        QMessageBox.information(
            self, "Export Data", "Export functionality to be implemented"
        )

    def _handle_error(self, error_message: str):
        """Handle errors gracefully"""
        print(f"Error: {error_message}")  # Log error
        QMessageBox.warning(self, "Error", error_message)

    def _handle_session_expired(self):
        """Handle session expiration"""
        self.session_timer.stop()
        QMessageBox.warning(
            self, "Session Expired", "Your session has expired. Please log in again."
        )
        self.logout_requested = True
        self.close()

    def _handle_logout(self):
        """Handle logout request"""
        reply = QMessageBox.question(
            self,
            "Logout",
            "Are you sure you want to logout?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.container.auth_service.logout()
            self.logout_requested = True
            self.close()

    def _refresh_session(self):
        """Refresh session to extend lifetime"""
        if self.container.auth_service.current_session:
            result = self.container.auth_service.refresh_session()
            if not result["success"]:
                self.event_bus.session_expired.emit()

    def _show_change_password_dialog(self):
        """Show change password dialog"""
        QMessageBox.information(
            self,
            "Change Password",
            "Change password functionality would be implemented here.",
        )

    def _clear_content(self):
        """Clear content area"""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

    def _clear_layout(self, layout):
        """Clear layout recursively"""
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self._clear_layout(child.layout())
        layout.deleteLater()

    def closeEvent(self, event):
        """Handle window close event"""
        if self.session_timer:
            self.session_timer.stop()
        event.accept()
