# config/session_config.py
from datetime import timedelta


class SessionConfig:
    # Session duration (how long sessions last)
    SESSION_DURATION = timedelta(hours=8)

    # Session refresh interval (how often to refresh session in the background)
    REFRESH_INTERVAL = timedelta(minutes=30)

    # Session file name (where to store session data locally)
    SESSION_FILE = "session.json"

    # Whether to enable auto-login (session persistence)
    AUTO_LOGIN_ENABLED = True

    # Whether to enable session refresh (extends session automatically)
    SESSION_REFRESH_ENABLED = True
