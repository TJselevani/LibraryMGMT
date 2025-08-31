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
    CheckConstraint,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship, validates
from .database import Base
from datetime import datetime


class UserRole(enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    ASSISTANT = "assistant"


class PaymentType(enum.Enum):
    ACCESS = "access"
    STUDY_ROOM = "study_room"
    MEMBERSHIP = "membership"


class GradeLevel(enum.Enum):
    PUPIL = "pupil"
    STUDENT = "student"
    ADULT = "adult"


class Category(enum.Enum):
    PUPIL = "pupil"
    STUDENT = "student"
    ADULT = "adult"


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

    sessions = relationship(
        "UserSession", back_populates="user", cascade="all, delete-orphan"
    )

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
    user_id = Column(
        Integer, ForeignKey("Users.id", ondelete="CASCADE"), nullable=False
    )
    session_token = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)

    user = relationship("User", back_populates="sessions")


class Patron(Base):
    __tablename__ = "patrons"

    user_id = Column(Integer, primary_key=True)
    patron_id = Column(String(5), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    institution = Column(String(200))
    grade_level = Column(String(50))
    category = Column(Enum(Category), nullable=False, default=Category.PUPIL)
    age = Column(Integer)
    gender = Column(String(10))
    date_of_birth = Column(Date)
    residence = Column(String(200))
    phone_number = Column(String(20))
    membership_status = Column(String(20), default="inactive")

    payments = relationship(
        "Payment", back_populates="patron", cascade="all, delete-orphan"
    )
    borrowed_books = relationship(
        "BorrowedBook", back_populates="patron", cascade="all, delete-orphan"
    )

    @validates("category")
    def validate_category(self, key, category):
        if isinstance(category, str):
            try:
                return GradeLevel(category.lower())
            except ValueError:
                raise ValueError(f"Invalid category: {category}")
        return category

    def get_membership_fee(self):
        """Get the membership fee based on grade level"""
        fee_map = {
            GradeLevel.PUPIL: 200,
            GradeLevel.STUDENT: 450,
            GradeLevel.ADULT: 600,
        }
        return fee_map.get(self.grade_level, 450)


class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("patrons.user_id", ondelete="CASCADE"), nullable=False
    )
    payment_type = Column(Enum(PaymentType), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patron = relationship("Patron", back_populates="payments")
    installments = relationship(
        "Installment", back_populates="payment", cascade="all, delete-orphan"
    )

    __table_args__ = (CheckConstraint("amount > 0", name="check_positive_amount"),)

    @validates("payment_type", "amount")
    def validate_payment(self, key, value):
        if key == "payment_type":
            if isinstance(value, str):
                try:
                    return PaymentType(value)
                except ValueError:
                    raise ValueError(f"Invalid payment type: {value}")
            return value

        elif key == "amount":
            if value <= 0:
                raise ValueError("Payment amount must be positive")
            return value

    def validate_payment_amount(self):
        """Validate that payment amount matches expected amount for type"""
        expected_amounts = {
            PaymentType.ACCESS: 20.0,
            PaymentType.STUDY_ROOM: 150.0,
            # Membership is variable based on patron grade level
        }

        if self.payment_type in expected_amounts:
            expected = expected_amounts[self.payment_type]
            if abs(self.amount - expected) > 0.01:  # Allow small rounding differences
                raise ValueError(
                    f"Invalid amount for {self.payment_type.value}: expected {expected}, got {self.amount}"
                )


class Installment(Base):
    __tablename__ = "installments"

    installment_id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(
        Integer, ForeignKey("payments.payment_id", ondelete="CASCADE"), nullable=False
    )
    installment_number = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    due_date = Column(Date, nullable=False)
    paid_date = Column(Date, nullable=True)
    is_paid = Column(Boolean, default=False)

    payment = relationship("Payment", back_populates="installments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_installment_amount"),
        CheckConstraint(
            "installment_number > 0", name="check_positive_installment_number"
        ),
        UniqueConstraint(
            "payment_id", "installment_number", name="unique_payment_installment"
        ),
    )

    @validates("installment_number", "amount")
    def validate_installment(self, key, value):
        if key == "installment_number":
            if value <= 0:
                raise ValueError("Installment number must be positive")
            return value
        elif key == "amount":
            if value <= 0:
                raise ValueError("Installment amount must be positive")
            return value


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    class_name = Column(String(100))
    accession_no = Column(String(20), unique=True, nullable=False)
    isbn = Column(String(20), unique=True, nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    borrowed_books = relationship(
        "BorrowedBook", back_populates="book", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Book(title='{self.title}', author='{self.author}', accession_no='{self.accession_no}')>"


class BorrowedBook(Base):
    __tablename__ = "borrowed_books"

    borrow_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("patrons.user_id", ondelete="CASCADE"), nullable=False
    )
    book_id = Column(
        Integer, ForeignKey("books.book_id", ondelete="CASCADE"), nullable=False
    )
    borrow_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=False)  # Add due date for better tracking
    return_date = Column(Date, nullable=True)
    returned = Column(Boolean, default=False)
    fine_amount = Column(Float, default=0.0)  # For overdue fines
    created_at = Column(DateTime, default=datetime.utcnow)

    patron = relationship("Patron", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")

    __table_args__ = (
        CheckConstraint("fine_amount >= 0", name="check_non_negative_fine"),
        # Prevent borrowing the same book multiple times while not returned
        UniqueConstraint("user_id", "book_id", "returned", name="unique_active_borrow"),
    )

    @validates("returned")
    def validate_return(self, key, returned):
        if returned and not self.return_date:
            self.return_date = datetime.utcnow().date()
        return returned

    def calculate_fine(self, daily_fine_rate=5.0):
        """Calculate fine for overdue books"""
        if not self.due_date or self.returned:
            return 0.0

        today = datetime.utcnow().date()
        if today > self.due_date:
            days_overdue = (today - self.due_date).days
            return days_overdue * daily_fine_rate
        return 0.0

    def __repr__(self):
        return f"<BorrowedBook(patron_id={self.user_id}, book_id={self.book_id}, returned={self.returned})>"


# Helper functions for business logic
class PaymentService:
    """Service class for payment-related business logic"""

    PAYMENT_AMOUNTS = {
        PaymentType.ACCESS: 20.0,
        PaymentType.STUDY_ROOM: 150.0,
    }

    MEMBERSHIP_FEES = {
        GradeLevel.PUPIL: 200.0,
        GradeLevel.STUDENT: 450.0,
        GradeLevel.ADULT: 600.0,
    }

    @classmethod
    def get_payment_amount(cls, payment_type, patron=None):
        """Get the expected payment amount for a given type and patron"""
        if payment_type == PaymentType.MEMBERSHIP:
            if not patron:
                raise ValueError("Patron required for membership payment")
            return cls.MEMBERSHIP_FEES.get(patron.grade_level, 450.0)

        return cls.PAYMENT_AMOUNTS.get(payment_type, 0.0)

    @classmethod
    def validate_payment_data(cls, payment_data, patron):
        """Validate payment data before creation"""
        errors = []

        # Validate payment type
        try:
            payment_type = PaymentType(payment_data.get("payment_type"))
        except ValueError:
            errors.append(f"Invalid payment type: {payment_data.get('payment_type')}")
            return errors

        # Validate amount
        expected_amount = cls.get_payment_amount(payment_type, patron)
        actual_amount = payment_data.get("amount", 0)

        if abs(actual_amount - expected_amount) > 0.01:
            errors.append(
                f"Invalid amount for {payment_type.value}: expected {expected_amount}, got {actual_amount}"
            )

        # Validate installments for membership
        if payment_type == PaymentType.MEMBERSHIP:
            installments = payment_data.get("installments", [])
            if installments:
                total_installments = sum(inst.get("amount", 0) for inst in installments)
                if abs(total_installments - actual_amount) > 0.01:
                    errors.append(
                        f"Installments total ({total_installments}) doesn't match payment amount ({actual_amount})"
                    )

                if len(installments) > 3:
                    errors.append("Maximum 3 installments allowed for membership")

        return errors
