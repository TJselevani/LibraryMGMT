# from typing import Dict, Any, List
from PyQt5.QtCore import QObject, pyqtSignal
from core.container import DIContainer


class DataService(QObject):
    data_loaded = pyqtSignal(str, object)
    error_occurred = pyqtSignal(str)

    def __init__(self, container: DIContainer):
        super().__init__()
        self.container = container
        self._cache = {}

    def load_data(self, controller_name: str, force_refresh=False):
        """Load data through controller"""
        try:
            if not force_refresh and controller_name in self._cache:
                self.data_loaded.emit(controller_name, self._cache[controller_name])
                return

            controller = self.container.get(controller_name)
            data = controller.get_all()
            self._cache[controller_name] = data
            self.data_loaded.emit(controller_name, data)

        except Exception as e:
            self.error_occurred.emit(str(e))


##################################################################################


class DataServiceWitchCache(QObject):
    """Service for managing data operations"""

    # Signals
    data_updated = pyqtSignal(str)  # controller_name
    data_loading = pyqtSignal(str)  # operation_description
    data_loaded = pyqtSignal(str, object)  # controller_name, data
    error_occurred = pyqtSignal(str)  # error_message

    def __init__(self, container: DIContainer):
        super().__init__()
        self.container = container
        self._cache = {}

    def get_data(self, controller_name: str, force_refresh: bool = False):
        """Get data from controller with caching"""
        if not force_refresh and controller_name in self._cache:
            self.data_loaded.emit(controller_name, self._cache[controller_name])
            return

        try:
            self.data_loading.emit(f"Loading {controller_name} data...")
            controller = self.container.get_controller(controller_name)
            if controller:
                data = controller.get_all()
                self._cache[controller_name] = data
                self.data_loaded.emit(controller_name, data)
            else:
                self.error_occurred.emit(f"Controller '{controller_name}' not found")
        except Exception as e:
            self.error_occurred.emit(f"Error loading {controller_name}: {str(e)}")

    def invalidate_cache(self, controller_name: str = None):
        """Invalidate cache for specific controller or all"""
        if controller_name:
            self._cache.pop(controller_name, None)
        else:
            self._cache.clear()
