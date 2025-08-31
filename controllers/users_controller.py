from sqlalchemy.exc import IntegrityError
from datetime import datetime
from db.models import User, UserRole


class UsersController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ---------------- CREATE ----------------
    def create(
        self,
        username,
        email,
        phone_number,
        password,
        full_name,
        role=UserRole.ASSISTANT,
    ):
        """Create a new user and save to DB"""
        with self.db_manager.get_session() as session:
            try:
                new_user = User(
                    username=username,
                    email=email,
                    phone_number=phone_number,
                    full_name=full_name,
                    role=role,
                    created_at=datetime.utcnow(),
                )
                new_user.set_password(password)  # hash + salt

                session.add(new_user)
                session.commit()
                return new_user
            except IntegrityError:
                session.rollback()
                raise ValueError("Username, email, or phone number already exists")

    # ---------------- READ ----------------
    def get_by_id(self, user_id):
        """Fetch user by ID"""
        with self.db_manager.get_session() as session:
            return session.get(User, user_id)

    def get_one(self, username):
        """Fetch user by username"""
        with self.db_manager.get_session() as session:
            return session.query(User).filter_by(username=username).first()

    def get_all(self, active_only=True):
        """Get all users (optionally filter only active ones)"""
        with self.db_manager.get_session() as session:
            query = session.query(User)
            if active_only:
                query = query.filter(User.is_active.is_(True))
            return query.all()

    # ---------------- UPDATE ----------------
    def update_user(self, user_id, **kwargs):
        """Update user details"""
        with self.db_manager.get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return None

            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)

            session.commit()
            return user

    def update_password(self, user_id, new_password):
        """Update user's password"""
        with self.db_manager.get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return None
            user.set_password(new_password)
            session.commit()
            return user

    # ---------------- DELETE ----------------
    def delete_user(self, user_id):
        """Delete user by ID"""
        with self.db_manager.get_session() as session:
            user = session.get(User, user_id)
            if not user:
                return False
            session.delete(user)
            session.commit()
            return True
