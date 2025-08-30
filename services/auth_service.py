import secrets
from datetime import datetime, timedelta
from db.models import User, UserSession
from utils.session_manager import SessionManager


class AuthenticationService:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_user = None
        self.current_session = None
        self.max_login_attempts = 3
        self.lockout_duration = timedelta(minutes=15)
        self.session_manager = SessionManager()  # Use QSettings for session persistence

    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()

            if not user:
                return {"success": False, "message": "Invalid username or password"}

            if not user.is_active:
                return {"success": False, "message": "Account is deactivated"}

            # Check if account is locked
            if user.locked_until and user.locked_until > datetime.utcnow():
                remaining = user.locked_until - datetime.utcnow()
                return {
                    "success": False,
                    "message": f"Account locked. Try again in {remaining.seconds//60} minutes",
                }

            if user.verify_password(password):
                # Reset login attempts on successful login
                user.login_attempts = 0
                user.locked_until = None
                user.last_login = datetime.utcnow()

                # Create session
                session_token = secrets.token_hex(32)
                user_session = UserSession(
                    user_id=user.id,
                    session_token=session_token,
                    expires_at=datetime.utcnow() + timedelta(hours=8),
                )

                session.add(user_session)
                session.commit()

                self.current_user = user
                self.current_session = user_session

                # Save session token using QSettings
                self.session_manager.save_session(session_token)

                return {
                    "success": True,
                    "message": "Login successful",
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.full_name,
                        "role": user.role.value,
                        "session_token": session_token,
                    },
                }
            else:
                # Increment failed attempts
                user.login_attempts += 1

                if user.login_attempts >= self.max_login_attempts:
                    user.locked_until = datetime.utcnow() + self.lockout_duration
                    session.commit()
                    return {
                        "success": False,
                        "message": "Too many failed attempts. Account locked for 15 minutes",
                    }

                session.commit()
                remaining_attempts = self.max_login_attempts - user.login_attempts
                return {
                    "success": False,
                    "message": f"Invalid password. {remaining_attempts} attempts remaining",
                }

        finally:
            session.close()

    def logout(self):
        """Logout current user and invalidate session"""
        if self.current_session:
            session = self.db_manager.get_session()
            try:
                session.query(UserSession).filter_by(
                    session_token=self.current_session.session_token
                ).update({"is_active": False})
                session.commit()
            finally:
                session.close()

        # Clear session from QSettings
        self.session_manager.clear_session()

        self.current_user = None
        self.current_session = None
        return {"success": True, "message": "Logged out successfully"}

    def validate_session(self, session_token):
        """Validate session token and refresh if valid"""
        session = self.db_manager.get_session()
        try:
            user_session = (
                session.query(UserSession)
                .filter_by(session_token=session_token, is_active=True)
                .first()
            )

            if not user_session or user_session.expires_at < datetime.utcnow():
                return {"success": False, "message": "Session expired"}

            user = session.query(User).filter_by(id=user_session.user_id).first()

            if not user or not user.is_active:
                return {"success": False, "message": "User account deactivated"}

            self.current_user = user
            self.current_session = user_session
            return {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "role": user.role.value,
                    "session_token": session_token,
                },
            }

        finally:
            session.close()

    def check_existing_session(self):
        """Check if there's an existing valid session saved locally"""
        try:
            # Get saved session token from QSettings
            session_token = self.session_manager.get_session()

            if not session_token:
                return {"success": False, "message": "No saved session"}

            # Validate the session token against database
            result = self.validate_session(session_token)
            if result["success"]:
                print(
                    f"Valid existing session found for user: {result['user']['full_name']}"
                )
                return result
            else:
                # Session is invalid, clear it from storage
                self.session_manager.clear_session()
                return result

        except Exception as e:
            print(f"Error checking existing session: {e}")
            # Clear potentially corrupted session data
            self.session_manager.clear_session()
            return {"success": False, "message": "Session check failed"}

    def refresh_session(self):
        """Extend current session expiration time"""
        if not self.current_session:
            return {"success": False, "message": "No active session"}

        session = self.db_manager.get_session()
        try:
            # Update session expiration time in database
            user_session = (
                session.query(UserSession)
                .filter_by(
                    session_token=self.current_session.session_token, is_active=True
                )
                .first()
            )

            if user_session:
                # Extend session by 8 hours from current time
                new_expiry = datetime.utcnow() + timedelta(hours=8)
                user_session.expires_at = new_expiry
                session.commit()

                # Update local session object
                self.current_session.expires_at = new_expiry

                print(f"Session refreshed until: {new_expiry}")
                return {"success": True, "message": "Session refreshed"}
            else:
                # Session not found in database, clear local session
                self.session_manager.clear_session()
                self.current_user = None
                self.current_session = None
                return {"success": False, "message": "Session not found"}

        except Exception as e:
            print(f"Error refreshing session: {e}")
            return {"success": False, "message": "Session refresh failed"}
        finally:
            session.close()
