from abc import ABC, abstractmethod
from typing import Any
from config.ui_config import ViewType


# =====================================================================
# COMMAND PATTERN FOR ACTIONS
# =====================================================================


class Command(ABC):
    """Abstract command interface"""

    @abstractmethod
    def execute(self) -> Any:
        pass

    @abstractmethod
    def undo(self) -> Any:
        pass


class NavigationCommand(Command):
    """Command for navigation actions"""

    def __init__(self, main_window, view_type: ViewType, **kwargs):
        self.main_window = main_window
        self.view_type = view_type
        self.kwargs = kwargs
        self.previous_view = None

    def execute(self):
        self.previous_view = getattr(self.main_window, "_current_view", None)
        self.main_window._navigate_to_view(self.view_type, **self.kwargs)

    def undo(self):
        if self.previous_view:
            self.main_window._navigate_to_view(self.previous_view)


class FormCommand(Command):
    """Command for form actions"""

    def __init__(self, main_window, form_type: str, **kwargs):
        self.main_window = main_window
        self.form_type = form_type
        self.kwargs = kwargs

    def execute(self):
        self.main_window._show_form(self.form_type, **self.kwargs)

    def undo(self):
        self.main_window._go_back()
