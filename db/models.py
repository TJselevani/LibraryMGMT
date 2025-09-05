# Enhanced models.py - Simplified Partial Payment System

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
    Text,
)
from sqlalchemy.orm import relationship, validates
from .database import Base
from datetime import datetime, date, timedelta


class UserRole(enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    ASSISTANT = "assistant"


class Category(enum.Enum):
    PUPIL = "pupil"
    STUDENT = "student"
    ADULT = "adult"


class Audience(enum.Enum):
    CHILDREN = "children"
    ADULT = "adult"
    YOUNG_ADULT = "young_adult"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    EXPIRED = "expired"  # New status for expired memberships


class MembershipStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    SUSPENDED = "suspended"  # if you also want suspended


# Enhanced PaymentItem with membership duration
class PaymentItem(Base):
    """
    Flexible payment items with membership duration support
    """

    __tablename__ = "payment_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    base_amount = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    supports_installments = Column(Boolean, default=False)
    max_installments = Column(Integer, default=1)
    is_category_based = Column(Boolean, default=False)

    # New membership-related fields
    is_membership = Column(Boolean, default=False)  # True for membership items
    membership_duration_months = Column(Integer, default=12)  # Duration in months

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category_prices = relationship(
        "PaymentItemPrice", back_populates="payment_item", cascade="all, delete-orphan"
    )
    payments = relationship("Payment", back_populates="payment_item")

    __table_args__ = (
        CheckConstraint(
            "base_amount IS NULL OR base_amount > 0", name="check_positive_base_amount"
        ),
        CheckConstraint("max_installments > 0", name="check_positive_max_installments"),
        CheckConstraint(
            "membership_duration_months > 0", name="check_positive_duration"
        ),
    )

    def get_amount_for_category(self, category):
        """Get the amount for a specific category"""
        if not self.is_category_based:
            return self.base_amount

        for price in self.category_prices:
            if price.category == category:
                return price.amount
        return None

    def get_amount_for_patron(self, patron):
        """Get the amount for a specific patron"""
        if not self.is_category_based:
            return self.base_amount
        return self.get_amount_for_category(patron.category)


class PaymentItemPrice(Base):
    """Category-specific pricing for payment items"""

    __tablename__ = "payment_item_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_item_id = Column(
        Integer, ForeignKey("payment_items.id", ondelete="CASCADE"), nullable=False
    )
    category = Column(Enum(Category), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    payment_item = relationship("PaymentItem", back_populates="category_prices")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_amount"),
        UniqueConstraint(
            "payment_item_id", "category", name="unique_item_category_price"
        ),
    )


# Enhanced Patron with membership expiry tracking
class Patron(Base):
    __tablename__ = "patrons"

    user_id = Column(Integer, primary_key=True)
    patron_id = Column(String(5), unique=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    institution = Column(String(200))
    grade_level = Column(String(50))
    category = Column(Enum(Category), nullable=False)
    age = Column(Integer)
    gender = Column(String(10))
    date_of_birth = Column(Date)
    residence = Column(String(200))
    phone_number = Column(String(20))

    # Enhanced membership tracking
    membership_status = Column(
        Enum(MembershipStatus), default=MembershipStatus.INACTIVE
    )
    membership_start_date = Column(Date, nullable=True)
    membership_expiry_date = Column(Date, nullable=True)
    membership_type = Column(String(100), nullable=True)  # Store payment item name

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
                return Category(category.lower())
            except ValueError:
                raise ValueError(f"Invalid category: {category}")
        return category

    def is_membership_active(self):
        """Check if membership is currently active and not expired"""
        if not self.membership_expiry_date:
            return False
        return (
            self.membership_status == MembershipStatus.ACTIVE
            and self.membership_expiry_date >= date.today()
        )

    def get_membership_days_remaining(self):
        """Get days remaining on membership"""
        if not self.membership_expiry_date:
            return 0
        remaining = (self.membership_expiry_date - date.today()).days
        return max(0, remaining)

    def expire_membership_if_needed(self):
        """Update membership status if expired"""
        if (
            self.membership_expiry_date
            and self.membership_expiry_date < date.today()
            and self.membership_status == MembershipStatus.ACTIVE
        ):
            self.membership_status = MembershipStatus.EXPIRED
            return True
        return False


# Simplified Payment model without complex installments
class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("patrons.user_id", ondelete="CASCADE"), nullable=False
    )
    payment_item_id = Column(
        Integer, ForeignKey("payment_items.id", ondelete="CASCADE"), nullable=False
    )

    # Core payment fields
    amount_paid = Column(Float, nullable=False)  # Amount actually paid
    # payment_type = Column(Text, nullable=True)
    total_amount_due = Column(Float, nullable=False)  # Total amount required
    payment_date = Column(Date, nullable=False)
    status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.PENDING)

    # Membership-specific fields
    membership_start_date = Column(Date, nullable=True)
    membership_expiry_date = Column(Date, nullable=True)
    is_membership_active = Column(Boolean, default=False)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patron = relationship("Patron", back_populates="payments")
    payment_item = relationship("PaymentItem", back_populates="payments")
    partial_payments = relationship(
        "PartialPayment", back_populates="main_payment", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("amount_paid > 0", name="check_positive_amount_paid"),
        CheckConstraint("total_amount_due > 0", name="check_positive_total_due"),
        CheckConstraint(
            "amount_paid <= total_amount_due", name="check_amount_not_exceed_total"
        ),
    )

    def get_remaining_amount(self):
        """Get remaining amount to be paid"""
        return self.total_amount_due - self.amount_paid

    def get_completion_percentage(self):
        """Get payment completion percentage"""
        return (self.amount_paid / self.total_amount_due) * 100

    def is_fully_paid(self):
        """Check if payment is fully completed"""
        return abs(self.get_remaining_amount()) < 0.01

    def update_status(self):
        """Update payment status based on amount paid"""
        if self.is_fully_paid():
            self.status = PaymentStatus.COMPLETED
            # Activate membership if it's a membership payment
            if self.payment_item.is_membership and not self.is_membership_expired():
                self.is_membership_active = True
        elif self.amount_paid > 0:
            self.status = PaymentStatus.PARTIAL
        else:
            self.status = PaymentStatus.PENDING

    def is_membership_expired(self):
        """Check if membership payment has expired"""
        if not self.payment_item.is_membership or not self.membership_expiry_date:
            return False
        return self.membership_expiry_date < date.today()

    def expire_if_needed(self):
        """Expire membership if past expiry date"""
        if self.is_membership_expired():
            self.status = PaymentStatus.EXPIRED
            self.is_membership_active = False
            return True
        return False


