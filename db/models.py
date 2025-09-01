# Enhanced models.py - Flexible Payment System

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
from datetime import datetime


class UserRole(enum.Enum):
    ADMIN = "admin"
    LIBRARIAN = "librarian"
    ASSISTANT = "assistant"


class Category(enum.Enum):
    PUPIL = "pupil"
    STUDENT = "student"
    ADULT = "adult"


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# New flexible payment item model
class PaymentItem(Base):
    """
    Flexible payment items that can be configured dynamically.
    Replaces the hardcoded PaymentType enum approach.
    """

    __tablename__ = "payment_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(
        String(100), unique=True, nullable=False
    )  # e.g., "access", "study_room"
    display_name = Column(String(200), nullable=False)  # e.g., "Daily Access Fee"
    description = Column(Text, nullable=True)
    base_amount = Column(
        Float, nullable=True
    )  # Fixed amount for non-category-based items
    is_active = Column(Boolean, default=True)
    supports_installments = Column(Boolean, default=False)
    max_installments = Column(Integer, default=1)
    is_category_based = Column(
        Boolean, default=False
    )  # True for membership-type payments
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
    )

    def get_amount_for_category(self, category):
        """Get the amount for a specific category"""
        if not self.is_category_based:
            return self.base_amount

        # Find price for this category
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
    """
    Category-specific pricing for payment items.
    Allows different amounts for pupils, students, adults, etc.
    """

    __tablename__ = "payment_item_prices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    payment_item_id = Column(
        Integer, ForeignKey("payment_items.id", ondelete="CASCADE"), nullable=False
    )
    category = Column(Enum(Category), nullable=False)
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    payment_item = relationship("PaymentItem", back_populates="category_prices")

    __table_args__ = (
        CheckConstraint("amount > 0", name="check_positive_amount"),
        UniqueConstraint(
            "payment_item_id", "category", name="unique_item_category_price"
        ),
    )


# Keep existing models but update Payment model
class MembershipPlan(Base):
    __tablename__ = "membership_plans"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category = Column(Enum(Category), unique=True, nullable=False)
    fee = Column(Float, nullable=False)

    __table_args__ = (CheckConstraint("fee > 0", name="check_positive_fee"),)


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
    category = Column(Enum(Category), nullable=False)
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
                return Category(category.lower())
            except ValueError:
                raise ValueError(f"Invalid category: {category}")
        return category


# Updated Payment model
class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("patrons.user_id", ondelete="CASCADE"), nullable=False
    )
    payment_item_id = Column(
        Integer, ForeignKey("payment_items.id", ondelete="CASCADE"), nullable=False
    )
    amount = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)
    status = Column(
        Enum(PaymentStatus), nullable=False, default=PaymentStatus.COMPLETED
    )
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patron = relationship("Patron", back_populates="payments")
    payment_item = relationship("PaymentItem", back_populates="payments")
    installments = relationship(
        "Installment", back_populates="payment", cascade="all, delete-orphan"
    )

    __table_args__ = (CheckConstraint("amount > 0", name="check_positive_amount"),)

    def calculate_completion_percentage(self):
        """Calculate payment completion percentage based on installments"""
        if not self.installments:
            return 100.0 if self.status == PaymentStatus.COMPLETED else 0.0

        total_amount = sum(inst.amount for inst in self.installments)
        paid_amount = sum(inst.amount for inst in self.installments if inst.is_paid)

        return (paid_amount / total_amount) * 100 if total_amount > 0 else 0.0

    def update_status(self):
        """Update payment status based on installment completion"""
        if not self.installments:
            return

        completion = self.calculate_completion_percentage()

        if completion == 0:
            self.status = PaymentStatus.PENDING
        elif completion == 100:
            self.status = PaymentStatus.COMPLETED
        else:
            self.status = PaymentStatus.PARTIAL


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
    notes = Column(Text, nullable=True)

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


