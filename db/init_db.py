import pandas as pd
import random
import string
from datetime import datetime
from .database import engine, SessionLocal, Base
from .models import Patron  # , Payment, Book, BorrowedBook


def init_db():
    """
    Creates all tables in the database.
    """
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")


def generate_patron_id():
    """Generate a 5-character patron ID: 2 letters + 3 hex digits"""
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    hex_digits = "".join(random.choices("0123456789ABCDEF", k=3))
    return letters + hex_digits


def generate_unique_patron_id(session):
    while True:
        pid = generate_patron_id()
        if not session.query(Patron).filter_by(patron_id=pid).first():
            return pid


def import_users_from_csv(file_path):
    """
    Imports users from a CSV or Excel file.python -m db.init_db
    The file should have columns: first_name, last_name, institution, grade_level,
    age, date_of_birth, residence, phone_number, membership_status
    """
    session = SessionLocal()
    try:
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            # Convert date_of_birth to datetime if needed
            dob = row.get("date_of_birth")
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    dob = None

            # Get the full name
            full_name = row.get("NAME", "").strip()

            # Split into first and last name
            name_parts = full_name.split()

            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            user = Patron(
                patron_id=generate_unique_patron_id(session),
                first_name=first_name,
                last_name=last_name,
                institution=row.get("SCHOOL"),
                grade_level=row.get("GRADE"),
                age=row.get("AGE"),
                gender=row.get("GENDER"),
                date_of_birth=dob,
                residence=row.get("RESIDENCE"),
                phone_number=row.get("CONTACT"),
                membership_status="PATRON",
            )
            session.add(user)
        session.commit()
        print(f"{len(df)} users imported successfully.")
    except Exception as e:
        print("Error importing users:", e)
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    # Example usage
    init_db()

    path0 = "/home/tjselevani/Documents/REGISTER/GRADE 1 - 4 Library access list.xlsx"
    path1 = "/home/tjselevani/Documents/REGISTER/GRADE 5 - 9 Library access list.xlsx"
    path2 = "/home/tjselevani/Documents/REGISTER/"
    path3 = "/home/tjselevani/Documents/REGISTER/"

    import_users_from_csv(path1)  # Uncomment to import users

# python -m db.init_db
