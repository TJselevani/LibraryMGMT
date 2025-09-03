import logging
import traceback
from typing import Optional
from PyQt5.QtWidgets import QMessageBox


class ErrorHandler:
    """Centralized error handling"""

    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)

    def handle_error(
        self,
        error: Exception,
        context: str = "",
        show_user_message: bool = True,
        parent_widget=None,
    ) -> bool:
        """Handle error with logging and optional user notification"""

        error_msg = f"{context}: {str(error)}" if context else str(error)

        # Log the error
        self.logger.error(f"{error_msg}\n{traceback.format_exc()}")

        # Show user message if requested
        if show_user_message:
            self._show_error_dialog(error_msg, parent_widget)

        return False  # Indicates operation failed

    def _show_error_dialog(self, message: str, parent=None):
        """Show error dialog to user"""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Error")
        msg_box.setText("An error occurred:")
        msg_box.setDetailedText(message)
        msg_box.exec_()
