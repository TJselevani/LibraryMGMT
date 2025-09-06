# main.py
import sys
from PyQt5.QtCore import Qt, QCoreApplication

# Must be set BEFORE QApplication is created
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineView

from ui.screens.login_window import LoginWindow
from utils.database_manager import MyDatabaseManager
from services.auth_service import AuthenticationService
from app.application import create_application


class ApplicationManager:
    def __init__(self):
        self.app = QApplication(sys.argv)  # ✅ create once
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

        # ✅ Pass the already-created QApplication
        app_instance = create_application(self.app, self.auth_service, user_info)
        app_instance.run()  # no sys.exit here, since run() won’t create another app

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