# Enhanced Payment Service with flexible configuration
class PaymentService:
    """Enhanced service class for payment-related business logic"""

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
    def validate_payment_data(cls, payment_data, patron, payment_item):
        """Validate payment data before creation"""
        errors = []

        # Validate amount
        expected_amount = cls.get_payment_amount(payment_item, patron)
        if expected_amount is None:
            errors.append(
                f"No price configured for {payment_item.name} and patron category {patron.category.value}"
            )
            return errors

        actual_amount = payment_data.get("amount", 0)

        # For installment payments, validate total installments match expected amount
        installments = payment_data.get("installments", [])
        if installments:
            if not payment_item.supports_installments:
                errors.append(
                    f"{payment_item.display_name} does not support installments"
                )
                return errors

            if len(installments) > payment_item.max_installments:
                errors.append(
                    f"Maximum {payment_item.max_installments} installments allowed for {payment_item.display_name}"
                )

            total_installments = sum(inst.get("amount", 0) for inst in installments)
            if abs(total_installments - expected_amount) > 0.01:
                errors.append(
                    f"Installments must total {expected_amount}, got {total_installments}"
                )
        else:
            # Full payment validation
            if abs(actual_amount - expected_amount) > 0.01:
                errors.append(
                    f"Invalid amount for {payment_item.display_name}: expected {expected_amount}, got {actual_amount}"
                )

        return errors

    @classmethod
    def create_default_payment_items(cls, session):
        """Create default payment items for initial setup"""
        default_items = [
            {
                "name": "access",
                "display_name": "Daily Access Fee",
                "description": "Fee for daily library access",
                "base_amount": 20.0,
                "supports_installments": False,
                "is_category_based": False,
            },
            {
                "name": "study_room",
                "display_name": "Study Room Access",
                "description": "Fee for study room booking",
                "base_amount": 150.0,
                "supports_installments": False,
                "is_category_based": False,
            },
            {
                "name": "membership",
                "display_name": "Annual Membership",
                "description": "Annual library membership with full access",
                "supports_installments": True,
                "max_installments": 3,
                "is_category_based": True,
            },
            {
                "name": "book_replacement",
                "display_name": "Book Replacement Fee",
                "description": "Fee for replacing lost or damaged books",
                "base_amount": 500.0,
                "supports_installments": True,
                "max_installments": 2,
                "is_category_based": False,
            },
            {
                "name": "late_return_fine",
                "display_name": "Late Return Fine",
                "description": "Fine for returning books after due date",
                "base_amount": 5.0,
                "supports_installments": False,
                "is_category_based": False,
            },
        ]

        for item_data in default_items:
            # Check if item already exists
            existing = (
                session.query(PaymentItem).filter_by(name=item_data["name"]).first()
            )
            if not existing:
                item = PaymentItem(**item_data)
                session.add(item)

        # Create membership category prices
        membership_item = (
            session.query(PaymentItem).filter_by(name="membership").first()
        )
        if membership_item:
            membership_prices = [
                {"category": Category.PUPIL, "amount": 200.0},
                {"category": Category.STUDENT, "amount": 450.0},
                {"category": Category.ADULT, "amount": 600.0},
            ]

            for price_data in membership_prices:
                existing_price = (
                    session.query(PaymentItemPrice)
                    .filter_by(
                        payment_item_id=membership_item.id,
                        category=price_data["category"],
                    )
                    .first()
                )

                if not existing_price:
                    price = PaymentItemPrice(
                        payment_item_id=membership_item.id, **price_data
                    )
                    session.add(price)

        session.commit()


# Enhanced Payment Item Controller
class PaymentItemController:
    """Controller for managing payment items and their configurations"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all_active_items(self):
        """Get all active payment items"""
        with self.db_manager.get_session() as session:
            return (
                session.query(PaymentItem).filter(PaymentItem.is_active.is_(True)).all()
            )

    def get_item_by_name(self, name):
        """Get payment item by name"""
        with self.db_manager.get_session() as session:
            return session.query(PaymentItem).filter(PaymentItem.name == name).first()

    def create_payment_item(self, item_data):
        """Create a new payment item"""
        try:
            with self.db_manager.get_session() as session:
                # Validate required fields
                required_fields = ["name", "display_name"]
                for field in required_fields:
                    if field not in item_data or not item_data[field]:
                        return {
                            "success": False,
                            "message": f"Missing required field: {field}",
                        }

                # Check for duplicate name
                existing = (
                    session.query(PaymentItem).filter_by(name=item_data["name"]).first()
                )
                if existing:
                    return {
                        "success": False,
                        "message": f"Payment item with name '{item_data['name']}' already exists",
                    }

                # Create payment item
                payment_item = PaymentItem(**item_data)
                session.add(payment_item)
                session.flush()  # Get ID

                # Create category prices if specified
                if item_data.get("category_prices"):
                    for price_data in item_data["category_prices"]:
                        price = PaymentItemPrice(
                            payment_item_id=payment_item.id,
                            category=Category(price_data["category"]),
                            amount=price_data["amount"],
                        )
                        session.add(price)

                session.commit()
                session.refresh(payment_item)

                return {
                    "success": True,
                    "payment_item": payment_item,
                    "message": f"Payment item '{payment_item.display_name}' created successfully",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating payment item: {str(e)}",
            }

    def update_payment_item(self, item_id, update_data):
        """Update a payment item"""
        try:
            with self.db_manager.get_session() as session:
                item = (
                    session.query(PaymentItem).filter(PaymentItem.id == item_id).first()
                )
                if not item:
                    return {"success": False, "message": "Payment item not found"}

                # Update basic fields
                for key, value in update_data.items():
                    if key != "category_prices" and hasattr(item, key):
                        setattr(item, key, value)

                # Update category prices if provided
                if "category_prices" in update_data:
                    # Remove existing prices
                    session.query(PaymentItemPrice).filter_by(
                        payment_item_id=item.id
                    ).delete()

                    # Add new prices
                    for price_data in update_data["category_prices"]:
                        price = PaymentItemPrice(
                            payment_item_id=item.id,
                            category=Category(price_data["category"]),
                            amount=price_data["amount"],
                        )
                        session.add(price)

                item.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(item)

                return {
                    "success": True,
                    "payment_item": item,
                    "message": f"Payment item '{item.display_name}' updated successfully",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating payment item: {str(e)}",
            }

    def deactivate_payment_item(self, item_id):
        """Deactivate a payment item (soft delete)"""
        return self.update_payment_item(item_id, {"is_active": False})

    def get_payment_items_for_patron(self, patron):
        """Get all payment items with their amounts for a specific patron"""
        with self.db_manager.get_session() as session:
            items = (
                session.query(PaymentItem).filter(PaymentItem.is_active.is_(True)).all()
            )

            result = []
            for item in items:
                amount = item.get_amount_for_patron(patron)
                if amount is not None:  # Only include items with valid pricing
                    result.append(
                        {
                            "item": item,
                            "amount": amount,
                            "formatted_display": f"{item.display_name} - KSh {amount:.2f}",
                        }
                    )

            return result
