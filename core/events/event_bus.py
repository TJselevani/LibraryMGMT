from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget

# =====================================================================
# EVENT SYSTEM
# =====================================================================


class EventBus(QWidget):
    """Application event bus for loose coupling"""

    # Define signals
    navigation_requested = pyqtSignal(str, dict)  # view_type, kwargs
    form_requested = pyqtSignal(str, dict)  # form_type, kwargs
    data_refresh_requested = pyqtSignal(str)  # controller_name
    session_expired = pyqtSignal()
    logout_requested = pyqtSignal()
