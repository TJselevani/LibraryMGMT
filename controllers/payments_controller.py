# controllers/payments_controller.py
from datetime import datetime, date, timedelta
from sqlalchemy.orm import joinedload
from db.models import Payment, Patron, Installment, PaymentType, PaymentService
from typing import Dict, List, Optional
from sqlalchemy.exc import IntegrityError


class PaymentController:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.db = db_manager

    # ---------- GET METHODS ----------

    def get_all(self):
        """Get all payments with patron + installments eagerly loaded"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.installments),
                )
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_one(self, payment_id):
        """Get a single payment by ID"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.installments),
                )
                .filter(Payment.payment_id == payment_id)
                .first()
            )

    def get_by_id(self, payment_id):
        """Alias for get_one (for naming consistency)"""
        return self.get_one(payment_id)

    def get_by_patron(self, user_id):
        """Get all payments made by a specific patron"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.installments),
                )
                .filter(Payment.user_id == user_id)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_by_type(self, payment_type):
        """Get all payments of a specific type"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.installments),
                )
                .filter(Payment.payment_type == payment_type)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_by_date_range(self, start_date, end_date):
        """Get payments within a date range"""
        with self.db_manager.get_session() as session:
            # Convert strings to date objects if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.installments),
                )
                .filter(
                    Payment.payment_date >= start_date,
                    Payment.payment_date <= end_date,
                )
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_recent(self, days=30):
        """Get payments from the last N days"""
        with self.db_manager.get_session() as session:
            cutoff_date = date.today() - timedelta(days=days)
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.installments),
                )
                .filter(Payment.payment_date >= cutoff_date)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    # ---------- CREATE ----------
    def create(self, payment_data: Dict) -> Dict:
        """
        Create a new payment with proper validation and tight coupling
        """
        with self.db_manager.get_session() as session:  # ✅ real SQLAlchemy session
            try:
                # 1. Validate patron exists
                patron = (
                    session.query(Patron)
                    .filter(Patron.user_id == payment_data.get("user_id"))
                    .first()
                )
                if not patron:
                    return {
                        "success": False,
                        "message": f"Patron {payment_data.get('user_id')} not found",
                    }

                # 2. Validate payment data
                validation_errors = PaymentService.validate_payment_data(
                    payment_data, patron
                )
                if validation_errors:
                    return {
                        "success": False,
                        "message": "Validation errors: " + "; ".join(validation_errors),
                    }

                # 3. Create payment record
                payment = Payment(
                    user_id=payment_data["user_id"],
                    payment_type=PaymentType(payment_data["payment_type"]),
                    amount=float(payment_data["amount"]),
                    payment_date=datetime.strptime(
                        payment_data["payment_date"], "%Y-%m-%d"
                    ).date(),
                )
                payment.validate_payment_amount()

                session.add(payment)
                session.flush()  # get ID

                # 4. Create installments
                if (
                    payment_data.get("installments")
                    and payment.payment_type == PaymentType.MEMBERSHIP
                ):
                    installments_created = self._create_installments(
                        payment.payment_id, payment_data["installments"], session
                    )
                    if not installments_created["success"]:
                        session.rollback()
                        return installments_created

                # 5. Update patron membership
                if payment.payment_type == PaymentType.MEMBERSHIP:
                    patron.membership_status = "active"

                session.commit()

                return {
                    "success": True,
                    "message": f"Payment of KSh {payment.amount:.2f} created successfully",
                    "payment_id": payment.payment_id,
                }

            except IntegrityError as e:
                session.rollback()
                return {
                    "success": False,
                    "message": f"Database integrity error: {str(e)}",
                }
            except ValueError as e:
                session.rollback()
                return {"success": False, "message": f"Validation error: {str(e)}"}
            except Exception as e:
                session.rollback()
                return {"success": False, "message": f"Unexpected error: {str(e)}"}

    def _create_installments(
        self, payment_id: int, installments_data: List[Dict]
    ) -> Dict:
        """Create installment records for a payment"""
        try:
            total_installments = 0

            for i, installment_data in enumerate(installments_data, 1):
                installment = Installment(
                    payment_id=payment_id,
                    installment_number=installment_data.get("installment_number", i),
                    amount=float(installment_data["amount"]),
                    due_date=datetime.strptime(
                        installment_data["date"], "%Y-%m-%d"
                    ).date(),
                )

                total_installments += installment.amount
                self.db.add(installment)

            return {"success": True}

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create installments: {str(e)}",
            }

    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        return self.db.query(Payment).filter(Payment.payment_id == payment_id).first()

    def get_payments_by_patron(self, user_id: int) -> List[Payment]:
        """Get all payments for a specific patron"""
        return self.db.query(Payment).filter(Payment.user_id == user_id).all()

    def get_outstanding_installments(self, user_id: int) -> List[Installment]:
        """Get unpaid installments for a patron"""
        return (
            self.db.query(Installment)
            .join(Payment)
            .filter(Payment.user_id == user_id, Installment.is_paid.is_(False))
            .all()
        )

    def mark_installment_paid(self, installment_id: int) -> Dict:
        """Mark an installment as paid"""
        try:
            installment = (
                self.db.query(Installment)
                .filter(Installment.installment_id == installment_id)
                .first()
            )

            if not installment:
                return {"success": False, "message": "Installment not found"}

            installment.is_paid = True
            installment.paid_date = date.today()

            self.db.commit()
            return {"success": True, "message": "Installment marked as paid"}

        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "message": f"Error updating installment: {str(e)}",
            }

    def get_payment_summary(self, user_id: int) -> Dict:
        """Get payment summary for a patron"""
        try:
            patron = self.db.query(Patron).filter(Patron.user_id == user_id).first()
            if not patron:
                return {"success": False, "message": "Patron not found"}

            payments = self.get_payments_by_patron(user_id)
            outstanding_installments = self.get_outstanding_installments(user_id)

            total_paid = sum(p.amount for p in payments)
            total_outstanding = sum(i.amount for i in outstanding_installments)

            return {
                "success": True,
                "patron": patron,
                "total_paid": total_paid,
                "total_outstanding": total_outstanding,
                "payment_count": len(payments),
                "outstanding_installments": len(outstanding_installments),
            }

        except Exception as e:
            return {"success": False, "message": f"Error getting summary: {str(e)}"}

    def validate_patron_can_pay(self, user_id: int, payment_type: str) -> Dict:
        """Validate if patron can make a specific payment"""
        try:
            patron = self.db.query(Patron).filter(Patron.user_id == user_id).first()
            if not patron:
                return {"success": False, "message": "Patron not found"}

            payment_type_enum = PaymentType(payment_type)

            # Check if patron already has active membership
            if payment_type_enum == PaymentType.MEMBERSHIP:
                existing_membership = (
                    self.db.query(Payment)
                    .filter(
                        Payment.user_id == user_id,
                        Payment.payment_type == PaymentType.MEMBERSHIP,
                    )
                    .first()
                )

                if existing_membership and patron.membership_status == "active":
                    return {
                        "success": False,
                        "message": "Patron already has an active membership",
                    }

            return {"success": True, "patron": patron}

        except ValueError:
            return {
                "success": False,
                "message": f"Invalid payment type: {payment_type}",
            }
        except Exception as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}

    # ---------- UPDATE ----------

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

    # ---------- DELETE ----------

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
