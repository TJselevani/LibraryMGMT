from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
)
from PyQt5.QtGui import QFont
from config.ui_config import ViewType, COLORS
from core.container import DependencyContainer
from typing import Callable

# =====================================================================
# VIEW FACTORY
# =====================================================================


class ViewFactory:
    """Factory for creating views"""

    def __init__(self, container: DependencyContainer):
        self.container = container
        self._view_creators = {
            ViewType.HOME: self._create_homepage_view,
            ViewType.DASHBOARD: self._create_dashboard_view,
            ViewType.ALL_TABLES: self._create_composite_view,
            ViewType.LIBRARY_DATA: self._create_library_data_view,
            ViewType.USERS: self._create_users_view,
        }

    def create_view(self, view_type: ViewType, **kwargs) -> QWidget:
        """Create view by type"""
        creator = self._view_creators.get(view_type)
        if creator:
            return creator(**kwargs)
        raise ValueError(f"Unknown view type: {view_type}")

    def _create_homepage_view(self, **kwargs) -> QWidget:
        """Create dashboard view"""
        from ui.screens.home_view import HomeView

        return HomeView()

    def _create_dashboard_view(self, **kwargs) -> QWidget:
        """Create dashboard view"""
        from ui.screens.dashboard_view import DashboardView

        return DashboardView(self.container.auth_service.db_manager)

    def _create_users_view(self, **kwargs) -> QWidget:
        """Create users view"""
        from ui.screens.attendance_view import AttendanceView

        return AttendanceView(self.container.auth_service.db_manager)

    def _create_composite_view(self, **kwargs) -> QWidget:
        """Create composite data view"""
        from ui.screens.composite_data_view import CompositeDataView

        return CompositeDataView(self.container.auth_service.db_manager)

    def _create_library_data_view(self, **kwargs) -> QWidget:
        """Create library data view"""
        from ui.screens.data_view import LibraryDataView

        return LibraryDataView(self.container.auth_service.db_manager)


# =====================================================================
# FORM FACTORY
# =====================================================================


class FormFactory:
    """Factory for creating forms"""

    def __init__(self, container: DependencyContainer):
        self.container = container
        self._form_creators = {
            "user": self._create_user_form,
            "patron": self._create_patron_form,
            "book": self._create_book_form,
            "borrowed_book": self._create_borrowed_book_form,
            "payment": self._create_payment_form,
        }

    def create_form(
        self, form_type: str, on_cancel: Callable, on_success: Callable, **kwargs
    ) -> QWidget:
        """Create form by type"""
        creator = self._form_creators.get(form_type)
        if creator:
            return creator(on_cancel=on_cancel, on_success=on_success, **kwargs)
        raise ValueError(f"Unknown form type: {form_type}")

    def _create_user_form(self, **kwargs):
        from ui.widgets.forms.create_user_form import AddUserForm

        return AddUserForm(
            users_controller=self.container.get_controller("users"), **kwargs
        )

    def _create_patron_form(self, **kwargs):
        from ui.widgets.forms.create_patron_form import AddPatronForm

        return AddPatronForm(
            patrons_controller=self.container.get_controller("patrons"), **kwargs
        )

    def _create_book_form(self, **kwargs):
        from ui.widgets.forms.create_book_form import AddBookForm

        return AddBookForm(
            books_controller=self.container.get_controller("books"), **kwargs
        )

    def _create_borrowed_book_form(self, **kwargs):
        from ui.widgets.forms.create_borrowed_book import AddBorrowedBookForm

        return AddBorrowedBookForm(
            books_controller=self.container.get_controller("books"),
            borrowed_books_controller=self.container.get_controller("borrowed_books"),
            patrons_controller=self.container.get_controller("patrons"),
            **kwargs,
        )

    def _create_payment_form(self, **kwargs):
        from ui.widgets.forms.create_payment_form import AddPaymentForm

        return AddPaymentForm(
            payments_controller=self.container.get_controller("payments"),
            patrons_controller=self.container.get_controller("patrons"),
            payment_items_controller=self.container.get_controller("payment_items"),
            **kwargs,
        )


# =====================================================================
# UI BUILDER
# =====================================================================


class UIBuilder:
    """Builder for UI components"""

    @staticmethod
    def create_title(text: str, font_size: int = 32) -> QLabel:
        """Create title label"""
        title = QLabel(text)
        title.setFont(QFont("Segoe UI", font_size, QFont.Light))
        title.setStyleSheet(f"color: {COLORS['on_surface']}; margin-bottom: 8px;")
        return title

    @staticmethod
    def create_subtitle(text: str) -> QLabel:
        """Create subtitle label"""
        subtitle = QLabel(text)
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet(
            f"color: {COLORS['on_surface_variant']}; margin-bottom: 24px;"
        )
        return subtitle

    @staticmethod
    def create_action_buttons(button_configs: list) -> QHBoxLayout:
        """Create action buttons layout"""
        from ui.widgets.buttons.material_button import MaterialButton

        layout = QHBoxLayout()
        buttons = []

        for config in button_configs:
            if isinstance(config, str):
                btn = MaterialButton(config, button_type="elevated")
            elif isinstance(config, dict):
                btn = MaterialButton(
                    config["text"], button_type=config.get("type", "elevated")
                )
            buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        return layout, buttons
