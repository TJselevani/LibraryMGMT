import sys
from PyQt5.QtWidgets import QApplication
from db.database import Base, engine
from ui.screens.main_Window import MainWindow
from ui.screens.login_window import LoginWindow
from utils.database_manager import MyDatabaseManager
from services.auth_service import AuthenticationService


# Create tables if not exist
Base.metadata.create_all(engine)


def main():
    app = QApplication(sys.argv)

    # Initialize database
    db_manager = MyDatabaseManager()
    db_manager.create_default_admin()

    # Initialize authentication service
    auth_service = AuthenticationService(db_manager)

    # Create and show login window
    login_window = LoginWindow(auth_service)

    def on_login_success(user_info):
        """Handle successful login"""
        login_window.hide()
        main_window = MainWindow(auth_service, user_info)
        main_window.show()

        # Handle main window close
        def on_main_window_close():
            app.quit()

        main_window.destroyed.connect(on_main_window_close)

    login_window.login_successful.connect(on_login_success)
    login_window.show()

    # window = MainWindow()
    # window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
