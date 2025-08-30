# controllers/books_controller.py
from sqlalchemy.exc import IntegrityError
from db.models import Book, BorrowedBook


class BooksController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self):
        """Get all books"""
        with self.db_manager.get_session() as session:
            return session.query(Book).all()

    def get_book_by_id(self, book_id):
        """Get book by book ID"""
        with self.db_manager.get_session() as session:
            return session.query(Book).filter(Book.book_id == book_id).first()

    def get_book_by_accession_no(self, accession_no):
        """Get book by accession number"""
        with self.db_manager.get_session() as session:
            return session.query(Book).filter(Book.accession_no == accession_no).first()

    def search_books(self, search_term):
        """Search books by title, author, class name, or accession number"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Book)
                .filter(
                    (Book.title.contains(search_term))
                    | (Book.author.contains(search_term))
                    | (Book.class_name.contains(search_term))
                    | (Book.accession_no.contains(search_term))
                )
                .all()
            )

    def get_books_by_author(self, author):
        """Get all books by a specific author"""
        with self.db_manager.get_session() as session:
            return session.query(Book).filter(Book.author == author).all()

    def get_books_by_class(self, class_name):
        """Get all books for a specific class"""
        with self.db_manager.get_session() as session:
            return session.query(Book).filter(Book.class_name == class_name).all()

    def get_available_books(self):
        """Get all books that are currently available (not borrowed)"""
        with self.db_manager.get_session() as session:
            borrowed_book_ids = (
                session.query(BorrowedBook.book_id)
                .filter(BorrowedBook.returned.is_(False))
                .subquery()
            )

            return (
                session.query(Book).filter(~Book.book_id.in_(borrowed_book_ids)).all()
            )

    def get_borrowed_books(self):
        """Get all books that are currently borrowed"""
        with self.db_manager.get_session() as session:
            borrowed_book_ids = (
                session.query(BorrowedBook.book_id)
                .filter(BorrowedBook.returned.is_(False))
                .subquery()
            )

            return session.query(Book).filter(Book.book_id.in_(borrowed_book_ids)).all()

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

                # Check if book is currently borrowed
                active_borrow = (
                    session.query(BorrowedBook)
                    .filter(
                        BorrowedBook.book_id == book_id,
                        BorrowedBook.returned.is_(False),
                    )
                    .first()
                )

                if active_borrow:
                    return {
                        "success": False,
                        "message": "Cannot delete book that is currently borrowed",
                    }

                session.delete(book)
                session.commit()
                return {"success": True, "message": "Book deleted successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error deleting book: {str(e)}"}

    def get_book_borrow_history(self, book_id):
        """Get borrow history for a specific book"""
        with self.db_manager.get_session() as session:
            return (
                session.query(BorrowedBook)
                .filter(BorrowedBook.book_id == book_id)
                .all()
            )

    def get_books_statistics(
        self,
    ):
        """Get book statistics"""
        with self.db_manager.get_session() as session:
            total_books = session.query(Book).count()

            borrowed_count = (
                session.query(BorrowedBook)
                .filter(BorrowedBook.returned.is_(False))
                .count()
            )

            available_count = total_books - borrowed_count

            return {
                "total": total_books,
                "borrowed": borrowed_count,
                "available": available_count,
            }
