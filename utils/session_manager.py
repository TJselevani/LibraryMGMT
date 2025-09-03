# utils/session_manager.py
from PyQt5.QtCore import QSettings


class SessionManager:
    def __init__(self):
        self.settings = QSettings("LibrarySystem", "Auth")

    def save_session(self, session_token: str):
        self.settings.setValue("session_token", session_token)

    def get_session(self):
        return self.settings.value("session_token", None)

    def clear_session(self):
        self.settings.remove("session_token")
