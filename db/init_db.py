import pandas as pd
import random
import string
from datetime import datetime
from db.models import Patron
from db.database import Base
from utils.database_manager import MyDatabaseManager  # import your class


def init_db(db_manager: MyDatabaseManager):
    """
    Creates all tables in the database.
    """
    Base.metadata.create_all(bind=db_manager.engine)
    print("Database tables created successfully.")


def generate_patron_id():
    """Generate a 5-character patron ID: 2 letters + 3 hex digits"""
    letters = "".join(random.choices(string.ascii_uppercase, k=2))
    hex_digits = "".join(random.choices("0123456789ABCDEF", k=3))
    return letters + hex_digits


def generate_unique_patron_id(session):
    """Ensure uniqueness in DB for patron_id"""
    while True:
        pid = generate_patron_id()
        if not session.query(Patron).filter_by(patron_id=pid).first():
            return pid


def import_users_from_csv(db_manager: MyDatabaseManager, file_path: str):
    """
    Imports users from a CSV or Excel file.
    File must have columns: NAME, SCHOOL, GRADE, AGE, GENDER, date_of_birth, RESIDENCE, CONTACT
    """
    session = db_manager.get_session()
    try:
        # Load CSV or Excel
        if file_path.endswith(".csv"):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            # Convert date_of_birth if string
            dob = row.get("date_of_birth")
            if isinstance(dob, str):
                try:
                    dob = datetime.strptime(dob, "%Y-%m-%d").date()
                except ValueError:
                    dob = None

            # Extract name
            full_name = str(row.get("NAME", "")).strip()
            name_parts = full_name.split()
            first_name = name_parts[0] if len(name_parts) > 0 else ""
            last_name = name_parts[-1] if len(name_parts) > 1 else ""

            # Create patron
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
        print(f"{len(df)} users imported successfully from {file_path}.")

    except Exception as e:
        print("Error importing users:", e)
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    db_manager = MyDatabaseManager()

    # Create tables
    init_db(db_manager)

    # Example usage
    path1 = "/home/tjselevani/Documents/REGISTER/GRADE 5 - 9 Library access list.xlsx"
    import_users_from_csv(db_manager, path1)
