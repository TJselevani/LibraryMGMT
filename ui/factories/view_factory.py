# from typing import Dict, Callable
from PyQt5.QtWidgets import QWidget
from core.container import DIContainer


class ViewFactory:
    def __init__(self, container: DIContainer):
        self.container = container
        self._creators = {
            "dashboard": self._create_dashboard,
            "users": self._create_users_view,
            # ... other views
        }

    def create_view(self, view_type: str, **kwargs) -> QWidget:
        creator = self._creators.get(view_type)
        if creator:
            return creator(**kwargs)
        raise ValueError(f"Unknown view type: {view_type}")

    def _create_dashboard(self, **kwargs):
        from ui.screens.dashboard_view import DashboardView

        return DashboardView(self.container, **kwargs)

    def _create_users_view(self, **kwargs):
        from ui.screens.users_view import UsersView

        return UsersView(self.container, **kwargs)
