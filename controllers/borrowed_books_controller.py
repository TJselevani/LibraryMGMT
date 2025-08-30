# controllers/borrowed_books_controller.py
from datetime import datetime, date, timedelta
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from db.models import BorrowedBook, Book, Patron


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

    def get_active_borrowed_books(self):
        """Get all currently borrowed books (not returned)"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BorrowedBook)
                .options(joinedload(BorrowedBook.book), joinedload(BorrowedBook.patron))
                .filter(BorrowedBook.returned.is_(False))
                .all()
            )

    def get_overdue_books(self):
        """Get all overdue books"""
        with self.db_manager.get_session() as session:
            today = date.today()
            return (
                session.query(BorrowedBook)
                .options(joinedload(BorrowedBook.book), joinedload(BorrowedBook.patron))
                .filter(
                    BorrowedBook.returned.is_(False), BorrowedBook.return_date < today
                )
                .all()
            )

    def get_borrowed_books_by_patron(self, user_id):
        """Get all books borrowed by a specific patron"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BorrowedBook)
                .options(joinedload(BorrowedBook.book))
                .filter(BorrowedBook.user_id == user_id)
                .all()
            )

    def get_active_borrowed_books_by_patron(self, user_id):
        """Get currently borrowed books by a specific patron"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BorrowedBook)
                .options(joinedload(BorrowedBook.book))
                .filter(
                    BorrowedBook.user_id == user_id, BorrowedBook.returned.is_(False)
                )
                .all()
            )

    def get_book_borrow_history(self, book_id):
        """Get borrow history for a specific book"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BorrowedBook)
                .options(joinedload(BorrowedBook.patron))
                .filter(BorrowedBook.book_id == book_id)
                .order_by(BorrowedBook.borrow_date.desc())
                .all()
            )

    def borrow_book(self, user_id, book_id, return_date=None, borrow_date=None):
        """Create a new book borrowing record"""
        try:
            with self.db_manager.get_session() as session:
                # Check if patron exists
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()
                if not patron:
                    return {"success": False, "message": "Patron not found"}

                # Check if book exists
                book = session.query(Book).filter(Book.book_id == book_id).first()
                if not book:
                    return {"success": False, "message": "Book not found"}

                # Check if book is already borrowed
                existing_borrow = (
                    session.query(BorrowedBook)
                    .filter(
                        BorrowedBook.book_id == book_id,
                        BorrowedBook.returned.is_(False),
                    )
                    .first()
                )

                if existing_borrow:
                    return {"success": False, "message": "Book is already borrowed"}

                # Check patron's membership status
                if patron.membership_status != "active":
                    return {
                        "success": False,
                        "message": "Patron membership is not active",
                    }

                # Set default dates if not provided
                if not borrow_date:
                    borrow_date = date.today()
                elif isinstance(borrow_date, str):
                    borrow_date = datetime.strptime(borrow_date, "%Y-%m-%d").date()

                if not return_date:
                    return_date = borrow_date + timedelta(days=14)  # Default 2 weeks
                elif isinstance(return_date, str):
                    return_date = datetime.strptime(return_date, "%Y-%m-%d").date()

                # Create borrow record
                borrowed_book = BorrowedBook(
                    user_id=user_id,
                    book_id=book_id,
                    borrow_date=borrow_date,
                    return_date=return_date,
                    returned=False,
                )

                session.add(borrowed_book)
                session.commit()
                session.refresh(borrowed_book)

                return {
                    "success": True,
                    "borrowed_book": borrowed_book,
                    "message": f"Book '{book.title}' borrowed successfully",
                }

        except Exception as e:
            return {"success": False, "message": f"Error borrowing book: {str(e)}"}

    def return_book(self, borrow_id, actual_return_date=None):
        """Mark a book as returned"""
        try:
            with self.db_manager.get_session() as session:
                borrowed_book = (
                    session.query(BorrowedBook)
                    .filter(BorrowedBook.borrow_id == borrow_id)
                    .first()
                )

                if not borrowed_book:
                    return {"success": False, "message": "Borrow record not found"}

                if borrowed_book.returned:
                    return {
                        "success": False,
                        "message": "Book has already been returned",
                    }

                # Mark as returned
                borrowed_book.returned = True

                # You might want to add an actual_return_date field to track when book was actually returned
                # For now, we'll just mark it as returned

                session.commit()
                session.refresh(borrowed_book)

                return {
                    "success": True,
                    "borrowed_book": borrowed_book,
                    "message": "Book returned successfully",
                }

        except Exception as e:
            return {"success": False, "message": f"Error returning book: {str(e)}"}

    def extend_return_date(self, borrow_id, new_return_date):
        """Extend the return date for a borrowed book"""
        try:
            with self.db_manager.get_session() as session:
                borrowed_book = (
                    session.query(BorrowedBook)
                    .filter(BorrowedBook.borrow_id == borrow_id)
                    .first()
                )

                if not borrowed_book:
                    return {"success": False, "message": "Borrow record not found"}

                if borrowed_book.returned:
                    return {
                        "success": False,
                        "message": "Cannot extend return date for already returned book",
                    }

                # Convert string to date if needed
                if isinstance(new_return_date, str):
                    new_return_date = datetime.strptime(
                        new_return_date, "%Y-%m-%d"
                    ).date()

                borrowed_book.return_date = new_return_date
                session.commit()
                session.refresh(borrowed_book)

                return {
                    "success": True,
                    "borrowed_book": borrowed_book,
                    "message": f"Return date extended to {new_return_date}",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error extending return date: {str(e)}",
            }

    def create_book(self, book_data):
        """Create a new book"""
        try:
            with self.db_manager.get_session() as session:
                # Validate required fields
                required_fields = ["title", "author", "accession_no"]
                for field in required_fields:
                    if field not in book_data or not book_data[field]:
                        return {"success": False, "message": f"{field} is required"}

                new_book = Book(**book_data)
                session.add(new_book)
                session.commit()
                session.refresh(new_book)
                return {
                    "success": True,
                    "book": new_book,
                    "message": "Book created successfully",
                }

        except IntegrityError:
            return {
                "success": False,
                "message": "Book with this accession number already exists",
            }
        except Exception as e:
            return {"success": False, "message": f"Error creating book: {str(e)}"}

    def update_book(self, book_id, update_data):
        """Update book information"""
        try:
            with self.db_manager.get_session() as session:
                book = session.query(Book).filter(Book.book_id == book_id).first()

                if not book:
                    return {"success": False, "message": "Book not found"}

                # Update book attributes
                for key, value in update_data.items():
                    if hasattr(book, key):
                        setattr(book, key, value)

                session.commit()
                session.refresh(book)
                return {
                    "success": True,
                    "book": book,
                    "message": "Book updated successfully",
                }

        except IntegrityError:
            return {
                "success": False,
                "message": "Update failed: Accession number already exists",
            }
        except Exception as e:
            return {"success": False, "message": f"Error updating book: {str(e)}"}

    def delete_book(self, book_id):
        """Delete book by book ID"""
        try:
            with self.db_manager.get_session() as session:
                book = session.query(Book).filter(Book.book_id == book_id).first()

                if not book:
                    return {"success": False, "message": "Book not found"}

                # Check if book has any borrow records
                borrow_records = (
                    session.query(BorrowedBook)
                    .filter(BorrowedBook.book_id == book_id)
                    .count()
                )

                if borrow_records > 0:
                    return {
                        "success": False,
                        "message": "Cannot delete book with existing borrow records",
                    }

                session.delete(book)
                session.commit()
                return {"success": True, "message": "Book deleted successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error deleting book: {str(e)}"}

    def get_borrowing_statistics(
        self,
    ):
        """Get borrowing statistics"""
        with self.db_manager.get_session() as session:
            total_borrows = session.query(BorrowedBook).count()
            active_borrows = (
                session.query(BorrowedBook)
                .filter(BorrowedBook.returned.is_(False))
                .count()
            )

            # Count overdue books
            today = date.today()
            overdue_count = (
                session.query(BorrowedBook)
                .filter(
                    BorrowedBook.returned.is_(False), BorrowedBook.return_date < today
                )
                .count()
            )

            returned_books = (
                session.query(BorrowedBook)
                .filter(BorrowedBook.returned.is_(True))
                .count()
            )

            return {
                "total_borrows": total_borrows,
                "active_borrows": active_borrows,
                "overdue": overdue_count,
                "returned": returned_books,
            }
