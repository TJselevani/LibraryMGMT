import enum
import hashlib
import secrets
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Date,
    ForeignKey,
    Float,
    Boolean,
    Enum,
)
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime


class UserRole(enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    ASSISTANT = "assistant"


class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone_number = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(32), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.ASSISTANT)
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # sessions = relationship("UserSession", back_populates="user")

    def set_password(self, password):
        """Hash and set password with salt"""
        self.salt = secrets.token_hex(16)
        password_salt = password + self.salt
        self.password_hash = hashlib.sha256(password_salt.encode()).hexdigest()

    def verify_password(self, password):
        """Verify password against stored hash"""
        password_salt = password + self.salt
        return hashlib.sha256(password_salt.encode()).hexdigest() == self.password_hash

    def has_permission(self, required_role):
        """Check if user has required permission level"""
        role_hierarchy = {
            UserRole.ASSISTANT: 1,
            UserRole.LIBRARIAN: 2,
            UserRole.ADMIN: 3,
        }
        return role_hierarchy[self.role] >= role_hierarchy[required_role]


class UserSession(Base):
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    # user = relationship("User", back_populates="sessions")


class Patron(Base):
    __tablename__ = "patrons"

    user_id = Column(Integer, primary_key=True)
    patron_id = Column(String(5), unique=True)
    first_name = Column(String)
    last_name = Column(String)
    institution = Column(String)
    grade_level = Column(String)
    age = Column(String)
    gender = Column(String)
    date_of_birth = Column(Date)
    residence = Column(String)
    phone_number = Column(String)
    membership_status = Column(String)

    payments = relationship("Payment", back_populates="patron")
    borrowed_books = relationship("BorrowedBook", back_populates="patron")


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("patrons.user_id"))
    payment_type = Column(String)  # access / membership, daily, partial, full
    amount = Column(Float)
    payment_date = Column(Date)

    patron = relationship("Patron", back_populates="payments")
    installments = relationship("Installment", back_populates="payment")


class Installment(Base):
    __tablename__ = "installments"

    installment_id = Column(Integer, primary_key=True)
    payment_id = Column(Integer, ForeignKey("payments.payment_id"))
    installment_number = Column(Integer)  # 1, 2, 3
    amount = Column(Float)
    date = Column(Date)

    payment = relationship("Payment", back_populates="installments")


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True)
    title = Column(String)
    author = Column(String)
    class_name = Column(String)
    accession_no = Column(String, unique=True)

    borrowed_books = relationship("BorrowedBook", back_populates="book")


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    borrow_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("patrons.user_id"))
    book_id = Column(Integer, ForeignKey("books.book_id"))
    borrow_date = Column(Date)
    return_date = Column(Date)
    returned = Column(Boolean, default=False)

    patron = relationship("Patron", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")
