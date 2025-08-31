import random
import string
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from db.models import Patron


class PatronsController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self):
        with self.db_manager.get_session() as session:
            return session.query(Patron).all()

    def get_patron_by_id(self, user_id):
        with self.db_manager.get_session() as session:
            return session.query(Patron).filter(Patron.user_id == user_id).first()

    def get_patron_by_patron_id(self, patron_id):
        """Get patron by patron ID"""
        with self.db_manager.get_session() as session:
            return session.query(Patron).filter(Patron.patron_id == patron_id).first()

    def get_patron_by_name(self, first_name, last_name=None):
        """Get patron by name"""
        with self.db_manager.get_session() as session:
            if last_name:
                return (
                    session.query(Patron)
                    .filter(
                        Patron.first_name == first_name, Patron.last_name == last_name
                    )
                    .first()
                )
            else:
                # Search by full name if only one parameter provided
                return (
                    session.query(Patron)
                    .filter((Patron.first_name + " " + Patron.last_name) == first_name)
                    .first()
                )

    def get_patrons_by_institution(self, institution):
        """Get all patrons from a specific institution"""
        with self.db_manager.get_session() as session:
            return session.query(Patron).filter(Patron.institution == institution).all()

    def get_patrons_by_grade(self, grade_level):
        """Get all patrons in a specific grade level"""
        with self.db_manager.get_session() as session:
            return session.query(Patron).filter(Patron.grade_level == grade_level).all()

    def get_patrons_by_status(self, membership_status):
        """Get all patrons with a specific membership status"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Patron)
                .filter(Patron.membership_status == membership_status)
                .all()
            )

    def search_patrons(self, search_term):
        """Search patrons by name, patron ID, or phone number"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Patron)
                .filter(
                    (Patron.first_name.contains(search_term))
                    | (Patron.last_name.contains(search_term))
                    | (Patron.patron_id.contains(search_term))
                    | (Patron.phone_number.contains(search_term))
                )
                .all()
            )

    @staticmethod
    def generate_patron_id():
        """Generate a 5-character patron ID: 2 letters + 3 hex digits"""
        letters = "".join(random.choices(string.ascii_uppercase, k=2))
        hex_digits = "".join(random.choices("0123456789ABCDEF", k=3))
        return letters + hex_digits

    def generate_unique_patron_id(self):
        with self.db_manager.get_session() as session:

            while True:
                pid = self.generate_patron_id()
                if not session.query(Patron).filter_by(patron_id=pid).first():
                    return pid

    def create(self, patron_data):
        """Create a new patron"""
        try:
            with self.db_manager.get_session() as session:
                # Generate patron ID if not provided
                if "patron_id" not in patron_data or not patron_data["patron_id"]:
                    patron_data["patron_id"] = self.generate_unique_patron_id()

                # Convert date string to date object if needed
                if "date_of_birth" in patron_data and isinstance(
                    patron_data["date_of_birth"], str
                ):
                    patron_data["date_of_birth"] = datetime.strptime(
                        patron_data["date_of_birth"], "%Y-%m-%d"
                    ).date()

                new_patron = Patron(**patron_data)
                session.add(new_patron)
                session.commit()
                session.refresh(new_patron)
                return {
                    "success": True,
                    "patron": new_patron,
                    "message": "Patron created successfully",
                }

        except IntegrityError as e:
            return {
                "success": False,
                "message": f"Patron ID, phone number, or other unique field already exists {e}",
            }
        except Exception as e:
            return {"success": False, "message": f"Error creating patron: {str(e)}"}

    def update_patron(self, user_id, update_data):
        """Update patron information"""
        try:
            with self.db_manager.get_session() as session:
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()

                if not patron:
                    return {"success": False, "message": "Patron not found"}

                # Convert date string to date object if needed
                if "date_of_birth" in update_data and isinstance(
                    update_data["date_of_birth"], str
                ):
                    update_data["date_of_birth"] = datetime.strptime(
                        update_data["date_of_birth"], "%Y-%m-%d"
                    ).date()

                # Update patron attributes
                for key, value in update_data.items():
                    if hasattr(patron, key):
                        setattr(patron, key, value)

                session.commit()
                session.refresh(patron)
                return {
                    "success": True,
                    "patron": patron,
                    "message": "Patron updated successfully",
                }

        except IntegrityError:
            return {
                "success": False,
                "message": "Update failed: Duplicate value for unique field",
            }
        except Exception as e:
            return {"success": False, "message": f"Error updating patron: {str(e)}"}

    def delete_patron(self, user_id):
        """Delete patron by user ID"""
        try:
            with self.db_manager.get_session() as session:
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()

                if not patron:
                    return {"success": False, "message": "Patron not found"}

                # Check if patron has active borrowed books
                from db.models import BorrowedBook

                active_books = (
                    session.query(BorrowedBook)
                    .filter(
                        BorrowedBook.user_id == user_id,
                        BorrowedBook.returned.is_(False),
                    )
                    .count()
                )

                if active_books > 0:
                    return {
                        "success": False,
                        "message": f"Cannot delete patron with {active_books} unreturned books",
                    }

                session.delete(patron)
                session.commit()
                return {"success": True, "message": "Patron deleted successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error deleting patron: {str(e)}"}

    def activate_patron(self, user_id):
        """Activate a patron's membership"""
        return self.update_patron(user_id, {"membership_status": "active"})

    def deactivate_patron(self, user_id):
        """Deactivate a patron's membership"""
        return self.update_patron(user_id, {"membership_status": "inactive"})

    def get_patron_statistics(self):
        """Get patron statistics"""
        with self.db_manager.get_session() as session:
            total_patrons = session.query(Patron).count()
            active_patrons = (
                session.query(Patron)
                .filter(Patron.membership_status == "active")
                .count()
            )
            inactive_patrons = (
                session.query(Patron)
                .filter(Patron.membership_status == "inactive")
                .count()
            )

            return {
                "total": total_patrons,
                "active": active_patrons,
                "inactive": inactive_patrons,
            }

    def get_membership_fee(self, patron_id):
        with self.db_manager.get_session() as session:
            patron = session.query(Patron).filter_by(user_id=patron_id).first()
            return patron.get_membership_fee(session)
