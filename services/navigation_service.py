# from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal


class NavigationService(QObject):
    """Service for handling navigation across the application"""

    # Signals
    navigate_requested = pyqtSignal(str, dict)  # view_type, kwargs
    back_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._navigation_history = []
        self._current_view = None

    def navigate_to(self, view_type: str, **kwargs):
        """Navigate to a specific view"""
        if self._current_view:
            self._navigation_history.append((self._current_view, {}))

        self._current_view = view_type
        self.navigate_requested.emit(view_type, kwargs)

    def go_back(self):
        """Navigate back to previous view"""
        if self._navigation_history:
            previous_view, previous_kwargs = self._navigation_history.pop()
            self._current_view = previous_view
            self.back_requested.emit()

    def can_go_back(self) -> bool:
        """Check if back navigation is possible"""
        return bool(self._navigation_history)
