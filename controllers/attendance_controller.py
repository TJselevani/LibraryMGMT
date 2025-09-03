# controllers/attendance_controller.py
from db.models import Attendance, Patron
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload


class AttendanceController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def mark_attendance(self, patron_id, attendance_date=None):
        """Mark attendance for a patron on a specific date"""
        attendance_date = attendance_date or date.today()
        session: Session = self.db_manager.get_session()

        try:
            # Check for existing attendance to prevent duplicates
            existing = (
                session.query(Attendance)
                .filter_by(patron_id=patron_id, attendance_date=attendance_date)
                .first()
            )

            if existing:
                return existing

            # Create new attendance record
            attendance = Attendance(
                patron_id=patron_id,
                attendance_date=attendance_date,
                created_at=datetime.now(),  # Add timestamp if your model supports it
            )
            session.add(attendance)
            session.commit()
            session.refresh(attendance)  # Refresh to get the ID and relationships

            return attendance

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def remove_attendance(self, attendance_id):
        """Remove an attendance record by ID"""
        session: Session = self.db_manager.get_session()

        try:
            attendance = session.query(Attendance).filter_by(id=attendance_id).first()

            if not attendance:
                return False

            session.delete(attendance)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def remove_attendance_by_patron(self, patron_id, attendance_date=None):
        """Remove attendance for a specific patron on a specific date"""
        attendance_date = attendance_date or date.today()
        session: Session = self.db_manager.get_session()

        try:
            attendance = (
                session.query(Attendance)
                .filter_by(patron_id=patron_id, attendance_date=attendance_date)
                .first()
            )

            if not attendance:
                return False

            session.delete(attendance)
            session.commit()
            return True

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_attendance_by_date(self, attendance_date=None):
        """Get all attendance records for a specific date"""
        attendance_date = attendance_date or date.today()
        session: Session = self.db_manager.get_session()

        try:
            attendances = (
                session.query(Attendance)
                .options(joinedload(Attendance.patron))  # Eager load patron
                .filter_by(attendance_date=attendance_date)
                .join(Patron)  # Join with patron to load relationship data
                .order_by(Attendance.id.desc())  # Most recent first
                .all()
            )
            return attendances

        except Exception as e:
            raise e
        finally:
            session.close()

    def get_attendance_by_patron(self, patron_id, start_date=None, end_date=None):
        """Get attendance records for a specific patron within a date range"""
        session: Session = self.db_manager.get_session()

        try:
            query = session.query(Attendance).filter_by(patron_id=patron_id)

            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)

            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)

            attendances = query.order_by(Attendance.attendance_date.desc()).all()
            return attendances

        except Exception as e:
            raise e
        finally:
            session.close()

    def get_attendance_statistics(self, start_date=None, end_date=None):
        """Get attendance statistics for a date range"""
        session: Session = self.db_manager.get_session()

        try:
            query = session.query(Attendance)

            if start_date:
                query = query.filter(Attendance.attendance_date >= start_date)

            if end_date:
                query = query.filter(Attendance.attendance_date <= end_date)

            total_attendance = query.count()
            unique_patrons = (
                query.with_entities(Attendance.patron_id).distinct().count()
            )

            # Get attendance by date
            from sqlalchemy import func

            daily_attendance = (
                query.with_entities(
                    Attendance.attendance_date, func.count(Attendance.id).label("count")
                )
                .group_by(Attendance.attendance_date)
                .order_by(Attendance.attendance_date.desc())
                .all()
            )

            return {
                "total_attendance": total_attendance,
                "unique_patrons": unique_patrons,
                "daily_attendance": daily_attendance,
            }

        except Exception as e:
            raise e
        finally:
            session.close()

    def search_patrons(self, query_text):
        """Search for patrons by name, ID, or institution"""
        if not query_text or len(query_text.strip()) < 2:
            return []

        session: Session = self.db_manager.get_session()

        try:
            query_text = query_text.strip().lower()

            patrons = (
                session.query(Patron)
                .filter(
                    (Patron.first_name.ilike(f"%{query_text}%"))
                    | (Patron.last_name.ilike(f"%{query_text}%"))
                    | (Patron.patron_id.ilike(f"%{query_text}%"))
                    | (Patron.institution.ilike(f"%{query_text}%"))
                )
                .order_by(Patron.first_name, Patron.last_name)
                .limit(20)  # Limit results for performance
                .all()
            )

            return patrons

        except Exception as e:
            raise e
        finally:
            session.close()

    def is_patron_present(self, patron_id, attendance_date=None):
        """Check if a patron is marked present on a specific date"""
        attendance_date = attendance_date or date.today()
        session: Session = self.db_manager.get_session()

        try:
            attendance = (
                session.query(Attendance)
                .filter_by(patron_id=patron_id, attendance_date=attendance_date)
                .first()
            )

            return attendance is not None

        except Exception as e:
            raise e
        finally:
            session.close()

    def get_patrons_present_today(self):
        """Get list of patrons present today"""
        return self.get_patrons_present_on_date(date.today())

    def get_patrons_present_on_date(self, attendance_date):
        """Get list of patrons present on a specific date"""
        session: Session = self.db_manager.get_session()

        try:
            patrons = (
                session.query(Patron)
                .join(Attendance)
                .filter(Attendance.attendance_date == attendance_date)
                .order_by(Patron.first_name, Patron.last_name)
                .all()
            )

            return patrons

        except Exception as e:
            raise e
        finally:
            session.close()

    def bulk_mark_attendance(self, patron_ids, attendance_date=None):
        """Mark attendance for multiple patrons at once"""
        attendance_date = attendance_date or date.today()
        session: Session = self.db_manager.get_session()

        try:
            created_count = 0
            existing_count = 0

            for patron_id in patron_ids:
                # Check if already exists
                existing = (
                    session.query(Attendance)
                    .filter_by(patron_id=patron_id, attendance_date=attendance_date)
                    .first()
                )

                if existing:
                    existing_count += 1
                    continue

                # Create new attendance
                attendance = Attendance(
                    patron_id=patron_id,
                    attendance_date=attendance_date,
                    created_at=datetime.now(),
                )
                session.add(attendance)
                created_count += 1

            session.commit()

            return {
                "created": created_count,
                "existing": existing_count,
                "total_processed": len(patron_ids),
            }

        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
