from typing import Dict, Any, Optional
from config.ui_config import ViewType

# =====================================================================
# STATE MANAGEMENT
# =====================================================================


class AppState:
    """Application state manager"""

    def __init__(self):
        self.current_view: Optional[ViewType] = None
        self.view_stack: list = []
        self.user_info: Dict[str, Any] = {}
        self.session_active: bool = True

    def push_view(self, view_type: ViewType):
        """Push new view to stack"""
        if self.current_view:
            self.view_stack.append(self.current_view)
        self.current_view = view_type

    def pop_view(self) -> Optional[ViewType]:
        """Pop previous view from stack"""
        if self.view_stack:
            self.current_view = self.view_stack.pop()
            return self.current_view
        return None

    def can_go_back(self) -> bool:
        """Check if can navigate back"""
        return bool(self.view_stack)
