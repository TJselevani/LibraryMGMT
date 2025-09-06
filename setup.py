# seed_data.py – Populate library_system with dummy data

from datetime import date, timedelta
import random
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.database import Base
from db.models import (
    User,
    UserRole,
    Patron,
    Category,
    MembershipStatus,
    Book,
    BorrowedBook,
    Payment,
    PaymentStatus,
    PaymentItem,
    PaymentService,
)

# ⚠️ Change this to your actual DB URL
DATABASE_URL = "sqlite:///library_system.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def create_tables():
    """Create tables if not already existing"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def seed_users(session):
    """Seed system users (staff)"""
    users = [
        User(
            username="admin",
            email="admin@example.com",
            phone_number="0700000000",
            full_name="System Administrator",
            role=UserRole.ADMIN,
        ),
        User(
            username="librarian",
            email="librarian@example.com",
            phone_number="0711111111",
            full_name="Main Librarian",
            role=UserRole.LIBRARIAN,
        ),
        User(
            username="assistant",
            email="assistant@example.com",
            phone_number="0722222222",
            full_name="Assistant Staff",
            role=UserRole.ASSISTANT,
        ),
    ]

    for u in users:
        u.set_password("password123")

    session.add_all(users)
    print("👤 Users seeded")


def seed_payment_items(session):
    """Seed default payment items using PaymentService"""
    PaymentService.create_default_payment_items(session)
    print("💳 Payment items seeded")


def seed_patrons(session):
    """Seed dummy patrons"""
    patrons = [
        Patron(
            patron_id="P001",
            first_name="Alice",
            last_name="Johnson",
            institution="Greenwood Primary",
            grade_level="5",
            category=Category.PUPIL,
            age=10,
            gender="Female",
            date_of_birth=date(2014, 6, 5),
            residence="Springfield",
            phone_number="0733333333",
            membership_status=MembershipStatus.INACTIVE,
        ),
        Patron(
            patron_id="S001",
            first_name="Bob",
            last_name="Smith",
            institution="Lakeside University",
            grade_level="2nd Year",
            category=Category.STUDENT,
            age=20,
            gender="Male",
            date_of_birth=date(2005, 1, 14),
            residence="Lakeside",
            phone_number="0744444444",
            membership_status=MembershipStatus.INACTIVE,
        ),
        Patron(
            patron_id="A001",
            first_name="Clara",
            last_name="Miller",
            institution="Community Center",
            grade_level=None,
            category=Category.ADULT,
            age=35,
            gender="Female",
            date_of_birth=date(1990, 9, 23),
            residence="Downtown",
            phone_number="0755555555",
            membership_status=MembershipStatus.INACTIVE,
        ),
    ]
    session.add_all(patrons)
    print("📚 Patrons seeded")


def seed_books(session):
    """Seed dummy books"""
    books = [
        Book(
            title="Python for Beginners",
            author="Jane Doe",
            class_name="CS101",
            accession_no="ACC001",
            isbn="1111111111",
        ),
        Book(
            title="Database Systems",
            author="John Smith",
            class_name="CS202",
            accession_no="ACC002",
            isbn="2222222222",
        ),
        Book(
            title="Artificial Intelligence",
            author="Ada Lovelace",
            class_name="CS303",
            accession_no="ACC003",
            isbn="3333333333",
        ),
    ]
    session.add_all(books)
    print("📖 Books seeded")


def seed_payments_and_memberships(session):
    """Seed payments for patrons (link to memberships)"""
    patrons = session.query(Patron).all()
    membership_item = session.query(PaymentItem).filter_by(name="membership").first()

    if not membership_item:
        print("⚠️ No membership item found, skipping payments.")
        return

    for patron in patrons:
        start, expiry = PaymentService.calculate_membership_dates(membership_item)
        total_due = membership_item.get_amount_for_patron(patron)
        paid = total_due if random.choice([True, False]) else total_due / 2

        payment = Payment(
            user_id=patron.user_id,
            payment_item_id=membership_item.id,
            amount_paid=paid,
            total_amount_due=total_due,
            payment_date=date.today() - timedelta(days=random.randint(1, 90)),
            status=(
                PaymentStatus.COMPLETED if paid == total_due else PaymentStatus.PARTIAL
            ),
            membership_start_date=start,
            membership_expiry_date=expiry,
            is_membership_active=(paid == total_due),
        )
        session.add(payment)

        if payment.is_fully_paid():
            PaymentService.activate_membership(session, patron, payment)

    print("💰 Payments & memberships seeded")


def seed_borrowed_books(session):
    """Seed borrowed books (link patrons -> books)"""
    patrons = session.query(Patron).all()
    books = session.query(Book).all()

    for patron in patrons:
        book = random.choice(books)
        borrow = BorrowedBook(
            user_id=patron.user_id,
            book_id=book.book_id,
            borrow_date=date.today() - timedelta(days=10),
            due_date=date.today() + timedelta(days=20),
            returned=False,
            fine_amount=0.0,
        )
        session.add(borrow)

    print("📕 Borrowed books seeded")


def run_seed():
    session = SessionLocal()
    try:
        create_tables()
        seed_users(session)
        seed_payment_items(session)
        seed_patrons(session)
        seed_books(session)
        session.commit()  # Commit before linking payments/borrows
        seed_payments_and_memberships(session)
        seed_borrowed_books(session)
        session.commit()
        print("🎉 Dummy data seeding complete!")
    except Exception as e:
        session.rollback()
        print(f"❌ Error seeding data: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    run_seed()