# New model for tracking individual partial payments
class PartialPayment(Base):
    __tablename__ = "partial_payments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_id = Column(
        Integer, ForeignKey("payments.payment_id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    payment_method = Column(String(50), nullable=True)  # cash, mpesa, etc.
    reference_number = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    main_payment = relationship("Payment", back_populates="partial_payments")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_partial_amount"),
    )


# Keep existing models (User, UserSession, Book, BorrowedBook) unchanged
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


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    author = Column(String(200), nullable=False)
    class_name = Column(String(100))
    accession_no = Column(String(20), unique=True, nullable=False)
    isbn = Column(String(20), unique=True, nullable=True)
    # publication_year = Column(String(20), nullable=True)
    is_available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    borrowed_books = relationship(
        "BorrowedBook", back_populates="book", cascade="all, delete-orphan"
    )

    categories = relationship(
        "BookCategory", secondary="book_category_associations", back_populates="books"
    )


class BookCategory(Base):
    __tablename__ = "book_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)  # e.g., "Fiction"
    audience = Column(Enum(Audience), nullable=False)  # Children / Adult / YA
    color_code = Column(String(20), nullable=True)  # e.g., "#FF5733"

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    books = relationship(
        "Book", secondary="book_category_associations", back_populates="categories"
    )


class BookCategoryAssociation(Base):
    __tablename__ = "book_category_associations"

    book_id = Column(
        Integer, ForeignKey("books.book_id", ondelete="CASCADE"), primary_key=True
    )
    category_id = Column(
        Integer, ForeignKey("book_categories.id", ondelete="CASCADE"), primary_key=True
    )


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
    due_date = Column(Date, nullable=False)
    return_date = Column(Date, nullable=True)
    returned = Column(Boolean, default=False)
    fine_amount = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

    patron = relationship("Patron", back_populates="borrowed_books")
    book = relationship("Book", back_populates="borrowed_books")

    __table_args__ = (
        CheckConstraint("fine_amount >= 0", name="check_non_negative_fine"),
        UniqueConstraint("user_id", "book_id", "returned", name="unique_active_borrow"),
    )


