from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, UserRole
from db.database import Base


class MyDatabaseManager:
    def __init__(self, db_path="library_system.db"):
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def get_session(self):
        return self.SessionLocal()

    def create_default_admin(self):
        """Create default admin user if none exists"""
        session = self.get_session()
        try:
            admin_exists = session.query(User).filter_by(role=UserRole.ADMIN).first()
            if not admin_exists:
                admin_user = User(
                    username="admin",
                    email="admin@library.system",
                    phone_number="0723452345",
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                    is_active=True,
                )
                admin_user.set_password("admin123")  # Should be changed on first login
                session.add(admin_user)
                session.commit()
                print(
                    "Default admin user created: username='admin', password='admin123'"
                )
        finally:
            session.close()
