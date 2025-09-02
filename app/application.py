# app/application.py
import sys
from PyQt5.QtWidgets import QApplication
from core.container import DIContainer
from app.main_window import MainWindow
from config.app_settings import AppSettings
from services.navigation_service import NavigationService
from services.data_service import DataService
from managers.session_manager import SessionManager
from utils.error_handler import ErrorHandler


class Application:
    def __init__(self, auth_service, user_info):
        self.auth_service = auth_service
        self.user_info = user_info
        self.settings = AppSettings()
        self.container = DIContainer(self.auth_service.db_manager)

    def run(self):
        app = QApplication(sys.argv)

        # Create main window
        main_window = MainWindow(
            # container=self.container,
            auth_service=self.auth_service,
            user_info=self.user_info,
            # settings=self.settings,
        )

        # Initialize supporting services
        error_handler = ErrorHandler()
        navigation_service = NavigationService()
        data_service = DataService(main_window.container)
        session_manager = SessionManager(self.auth_service)

        # Hook services into main_window
        navigation_service.navigate_requested.connect(
            lambda view_type, kwargs: main_window.navigate_to(view_type, **kwargs)
        )

        data_service.error_occurred.connect(
            lambda error: error_handler.handle_error(
                Exception(error), parent_widget=main_window
            )
        )

        session_manager.session_expired.connect(main_window.event_bus.session_expired)

        # Show the main window
        main_window.show()
        return app.exec_()


def create_application(auth_service, user_info):
    return Application(auth_service, user_info)