# Enhanced Payment Service
class PaymentService:
    """Enhanced service class for simplified partial payment system"""

    @classmethod
    def get_payment_amount(cls, payment_item, patron=None):
        """Get the expected payment amount for a payment item and patron"""
        if payment_item.is_category_based:
            if not patron:
                raise ValueError(
                    f"Patron required for category-based payment: {payment_item.name}"
                )
            return payment_item.get_amount_for_patron(patron)
        return payment_item.base_amount

    @classmethod
    def get_existing_incomplete_payment(cls, session, user_id, payment_item_name):
        """Get existing incomplete payment for the same payment item"""
        from sqlalchemy.orm import joinedload

        return (
            session.query(Payment)
            .join(PaymentItem)
            .options(joinedload(Payment.partial_payments))
            .filter(
                Payment.user_id == user_id,
                PaymentItem.name == payment_item_name,
                Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL]),
                # Only check for non-expired payments
                Payment.status != PaymentStatus.EXPIRED,
            )
            .first()
        )

    @classmethod
    def calculate_membership_dates(cls, payment_item, start_date=None):
        """Calculate membership start and expiry dates"""
        if not payment_item.is_membership:
            return None, None

        start_date = start_date or date.today()
        expiry_date = start_date + timedelta(
            days=payment_item.membership_duration_months * 30
        )

        return start_date, expiry_date

    @classmethod
    def activate_membership(cls, session, patron, payment):
        """Activate membership for patron"""
        if not payment.payment_item.is_membership or not payment.is_fully_paid():
            return False

        # Update patron membership info
        patron.membership_status = MembershipStatus.ACTIVE
        patron.membership_start_date = payment.membership_start_date
        patron.membership_expiry_date = payment.membership_expiry_date
        patron.membership_type = payment.payment_item.name

        return True

    @classmethod
    def expire_old_memberships(cls, session):
        """Expire all memberships that have passed their expiry date"""
        expired_count = 0

        # Expire payments
        expired_payments = (
            session.query(Payment)
            .join(PaymentItem)
            .filter(
                PaymentItem.is_membership.is_(True),
                Payment.membership_expiry_date < date.today(),
                Payment.status != PaymentStatus.EXPIRED,
            )
            .all()
        )

        for payment in expired_payments:
            payment.expire_if_needed()
            expired_count += 1

        # Expire patron memberships
        expired_patrons = (
            session.query(Patron)
            .filter(
                Patron.membership_expiry_date < date.today(),
                Patron.membership_status == MembershipStatus.ACTIVE,
            )
            .all()
        )

        for patron in expired_patrons:
            patron.expire_membership_if_needed()

        session.commit()
        return expired_count

    @classmethod
    def create_default_payment_items(cls, session):
        """Create default payment items with membership durations"""
        default_items = [
            {
                "name": "access",
                "display_name": "Daily Access Fee",
                "description": "Fee for daily library access",
                "base_amount": 20.0,
                "supports_installments": False,
                "is_category_based": False,
                "is_membership": False,
            },
            {
                "name": "study_room",
                "display_name": "Study Room Access",
                "description": "Fee for study room booking",
                "base_amount": 150.0,
                "supports_installments": False,
                "is_category_based": False,
                "is_membership": False,
            },
            {
                "name": "membership",
                "display_name": "Annual Membership",
                "description": "Annual library membership with full access",
                "supports_installments": True,
                "max_installments": 12,
                "is_category_based": True,
                "is_membership": True,
                "membership_duration_months": 12,
            },
            {
                "name": "quarterly_membership",
                "display_name": "Quarterly Membership",
                "description": "3-month library membership",
                "supports_installments": True,
                "max_installments": 3,
                "is_category_based": True,
                "is_membership": True,
                "membership_duration_months": 3,
            },
            {
                "name": "monthly_membership",
                "display_name": "Monthly Membership",
                "description": "1-month library membership",
                "supports_installments": False,
                "is_category_based": True,
                "is_membership": True,
                "membership_duration_months": 1,
            },
        ]

        for item_data in default_items:
            existing = (
                session.query(PaymentItem).filter_by(name=item_data["name"]).first()
            )
            if not existing:
                item = PaymentItem(**item_data)
                session.add(item)

        # Create membership category prices
        membership_items = ["membership", "quarterly_membership", "monthly_membership"]
        membership_prices = {
            "membership": {
                Category.PUPIL: 200.0,
                Category.STUDENT: 450.0,
                Category.ADULT: 600.0,
            },
            "quarterly_membership": {
                Category.PUPIL: 60.0,
                Category.STUDENT: 135.0,
                Category.ADULT: 180.0,
            },
            "monthly_membership": {
                Category.PUPIL: 25.0,
                Category.STUDENT: 50.0,
                Category.ADULT: 75.0,
            },
        }

        for item_name in membership_items:
            item = session.query(PaymentItem).filter_by(name=item_name).first()
            if item and item_name in membership_prices:
                for category, amount in membership_prices[item_name].items():
                    existing_price = (
                        session.query(PaymentItemPrice)
                        .filter_by(payment_item_id=item.id, category=category)
                        .first()
                    )
                    if not existing_price:
                        price = PaymentItemPrice(
                            payment_item_id=item.id,
                            category=category,
                            amount=amount,
                        )
                        session.add(price)

        session.commit()


# models.py
class Attendance(Base):
    __tablename__ = "attendances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    patron_id = Column(
        Integer, ForeignKey("patrons.user_id", ondelete="CASCADE"), nullable=False
    )
    attendance_date = Column(Date, default=date.today, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    patron = relationship("Patron", backref="attendances")

    __table_args__ = (
        UniqueConstraint(
            "patron_id", "attendance_date", name="unique_daily_attendance"
        ),
    )
