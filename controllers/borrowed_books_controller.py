# from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta
from db.models import BorrowedBook, Patron, Book
from sqlalchemy.orm import joinedload
from typing import Dict, List


class BorrowedBooksController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self):
        """Get all borrowed books with book and patron details"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BorrowedBook)
                .options(joinedload(BorrowedBook.book), joinedload(BorrowedBook.patron))
                .all()
            )

    def create(self, borrow_data: Dict) -> Dict:
        with self.db_manager.get_session() as session:
            try:
                # use session instead of self.db
                patron = (
                    session.query(Patron)
                    .filter(Patron.user_id == borrow_data.get("user_id"))
                    .first()
                )
                if not patron:
                    return {
                        "success": False,
                        "message": f"Patron {borrow_data.get('user_id')} not found",
                    }

                book = (
                    session.query(Book)
                    .filter(Book.book_id == borrow_data.get("book_id"))
                    .first()
                )
                if not book:
                    return {
                        "success": False,
                        "message": f"Book {borrow_data.get('book_id')} not found",
                    }

                if not getattr(book, "is_available", True):
                    return {
                        "success": False,
                        "message": f"Book '{book.title}' not available",
                    }

                # check duplicate borrow
                existing_borrow = (
                    session.query(BorrowedBook)
                    .filter(
                        BorrowedBook.user_id == borrow_data["user_id"],
                        BorrowedBook.book_id == borrow_data["book_id"],
                        BorrowedBook.returned.is_(False),
                    )
                    .first()
                )
                if existing_borrow:
                    return {
                        "success": False,
                        "message": f"Patron already has '{book.title}' borrowed",
                    }

                # parse dates
                borrow_date = datetime.strptime(
                    borrow_data["borrow_date"], "%Y-%m-%d"
                ).date()
                due_date = datetime.strptime(borrow_data["due_date"], "%Y-%m-%d").date()

                # validate dates
                validation = self._validate_borrowing_dates(borrow_date, due_date)
                if not validation["success"]:
                    return validation

                # create record
                borrow_record = BorrowedBook(
                    user_id=borrow_data["user_id"],
                    book_id=borrow_data["book_id"],
                    borrow_date=borrow_date,
                    due_date=due_date,
                    returned=False,
                )
                book.is_available = False

                session.add(borrow_record)
                session.commit()

                return {
                    "success": True,
                    "message": f"Book '{book.title}' borrowed successfully by {patron.first_name} {patron.last_name}",
                    "borrow_id": borrow_record.borrow_id,
                    "due_date": due_date.strftime("%Y-%m-%d"),
                }

            except IntegrityError as e:
                session.rollback()
                return {
                    "success": False,
                    "message": f"Database constraint violation: {str(e)}",
                }
            except ValueError as e:
                session.rollback()
                return {"success": False, "message": f"Invalid data format: {str(e)}"}
            except Exception as e:
                session.rollback()
                return {
                    "success": False,
                    "message": f"Error creating borrow record: {str(e)}",
                }

    def _check_borrowing_limits(self, patron: Patron) -> Dict:
        """Check if patron has reached borrowing limits"""
        try:
            # Define borrowing limits based on patron grade level
            borrowing_limits = {"pupil": 3, "student": 5, "adult": 7}

            grade_level = (
                patron.grade_level.value
                if hasattr(patron.grade_level, "value")
                else str(patron.grade_level).lower()
            )
            limit = borrowing_limits.get(grade_level, 3)

            # Count current active borrows
            current_borrows = (
                self.db_manager.query(BorrowedBook)
                .filter(
                    BorrowedBook.user_id == patron.user_id,
                    BorrowedBook.returned.is_(False),
                )
                .count()
            )

            if current_borrows >= limit:
                return {
                    "success": False,
                    "message": f"Patron has reached borrowing limit of {limit} books. "
                    f"Currently borrowed: {current_borrows} books. "
                    f"Please return some books before borrowing new ones.",
                }

            return {"success": True, "current_borrows": current_borrows, "limit": limit}

        except Exception as e:
            # If we can't check limits, allow borrowing but log the error
            print(f"Error checking borrowing limits: {e}")
            return {"success": True}

    def _validate_borrowing_dates(self, borrow_date: date, due_date: date) -> Dict:
        """Validate borrowing and due dates"""
        today = datetime.now().date()

        # Borrow date shouldn't be in the future
        if borrow_date > today:
            return {"success": False, "message": "Borrow date cannot be in the future"}

        # Due date must be after borrow date
        if due_date <= borrow_date:
            return {"success": False, "message": "Due date must be after borrow date"}

        # Check reasonable borrowing period (not more than 30 days)
        borrowing_days = (due_date - borrow_date).days
        if borrowing_days > 30:
            return {
                "success": False,
                "message": f"Borrowing period of {borrowing_days} days exceeds maximum limit of 30 days",
            }

        # Warn if borrowing period is very short
        if borrowing_days < 1:
            return {
                "success": False,
                "message": "Borrowing period must be at least 1 day",
            }

        return {"success": True}

    def return_book(self, borrow_id: int, return_date: date = None) -> Dict:
        """Return a borrowed book"""
        try:
            borrow_record = (
                self.db_manager.query(BorrowedBook)
                .filter(BorrowedBook.borrow_id == borrow_id)
                .first()
            )

            if not borrow_record:
                return {"success": False, "message": "Borrow record not found"}

            if borrow_record.returned:
                return {"success": False, "message": "Book has already been returned"}

            # Set return date
            if return_date is None:
                return_date = datetime.now().date()

            borrow_record.returned = True
            borrow_record.return_date = return_date

            # Calculate fine if overdue
            if return_date > borrow_record.due_date:
                days_overdue = (return_date - borrow_record.due_date).days
                fine_amount = days_overdue * 5.0  # 5 KSh per day
                borrow_record.fine_amount = fine_amount

            # Mark book as available
            book = (
                self.db_manager.query(Book)
                .filter(Book.book_id == borrow_record.book_id)
                .first()
            )
            if book:
                book.is_available = True

            self.db_manager.commit()

            message = "Book returned successfully"
            if borrow_record.fine_amount > 0:
                message += f" (Fine: KSh {borrow_record.fine_amount:.2f})"

            return {
                "success": True,
                "message": message,
                "fine_amount": borrow_record.fine_amount,
            }

        except Exception as e:
            self.db_manager.rollback()
            return {"success": False, "message": f"Error returning book: {str(e)}"}

    def get_active_borrows_count(self, user_id: int) -> int:
        """Get count of active borrowed books for a patron"""
        try:
            return (
                self.db_manager.query(BorrowedBook)
                .filter(
                    BorrowedBook.user_id == user_id, BorrowedBook.returned.is_(False)
                )
                .count()
            )
        except Exception:
            return 0

    def get_overdue_books(self, user_id: int = None) -> List[BorrowedBook]:
        """Get overdue books, optionally filtered by patron"""
        try:
            query = self.db_manager.query(BorrowedBook).filter(
                BorrowedBook.returned.is_(False),
                BorrowedBook.due_date < datetime.now().date(),
            )

            if user_id:
                query = query.filter(BorrowedBook.user_id == user_id)

            return query.all()
        except Exception:
            return []

    def get_patron_borrowing_history(self, user_id: int) -> Dict:
        """Get complete borrowing history for a patron"""
        try:
            patron = (
                self.db_manager.query(Patron).filter(Patron.user_id == user_id).first()
            )
            if not patron:
                return {"success": False, "message": "Patron not found"}

            # Get all borrows
            all_borrows = (
                self.db_manager.query(BorrowedBook)
                .filter(BorrowedBook.user_id == user_id)
                .order_by(BorrowedBook.borrow_date.desc())
                .all()
            )

            # Get active borrows
            active_borrows = [b for b in all_borrows if not b.returned]

            # Get overdue books
            overdue_books = [
                b for b in active_borrows if b.due_date < datetime.now().date()
            ]

            # Calculate total fines
            total_fines = sum(b.fine_amount for b in all_borrows if b.fine_amount > 0)

            return {
                "success": True,
                "patron": patron,
                "total_books_borrowed": len(all_borrows),
                "currently_borrowed": len(active_borrows),
                "overdue_books": len(overdue_books),
                "total_fines": total_fines,
                "borrowing_history": all_borrows,
                "active_borrows": active_borrows,
            }

        except Exception as e:
            return {"success": False, "message": f"Error getting history: {str(e)}"}

    def extend_due_date(self, borrow_id: int, new_due_date: date) -> Dict:
        """Extend the due date for a borrowed book"""
        try:
            borrow_record = (
                self.db_manager.query(BorrowedBook)
                .filter(BorrowedBook.borrow_id == borrow_id)
                .first()
            )

            if not borrow_record:
                return {"success": False, "message": "Borrow record not found"}

            if borrow_record.returned:
                return {
                    "success": False,
                    "message": "Cannot extend due date for returned book",
                }

            # Validate new due date
            if new_due_date <= datetime.now().date():
                return {
                    "success": False,
                    "message": "New due date must be in the future",
                }

            if new_due_date <= borrow_record.due_date:
                return {
                    "success": False,
                    "message": "New due date must be later than current due date",
                }

            # Check if extension is reasonable (max 30 days from original borrow)
            max_period = borrow_record.borrow_date + timedelta(days=30)
            if new_due_date > max_period:
                return {
                    "success": False,
                    "message": f"Due date cannot be extended beyond {max_period.strftime('%Y-%m-%d')}",
                }

            old_due_date = borrow_record.due_date
            borrow_record.due_date = new_due_date

            self.db_manager.commit()

            return {
                "success": True,
                "message": f"Due date extended from {old_due_date} to {new_due_date}",
                "old_due_date": old_due_date.strftime("%Y-%m-%d"),
                "new_due_date": new_due_date.strftime("%Y-%m-%d"),
            }

        except Exception as e:
            self.db_manager.rollback()
            return {"success": False, "message": f"Error extending due date: {str(e)}"}

    def get_books_due_soon(self, days_ahead: int = 3) -> List[BorrowedBook]:
        """Get books that are due within specified days"""
        try:
            due_date_threshold = datetime.now().date() + timedelta(days=days_ahead)

            return (
                self.db_manager.query(BorrowedBook)
                .filter(
                    BorrowedBook.returned.is_(False),
                    BorrowedBook.due_date <= due_date_threshold,
                    BorrowedBook.due_date >= datetime.now().date(),
                )
                .all()
            )

        except Exception:
            return []

    def get_borrowing_statistics(self) -> Dict:
        """Get overall borrowing statistics"""
        try:
            total_active = (
                self.db_manager.query(BorrowedBook)
                .filter(BorrowedBook.returned.is_(False))
                .count()
            )

            total_overdue = (
                self.db_manager.query(BorrowedBook)
                .filter(
                    BorrowedBook.returned.is_(False),
                    BorrowedBook.due_date < datetime.now().date(),
                )
                .count()
            )

            total_returned = (
                self.db_manager.query(BorrowedBook)
                .filter(BorrowedBook.returned.is_(True))
                .count()
            )

            # Most borrowed books
            from sqlalchemy import func

            popular_books = (
                self.db_manager.query(
                    Book.title,
                    Book.author,
                    func.count(BorrowedBook.book_id).label("borrow_count"),
                )
                .join(BorrowedBook)
                .group_by(Book.book_id, Book.title, Book.author)
                .order_by(func.count(BorrowedBook.book_id).desc())
                .limit(5)
                .all()
            )

            return {
                "success": True,
                "total_active_borrows": total_active,
                "total_overdue": total_overdue,
                "total_returned": total_returned,
                "popular_books": [
                    {
                        "title": book.title,
                        "author": book.author,
                        "count": book.borrow_count,
                    }
                    for book in popular_books
                ],
            }

        except Exception as e:
            return {"success": False, "message": f"Error getting statistics: {str(e)}"}

    def validate_patron_can_borrow(self, user_id: int) -> Dict:
        """Comprehensive validation if patron can borrow books"""
        try:
            patron = (
                self.db_manager.query(Patron).filter(Patron.user_id == user_id).first()
            )
            if not patron:
                return {"success": False, "message": "Patron not found"}

            # Check if patron has overdue books
            overdue_books = self.get_overdue_books(user_id)
            if overdue_books:
                overdue_titles = [
                    f"• {book.book.title} (Due: {book.due_date})"
                    for book in overdue_books[:3]  # Show max 3
                ]
                message = f"Patron has {len(overdue_books)} overdue book(s):\n"
                message += "\n".join(overdue_titles)
                if len(overdue_books) > 3:
                    message += f"\n... and {len(overdue_books) - 3} more"
                message += "\n\nPlease return overdue books before borrowing new ones."

                return {"success": False, "message": message}

            # Check borrowing limits
            return self._check_borrowing_limits(patron)

        except Exception as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}

    def _check_borrowing_limits_(self, patron: Patron) -> Dict:
        """Internal method to check borrowing limits"""
        try:
            # Define limits based on grade level
            limits = {"pupil": 3, "student": 5, "adult": 7}

            grade_level = (
                patron.grade_level.value
                if hasattr(patron.grade_level, "value")
                else str(patron.grade_level).lower()
            )
            limit = limits.get(grade_level, 3)

            current_count = self.get_active_borrows_count(patron.user_id)

            if current_count >= limit:
                return {
                    "success": False,
                    "message": f"Borrowing limit reached. "
                    f"Current: {current_count}/{limit} books. "
                    f"Please return some books before borrowing new ones.",
                }

            return {
                "success": True,
                "current_borrows": current_count,
                "limit": limit,
                "remaining": limit - current_count,
            }

        except Exception as e:
            return {"success": False, "message": f"Error checking limits: {str(e)}"}

    def _validate_borrowing_dates_(self, borrow_date: date, due_date: date) -> Dict:
        """Validate borrowing and due dates"""
        today = datetime.now().date()

        # Borrow date validation
        if borrow_date > today:
            return {"success": False, "message": "Borrow date cannot be in the future"}

        # Check if borrow date is too far in the past (more than 7 days)
        if (today - borrow_date).days > 7:
            return {
                "success": False,
                "message": "Borrow date cannot be more than 7 days in the past",
            }

        # Due date validation
        if due_date <= borrow_date:
            return {"success": False, "message": "Due date must be after borrow date"}

        # Check borrowing period
        borrowing_days = (due_date - borrow_date).days
        if borrowing_days > 30:
            return {
                "success": False,
                "message": f"Borrowing period of {borrowing_days} days exceeds maximum of 30 days",
            }

        if borrowing_days < 1:
            return {
                "success": False,
                "message": "Borrowing period must be at least 1 day",
            }

        return {"success": True}

    def get_all_active_borrows(self) -> List[BorrowedBook]:
        """Get all active borrowed books"""
        try:
            return (
                self.db_manager.query(BorrowedBook)
                .filter(BorrowedBook.returned.is_(False))
                .order_by(BorrowedBook.borrow_date.desc())
                .all()
            )
        except Exception:
            return []

    def search_borrowed_books(
        self, search_term: str, include_returned: bool = False
    ) -> List[BorrowedBook]:
        """Search borrowed books by patron name, book title, or accession number"""
        try:
            query = self.db_manager.query(BorrowedBook).join(Patron).join(Book)

            if not include_returned:
                query = query.filter(BorrowedBook.returned.is_(False))

            # Search in multiple fields
            search_filter = (
                Patron.first_name.ilike(f"%{search_term}%")
                | Patron.last_name.ilike(f"%{search_term}%")
                | Book.title.ilike(f"%{search_term}%")
                | Book.author.ilike(f"%{search_term}%")
                | Book.accession_no.ilike(f"%{search_term}%")
            )

            return (
                query.filter(search_filter)
                .order_by(BorrowedBook.borrow_date.desc())
                .all()
            )

        except Exception as e:
            print(f"Error searching borrowed books: {e}")
            return []

    def get_borrowing_report(self, start_date: date, end_date: date) -> Dict:
        """Generate borrowing report for a date range"""
        try:
            borrows_in_period = (
                self.db_manager.query(BorrowedBook)
                .filter(
                    BorrowedBook.borrow_date >= start_date,
                    BorrowedBook.borrow_date <= end_date,
                )
                .all()
            )

            returns_in_period = (
                self.db_manager.query(BorrowedBook)
                .filter(
                    BorrowedBook.return_date >= start_date,
                    BorrowedBook.return_date <= end_date,
                    BorrowedBook.returned.is_(True),
                )
                .all()
            )

            total_fines = sum(
                b.fine_amount for b in returns_in_period if b.fine_amount > 0
            )

            return {
                "success": True,
                "period": f"{start_date} to {end_date}",
                "books_borrowed": len(borrows_in_period),
                "books_returned": len(returns_in_period),
                "total_fines_collected": total_fines,
                "average_borrowing_period": self._calculate_average_period(
                    returns_in_period
                ),
            }

        except Exception as e:
            return {"success": False, "message": f"Error generating report: {str(e)}"}

    def _calculate_average_period(self, returned_books: List[BorrowedBook]) -> float:
        """Calculate average borrowing period from returned books"""
        if not returned_books:
            return 0.0

        total_days = sum(
            (book.return_date - book.borrow_date).days
            for book in returned_books
            if book.return_date
        )

        return total_days / len(returned_books) if returned_books else 0.0
