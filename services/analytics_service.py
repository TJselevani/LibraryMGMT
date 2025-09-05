# services/analytics_service.py
"""
Analytics service for generating data visualizations using Plotly.
Integrates with the existing SQLAlchemy models and repository pattern.
"""

import plotly.graph_objects as go
import pandas as pd
import json
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy import func, and_
from utils.database_manager import MyDatabaseManager
from controllers.books_controller import BooksController
from controllers.borrowed_books_controller import BorrowedBooksController
from controllers.patrons_controller import PatronsController
from controllers.payments_controller import PaymentController


from db.models import BorrowedBook, Book, Patron, Payment


class AnalyticsService:
    """Service for generating analytics and visualizations."""

    def __init__(self, db_manager: MyDatabaseManager):
        self.db_manager = db_manager
        self.book_repo = BooksController(db_manager)
        self.borrowed_book_repo = BorrowedBooksController(db_manager)
        self.patron_repo = PatronsController(db_manager)
        self.payment_repo = PaymentController(db_manager)

    def get_borrowing_trends(self, days: int = 30) -> Dict[str, Any]:
        """Generate borrowing trends over the specified period."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        with self.db_manager.get_session() as session:
            # Get daily borrowing counts
            daily_borrowings = (
                session.query(
                    func.date(BorrowedBook.borrowed_date).label("date"),
                    func.count(BorrowedBook.id).label("count"),
                )
                .filter(BorrowedBook.borrowed_date.between(start_date, end_date))
                .group_by(func.date(BorrowedBook.borrowed_date))
                .all()
            )

        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(daily_borrowings, columns=["date", "count"])
        df["date"] = pd.to_datetime(df["date"])

        # Create the plot
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["date"],
                y=df["count"],
                mode="lines+markers",
                name="Books Borrowed",
                line=dict(color="#2E86AB", width=3),
                marker=dict(size=8, color="#2E86AB"),
            )
        )

        fig.update_layout(
            title=f"Book Borrowing Trends - Last {days} Days",
            xaxis_title="Date",
            yaxis_title="Number of Books Borrowed",
            template="plotly_white",
            hovermode="x unified",
        )

        return {
            "figure": json.loads(fig.to_json()),
            "summary": {
                "total_borrowings": df["count"].sum(),
                "average_daily": df["count"].mean(),
                "peak_day": (
                    df.loc[df["count"].idxmax(), "date"].strftime("%Y-%m-%d")
                    if not df.empty
                    else None
                ),
            },
        }

    def get_popular_books(self, limit: int = 10) -> Dict[str, Any]:
        """Get the most popular books by borrowing frequency."""
        with self.db_manager.get_session() as session:
            popular_books = (
                session.query(
                    Book.title,
                    Book.author,
                    func.count(BorrowedBook.id).label("borrow_count"),
                )
                .join(BorrowedBook, Book.id == BorrowedBook.book_id)
                .group_by(Book.id, Book.title, Book.author)
                .order_by(func.count(BorrowedBook.id).desc())
                .limit(limit)
                .all()
            )

        if not popular_books:
            return {"figure": {}, "summary": {"message": "No borrowing data available"}}

        df = pd.DataFrame(popular_books, columns=["title", "author", "borrow_count"])
        df["display_title"] = df["title"].apply(
            lambda x: x[:30] + "..." if len(x) > 30 else x
        )

        # Create horizontal bar chart
        fig = go.Figure(
            go.Bar(
                x=df["borrow_count"],
                y=df["display_title"],
                orientation="h",
                marker_color="#A23B72",
                text=df["borrow_count"],
                textposition="auto",
            )
        )

        fig.update_layout(
            title=f"Top {limit} Most Popular Books",
            xaxis_title="Number of Times Borrowed",
            yaxis_title="Book Title",
            template="plotly_white",
            height=max(400, len(df) * 40),
        )

        return {
            "figure": json.loads(fig.to_json()),
            "summary": {
                "top_book": df.iloc[0]["title"] if not df.empty else None,
                "top_count": int(df.iloc[0]["borrow_count"]) if not df.empty else 0,
                "total_books": len(df),
            },
        }

    def get_patron_activity(self) -> Dict[str, Any]:
        """Analyze patron activity patterns."""
        with self.db_manager.get_session() as session:
            patron_stats = (
                session.query(
                    Patron.name,
                    func.count(BorrowedBook.id).label("books_borrowed"),
                    func.coalesce(func.sum(Payment.amount), 0).label("total_payments"),
                )
                .outerjoin(BorrowedBook, Patron.id == BorrowedBook.patron_id)
                .outerjoin(Payment, Patron.id == Payment.patron_id)
                .group_by(Patron.id, Patron.name)
                .all()
            )

        if not patron_stats:
            return {"figure": {}, "summary": {"message": "No patron data available"}}

        df = pd.DataFrame(
            patron_stats, columns=["name", "books_borrowed", "total_payments"]
        )

        # Create scatter plot
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=df["books_borrowed"],
                y=df["total_payments"],
                mode="markers",
                text=df["name"],
                marker=dict(
                    size=10,
                    color=df["books_borrowed"],
                    colorscale="Viridis",
                    showscale=True,
                    colorbar=dict(title="Books Borrowed"),
                ),
                hovertemplate="<b>%{text}</b><br>Books Borrowed: %{x}<br>Total Payments: $%{y}<extra></extra>",
            )
        )

        fig.update_layout(
            title="Patron Activity Analysis",
            xaxis_title="Number of Books Borrowed",
            yaxis_title="Total Payments ($)",
            template="plotly_white",
        )

        return {
            "figure": json.loads(fig.to_json()),
            "summary": {
                "total_patrons": len(df),
                "active_patrons": len(df[df["books_borrowed"] > 0]),
                "avg_books_per_patron": df["books_borrowed"].mean(),
                "total_payments": df["total_payments"].sum(),
            },
        }

    def get_overdue_analysis(self) -> Dict[str, Any]:
        """Analyze overdue books and patterns."""
        current_date = datetime.now()

        with self.db_manager.get_session() as session:
            overdue_books = (
                session.query(
                    BorrowedBook, Book.title, Patron.name.label("patron_name")
                )
                .join(Book, BorrowedBook.book_id == Book.id)
                .join(Patron, BorrowedBook.patron_id == Patron.id)
                .filter(
                    and_(
                        BorrowedBook.return_date.is_(None),
                        BorrowedBook.due_date < current_date,
                    )
                )
                .all()
            )

        if not overdue_books:
            return {
                "figure": json.loads(go.Figure().to_json()),
                "summary": {"message": "No overdue books"},
            }

        # Calculate days overdue
        overdue_data = []
        for borrowed_book, title, patron_name in overdue_books:
            days_overdue = (current_date - borrowed_book.due_date).days
            overdue_data.append(
                {
                    "title": title,
                    "patron": patron_name,
                    "days_overdue": days_overdue,
                    "due_date": borrowed_book.due_date,
                }
            )

        df = pd.DataFrame(overdue_data)

        # Create histogram of overdue days
        fig = go.Figure()
        fig.add_trace(
            go.Histogram(
                x=df["days_overdue"], nbinsx=20, marker_color="#F18F01", opacity=0.7
            )
        )

        fig.update_layout(
            title="Distribution of Overdue Days",
            xaxis_title="Days Overdue",
            yaxis_title="Number of Books",
            template="plotly_white",
        )

        return {
            "figure": json.loads(fig.to_json()),
            "summary": {
                "total_overdue": len(df),
                "avg_days_overdue": df["days_overdue"].mean(),
                "max_days_overdue": df["days_overdue"].max(),
                "books_overdue_week": len(df[df["days_overdue"] <= 7]),
                "books_overdue_month": len(df[df["days_overdue"] > 30]),
            },
        }

    def get_financial_overview(self, months: int = 12) -> Dict[str, Any]:
        """Generate financial overview and revenue trends."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)

        with self.db_manager.get_session() as session:
            payments = (
                session.query(
                    Payment.payment_date, Payment.amount, Payment.payment_type
                )
                .filter(Payment.payment_date.between(start_date, end_date))
                .all()
            )

        if not payments:
            return {"figure": {}, "summary": {"message": "No payment data available"}}

        df = pd.DataFrame(payments, columns=["payment_date", "amount", "payment_type"])
        df["payment_date"] = pd.to_datetime(df["payment_date"])
        df["month"] = df["payment_date"].dt.to_period("M")

        # Monthly revenue
        monthly_revenue = df.groupby("month")["amount"].sum().reset_index()
        monthly_revenue["month_str"] = monthly_revenue["month"].astype(str)

        # Create subplot with revenue trend and payment type distribution
        from plotly.subplots import make_subplots

        fig = make_subplots(
            rows=1,
            cols=2,
            subplot_titles=("Monthly Revenue Trend", "Payment Type Distribution"),
            specs=[[{"secondary_y": False}, {"type": "pie"}]],
        )

        # Revenue trend
        fig.add_trace(
            go.Scatter(
                x=monthly_revenue["month_str"],
                y=monthly_revenue["amount"],
                mode="lines+markers",
                name="Revenue",
                line=dict(color="#2E8B57", width=3),
            ),
            row=1,
            col=1,
        )

        # Payment type distribution
        payment_type_dist = df.groupby("payment_type")["amount"].sum()
        fig.add_trace(
            go.Pie(
                labels=payment_type_dist.index,
                values=payment_type_dist.values,
                name="Payment Types",
            ),
            row=1,
            col=2,
        )

        fig.update_layout(
            title=f"Financial Overview - Last {months} Months",
            template="plotly_white",
            height=500,
        )

        return {
            "figure": json.loads(fig.to_json()),
            "summary": {
                "total_revenue": df["amount"].sum(),
                "avg_monthly_revenue": monthly_revenue["amount"].mean(),
                "total_payments": len(df),
                "payment_types": df["payment_type"].nunique(),
            },
        }

    def get_library_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive dashboard data."""
        with self.db_manager.get_session() as session:
            # Key metrics
            total_books = session.query(Book).count()
            total_patrons = session.query(Patron).count()
            active_borrowings = (
                session.query(BorrowedBook)
                .filter(BorrowedBook.return_date.is_(None))
                .count()
            )

            overdue_count = (
                session.query(BorrowedBook)
                .filter(
                    and_(
                        BorrowedBook.return_date.is_(None),
                        BorrowedBook.due_date < datetime.now(),
                    )
                )
                .count()
            )

            total_revenue = session.query(func.sum(Payment.amount)).scalar() or 0

        # Create KPI cards data
        kpis = [
            {"title": "Total Books", "value": total_books, "icon": "📚"},
            {"title": "Total Patrons", "value": total_patrons, "icon": "👥"},
            {"title": "Active Borrowings", "value": active_borrowings, "icon": "📖"},
            {"title": "Overdue Books", "value": overdue_count, "icon": "⚠️"},
            {"title": "Total Revenue", "value": f"${total_revenue:.2f}", "icon": "💰"},
        ]

        return {
            "kpis": kpis,
            "borrowing_trends": self.get_borrowing_trends(30)["figure"],
            "popular_books": self.get_popular_books(5)["figure"],
            "overdue_analysis": self.get_overdue_analysis()["figure"],
        }


# Create factory function for easy instantiation
def create_analytics_service(db_manager: MyDatabaseManager) -> AnalyticsService:
    """Factory function to create AnalyticsService instance."""
    return AnalyticsService(db_manager)
