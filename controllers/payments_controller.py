# controllers/payments_controller.py
from datetime import datetime, date, timedelta

# from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

# from sqlalchemy import func, extract
from db.models import Payment, Patron


class PaymentController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self):
        """Get all payments with patron details"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(joinedload(Payment.patron))
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_payment_by_id(self, payment_id):
        """Get payment by payment ID"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(joinedload(Payment.patron))
                .filter(Payment.payment_id == payment_id)
                .first()
            )

    def get_payments_by_patron(self, user_id):
        """Get all payments made by a specific patron"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .filter(Payment.user_id == user_id)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_payments_by_type(self, payment_type):
        """Get all payments of a specific type"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(joinedload(Payment.patron))
                .filter(Payment.payment_type == payment_type)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_payments_by_date_range(self, start_date, end_date):
        """Get payments within a date range"""
        with self.db_manager.get_session() as session:
            # Convert strings to date objects if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            return (
                session.query(Payment)
                .options(joinedload(Payment.patron))
                .filter(
                    Payment.payment_date >= start_date, Payment.payment_date <= end_date
                )
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_recent_payments(self, days=30):
        """Get payments from the last N days"""
        with self.db_manager.get_session() as session:
            cutoff_date = date.today() - timedelta(days=days)
            return (
                session.query(Payment)
                .options(joinedload(Payment.patron))
                .filter(Payment.payment_date >= cutoff_date)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def create_payment(self, payment_data):
        """Create a new payment record"""
        try:
            with self.db_manager.get_session() as session:
                # Validate required fields
                required_fields = ["user_id", "payment_type", "amount"]
                for field in required_fields:
                    if field not in payment_data or payment_data[field] is None:
                        return {"success": False, "message": f"{field} is required"}

                # Check if patron exists
                patron = (
                    session.query(Patron)
                    .filter(Patron.user_id == payment_data["user_id"])
                    .first()
                )
                if not patron:
                    return {"success": False, "message": "Patron not found"}

                # Set payment date if not provided
                if "payment_date" not in payment_data:
                    payment_data["payment_date"] = date.today()
                elif isinstance(payment_data["payment_date"], str):
                    payment_data["payment_date"] = datetime.strptime(
                        payment_data["payment_date"], "%Y-%m-%d"
                    ).date()

                # Validate amount
                if payment_data["amount"] <= 0:
                    return {
                        "success": False,
                        "message": "Payment amount must be greater than 0",
                    }

                new_payment = Payment(**payment_data)
                session.add(new_payment)
                session.commit()
                session.refresh(new_payment)

                return {
                    "success": True,
                    "payment": new_payment,
                    "message": "Payment recorded successfully",
                }

        except Exception as e:
            return {"success": False, "message": f"Error creating payment: {str(e)}"}

    def update_payment(self, payment_id, update_data):
        """Update payment information"""
        try:
            with self.db_manager.get_session() as session:
                payment = (
                    session.query(Payment)
                    .filter(Payment.payment_id == payment_id)
                    .first()
                )

                if not payment:
                    return {"success": False, "message": "Payment not found"}

                # Convert date string if needed
                if "payment_date" in update_data and isinstance(
                    update_data["payment_date"], str
                ):
                    update_data["payment_date"] = datetime.strptime(
                        update_data["payment_date"], "%Y-%m-%d"
                    ).date()

                # Validate amount if being updated
                if "amount" in update_data and update_data["amount"] <= 0:
                    return {
                        "success": False,
                        "message": "Payment amount must be greater than 0",
                    }

                # Update payment attributes
                for key, value in update_data.items():
                    if hasattr(payment, key):
                        setattr(payment, key, value)

                session.commit()
                session.refresh(payment)
                return {
                    "success": True,
                    "payment": payment,
                    "message": "Payment updated successfully",
                }

        except Exception as e:
            return {"success": False, "message": f"Error updating payment: {str(e)}"}

    def delete_payment(self, payment_id):
        """Delete payment record"""
        try:
            with self.db_manager.get_session() as session:
                payment = (
                    session.query(Payment)
                    .filter(Payment.payment_id == payment_id)
                    .first()
                )

                if not payment:
                    return {"success": False, "message": "Payment not found"}

                session.delete(payment)
                session.commit()
                return {"success": True, "message": "Payment deleted successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error deleting payment: {str(e)}"}
