# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.screens.main_Window import MainWindow
from ui.screens.login_window import LoginWindow
from utils.database_manager import MyDatabaseManager
from services.auth_service import AuthenticationService


class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.db_manager = None
        self.auth_service = None
        self.login_window = None
        self.main_window = None

    def initialize_services(self):
        """Initialize database and authentication services"""
        self.db_manager = MyDatabaseManager()
        self.db_manager.create_default_admin()
        self.auth_service = AuthenticationService(self.db_manager)

    def launch_main_window(self, user_info):
        if self.login_window:
            self.login_window.hide()
        self.main_window = MainWindow(self.auth_service, user_info)
        self.main_window.show()

        def on_main_window_close():
            if getattr(self.main_window, "logout_requested", False):
                self.show_login_window()
            else:
                self.app.quit()

        self.main_window.destroyed.connect(on_main_window_close)

    def show_login_window(self):
        self.login_window = LoginWindow(self.auth_service)
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()

    def on_login_success(self, user_info):
        self.launch_main_window(user_info)

    def check_existing_session(self):
        try:
            result = self.auth_service.check_existing_session()
            if result["success"]:
                print(f"Existing session found for user: {result['user']['full_name']}")
                return result["user"]
            else:
                print("No valid existing session found")
                return None
        except Exception as e:
            print(f"Error checking session: {e}")
            return None

    def run(self):
        self.initialize_services()
        existing_user = self.check_existing_session()

        if existing_user:
            self.launch_main_window(existing_user)
        else:
            self.show_login_window()

        return self.app.exec_()


def main():
    app_manager = ApplicationManager()
    sys.exit(app_manager.run())


if __name__ == "__main__":
    main()
