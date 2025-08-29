from db.database import SessionLocal
from db.models import Patron as User


def get_all_users():
    with SessionLocal() as session:
        return session.query(User).all()


def get_one_user_by_name(name):
    """Get one user by full name (first + last)"""
    with SessionLocal() as session:
        return (
            session.query(User)
            .filter((User.first_name + " " + User.last_name) == name)
            .first()
        )  # use first() to avoid exception


def get_user_by_id(user_id):
    """Get user by ID"""
    with SessionLocal() as session:
        return session.query(User).filter(User.user_id == user_id).first()


def get_users_by_grade(grade_level: str):
    with SessionLocal() as session:
        return session.query(User).filter(User.grade_level == grade_level).all()


def add_user(first_name, last_name, grade_level, status="active"):
    with SessionLocal() as session:
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            grade_level=grade_level,
            membership_status=status,
        )
        session.add(new_user)
        session.commit()
        return new_user
