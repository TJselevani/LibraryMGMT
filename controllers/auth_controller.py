import secrets
import json
import os
from datetime import datetime, timedelta
from db.models import User, UserSession as Session


class AuthenticationController:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.current_user = None
        self.current_session = None
        self.max_login_attempts = 3
        self.lockout_duration = timedelta(minutes=15)
        self.session_file = "session.json"  # File to store session data

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
                user_session = Session(
                    user_id=user.id,
                    session_token=session_token,
                    expires_at=datetime.utcnow() + timedelta(hours=8),
                )

                session.add(user_session)
                session.commit()

                self.current_user = user
                self.current_session = user_session

                # Save session to file for persistence
                self._save_session_to_file(session_token)

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
                session.query(Session).filter_by(
                    session_token=self.current_session.session_token
                ).update({"is_active": False})
                session.commit()
            finally:
                session.close()

        # Clear session file
        self._clear_session_file()

        self.current_user = None
        self.current_session = None
        return {"success": True, "message": "Logged out successfully"}

    def validate_session(self, session_token):
        """Validate session token and refresh if valid"""
        session = self.db_manager.get_session()
        try:
            user_session = (
                session.query(Session)
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
            if not os.path.exists(self.session_file):
                return {"success": False, "message": "No saved session"}

            with open(self.session_file, "r") as f:
                session_data = json.load(f)

            session_token = session_data.get("session_token")
            if not session_token:
                return {"success": False, "message": "Invalid session data"}

            # Validate the session token against database
            result = self.validate_session(session_token)
            if result["success"]:
                # Session is still valid, update the file with fresh timestamp
                self._save_session_to_file(session_token)
                return result
            else:
                # Session is invalid, clear the file
                self._clear_session_file()
                return result

        except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
            # If there's any error reading the session file, clear it
            self._clear_session_file()
            return {"success": False, "message": f"Session file corrupted, {e}"}

    def _save_session_to_file(self, session_token):
        """Save session token to local file"""
        try:
            session_data = {
                "session_token": session_token,
                "saved_at": datetime.utcnow().isoformat(),
            }
            with open(self.session_file, "w") as f:
                json.dump(session_data, f)
        except Exception as e:
            print(f"Error saving session: {e}")

    def _clear_session_file(self):
        """Clear the session file"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
        except Exception as e:
            print(f"Error clearing session file: {e}")

    def change_password(self, old_password, new_password):
        """Change password for current user"""
        if not self.current_user:
            return {"success": False, "message": "No user logged in"}

        if not self.current_user.verify_password(old_password):
            return {"success": False, "message": "Current password is incorrect"}

        if len(new_password) < 6:
            return {
                "success": False,
                "message": "New password must be at least 6 characters long",
            }

        session = self.db_manager.get_session()
        try:
            user = session.query(User).filter_by(id=self.current_user.id).first()
            user.set_password(new_password)
            session.commit()
            return {"success": True, "message": "Password changed successfully"}
        finally:
            session.close()

    def has_permission(self, required_role):
        """Check if current user has required permission"""
        if not self.current_user:
            return False
        return self.current_user.has_permission(required_role)

    def refresh_session(self):
        """Extend current session expiration time"""
        if not self.current_session:
            return {"success": False, "message": "No active session"}

        session = self.db_manager.get_session()
        try:
            # Update session expiration time
            user_session = (
                session.query(Session)
                .filter_by(session_token=self.current_session.session_token)
                .first()
            )

            if user_session:
                user_session.expires_at = datetime.utcnow() + timedelta(hours=8)
                session.commit()
                self.current_session.expires_at = user_session.expires_at

                # Update saved session file
                self._save_session_to_file(self.current_session.session_token)

                return {"success": True, "message": "Session refreshed"}
            else:
                return {"success": False, "message": "Session not found"}

        finally:
            session.close()
