# app/application.py
from app.main_window import MainWindow
from config.app_settings import AppSettings
from services.navigation_service import NavigationService
from services.data_service import DataService
from managers.session_manager import SessionManager
from utils.error_handler import ErrorHandler


class Application:
    def __init__(self, app, auth_service, user_info):
        self.app = app
        self.auth_service = auth_service
        self.user_info = user_info
        self.settings = AppSettings()
        from core.container import DIContainer

        self.container = DIContainer(self.auth_service.db_manager)

    def run(self):
        # Create main window
        main_window = MainWindow(
            auth_service=self.auth_service,
            user_info=self.user_info,
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


def create_application(app, auth_service, user_info):
    return Application(app, auth_service, user_info)
