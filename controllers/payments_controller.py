# Enhanced payments_controller.py - Simplified Partial Payment System
from datetime import datetime, date
from sqlalchemy.orm import joinedload
from db.models import (
    Payment,
    Patron,
    PartialPayment,
    PaymentItem,
    PaymentService,
    PaymentStatus,
)
from typing import Dict


class PaymentController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ---------- GET METHODS ----------

    def get_all(self):
        """Get all payments with patron and payment_item eagerly loaded"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.payment_item),
                    joinedload(Payment.partial_payments),
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
                    joinedload(Payment.payment_item),
                    joinedload(Payment.partial_payments),
                )
                .filter(Payment.payment_id == payment_id)
                .first()
            )

    def get_by_patron(self, user_id):
        """Get all payments made by a specific patron"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.payment_item),
                    joinedload(Payment.partial_payments),
                )
                .filter(Payment.user_id == user_id)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_incomplete_payments(self, user_id=None):
        """Get all incomplete payments, optionally filtered by patron"""
        with self.db_manager.get_session() as session:
            query = (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.payment_item),
                    joinedload(Payment.partial_payments),
                )
                .filter(
                    Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL])
                )
            )

            if user_id:
                query = query.filter(Payment.user_id == user_id)

            return query.order_by(Payment.created_at.desc()).all()

    def get_patron_incomplete_payment(self, user_id, payment_item_name):
        """Get existing incomplete payment for a patron and payment item"""
        with self.db_manager.get_session() as session:
            return PaymentService.get_existing_incomplete_payment(
                session, user_id, payment_item_name
            )

    # ---------- CREATE ----------
    def create(self, payment_data: Dict) -> Dict:
        """Create a new payment or add to existing incomplete payment"""
        with self.db_manager.get_session() as session:
            try:
                # 1. Validate required fields
                required_fields = [
                    "user_id",
                    "payment_item_name",
                    "payment_item_id",
                    "amount",
                    "payment_date",
                ]
                for field in required_fields:
                    if not payment_data.get(field):
                        return {
                            "success": False,
                            "message": f"Missing required field: {field}",
                        }

                # Check if we have either payment_item_id or payment_item_name
                payment_item_id = payment_data.get("payment_item_id")
                payment_item_name = payment_data.get("payment_item_name")

                if not payment_item_id and not payment_item_name:
                    return {
                        "success": False,
                        "message": "Either payment_item_id or payment_item_name is required",
                    }

                # 2. Validate patron exists
                user_id = payment_data.get("user_id")
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()
                if not patron:
                    return {
                        "success": False,
                        "message": f"Patron {user_id} not found",
                    }

                # 3. Enhanced payment item validation
                print(f"DEBUG: Looking for payment item: '{payment_item_name}'")

                # Get payment item (prefer ID over name)
                if payment_item_id:
                    payment_item = (
                        session.query(PaymentItem)
                        .filter(
                            PaymentItem.id == payment_item_id,
                            PaymentItem.is_active.is_(True),
                        )
                        .first()
                    )

                    if not payment_item:
                        return {
                            "success": False,
                            "message": f"Payment item with ID {payment_item_id} not found or inactive",
                        }
                else:
                    # Fallback to name-based lookup
                    payment_item = (
                        session.query(PaymentItem)
                        .filter(
                            PaymentItem.name == payment_item_name,
                            PaymentItem.is_active.is_(True),
                        )
                        .first()
                    )

                    if not payment_item:
                        available_items = (
                            session.query(PaymentItem)
                            .filter(PaymentItem.is_active.is_(True))
                            .all()
                        )
                        available_names = [f"'{item.name}'" for item in available_items]
                        return {
                            "success": False,
                            "message": f"Payment item '{payment_item_name}' not found or inactive. Available: {', '.join(available_names)}",
                        }

                # Check if payment item is active
                if not payment_item.is_active:
                    return {
                        "success": False,
                        "message": f"Payment item '{payment_item_name}' is inactive",
                    }

                print(
                    f"DEBUG: Found payment item: {payment_item.name}, is_membership: {payment_item.is_membership}"
                )

                # 4. Validate payment amount
                try:
                    amount_to_pay = float(payment_data.get("amount", 0))
                except (ValueError, TypeError):
                    return {
                        "success": False,
                        "message": "Invalid payment amount format",
                    }

                if amount_to_pay <= 0:
                    return {
                        "success": False,
                        "message": "Payment amount must be positive",
                    }
                print(f"DEBUG: payment amount: '{amount_to_pay}'")

                # 5. Check for existing incomplete payment
                existing_payment = PaymentService.get_existing_incomplete_payment(
                    session, user_id, payment_item_name
                )

                if existing_payment:
                    print(f"DEBUG: Existing payment found: '{existing_payment}'")
                    # Add to existing payment
                    return self._add_partial_payment(
                        session, existing_payment, amount_to_pay, payment_data
                    )
                else:
                    # Create new payment
                    print("DEBUG: calling Creating new payment")
                    return self._create_new_payment(
                        session, patron, payment_item, amount_to_pay, payment_data
                    )

            except Exception as e:
                import traceback

                print(f"ERROR in create method: {str(e)}")
                print(f"Traceback: {traceback.format_exc()}")
                return {
                    "success": False,
                    "message": f"Error creating payment: {str(e)}",
                }

    def get_existing_incomplete_payment_by_id(self, user_id, payment_item_id):
        """Get existing incomplete payment by payment item ID instead of name"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(joinedload(Payment.partial_payments))
                .filter(
                    Payment.user_id == user_id,
                    Payment.payment_item_id == payment_item_id,
                    Payment.status.in_([PaymentStatus.PENDING, PaymentStatus.PARTIAL]),
                    Payment.status != PaymentStatus.EXPIRED,
                )
                .first()
            )

    def debug_payment_items(self):
        """Debug method to check what payment items exist"""
        with self.db_manager.get_session() as session:
            items = session.query(PaymentItem).all()
            print("\n=== DEBUG: Payment Items in Database ===")
            if not items:
                print("No payment items found!")
                return []

            for item in items:
                print(f"ID: {item.id}")
                print(f"Name: '{item.name}'")
                print(f"Display Name: {item.display_name}")
                print(f"Active: {item.is_active}")
                print(f"Is Membership: {item.is_membership}")
                print(f"Base Amount: {item.base_amount}")
                print("---")

            return items

    def ensure_payment_items_exist(self):
        """Ensure payment items are initialized"""
        try:
            with self.db_manager.get_session() as session:
                count = session.query(PaymentItem).count()
                if count == 0:
                    print("No payment items found. Initializing defaults...")
                    PaymentService.create_default_payment_items(session)
                    print("Default payment items created.")
                else:
                    print(f"Found {count} payment items in database.")
                return True
        except Exception as e:
            print(f"Error checking/creating payment items: {e}")
            return False

    def _create_new_payment(
        self,
        session,
        patron: Patron,
        payment_item: PaymentItem,
        amount_to_pay,
        payment_data,
    ):
        """Create a new payment record"""
        try:
            # Get total amount due
            total_amount = PaymentService.get_payment_amount(payment_item, patron)
            if total_amount is None:
                return {
                    "success": False,
                    "message": f"No pricing configured for {payment_item.display_name} and patron category {patron.category.value}",
                }
            print(f"DEBUG: Total amount to be paid: {total_amount}")

            # Validate amount doesn't exceed total
            if amount_to_pay > total_amount:
                return {
                    "success": False,
                    "message": f"Payment amount (KSh {amount_to_pay:.2f}) cannot exceed total due (KSh {total_amount:.2f})",
                }

            # Calculate membership dates if applicable
            membership_start, membership_expiry = None, None
            if payment_item.is_membership:
                membership_start, membership_expiry = (
                    PaymentService.calculate_membership_dates(payment_item)
                )

            print("DEBUG: Processed membership dates")

            # Create payment record
            payment = Payment(
                user_id=patron.user_id,
                payment_item_id=payment_item.id,
                amount_paid=amount_to_pay,
                total_amount_due=total_amount,
                payment_date=datetime.strptime(
                    payment_data["payment_date"], "%Y-%m-%d"
                ).date(),
                membership_start_date=membership_start,
                membership_expiry_date=membership_expiry,
                notes=payment_data.get("notes"),
            )

            # After creating the Payment object:
            payment.payment_item = payment_item
            payment.update_status()

            print("DEBUG: creating new payment")

            # Update status based on amount paid
            payment.update_status()

            session.add(payment)
            session.flush()  # Assigns payment_id

            # Create partial payment record
            partial_payment = PartialPayment(
                payment_id=payment.payment_id,
                amount=amount_to_pay,
                payment_date=payment.payment_date,
                payment_method=payment_data.get("payment_method", "cash"),
                reference_number=payment_data.get("reference_number"),
                notes=payment_data.get("partial_payment_notes"),
            )
            print("DEBUG: creating new partial payment")
            session.add(partial_payment)

            # Handle membership activation if fully paid
            if payment.is_fully_paid() and payment_item.is_membership:
                PaymentService.activate_membership(session, patron, payment)

            session.commit()

            # Prepare response message
            if payment.is_fully_paid():
                message = f"Payment of KSh {amount_to_pay:.2f} completed for {payment_item.display_name}"
                if payment_item.is_membership:
                    message += f". Membership activated until {membership_expiry}"
            else:
                remaining = payment.get_remaining_amount()
                message = f"Partial payment of KSh {amount_to_pay:.2f} recorded. Remaining: KSh {remaining:.2f}"

            return {
                "success": True,
                "message": message,
                "payment_id": payment.payment_id,
                "status": payment.status.value,
                "amount_paid": payment.amount_paid,
                "total_due": payment.total_amount_due,
                "remaining": payment.get_remaining_amount(),
            }

        except Exception as e:
            session.rollback()
            return {"success": False, "message": f"Error creating payment: {str(e)}"}

    def _add_partial_payment(
        self, session, existing_payment, amount_to_pay, payment_data
    ):
        """Add a partial payment to an existing incomplete payment"""
        try:
            remaining_amount = existing_payment.get_remaining_amount()

            # Validate amount doesn't exceed remaining
            if amount_to_pay > remaining_amount:
                return {
                    "success": False,
                    "message": f"Payment amount (KSh {amount_to_pay:.2f}) cannot exceed remaining balance (KSh {remaining_amount:.2f})",
                }

            # Update payment amounts
            existing_payment.amount_paid += amount_to_pay
            existing_payment.updated_at = datetime.utcnow()

            # Ensure payment_item relationship is loaded for update_status()
            if (
                not hasattr(existing_payment, "payment_item")
                or existing_payment.payment_item is None
            ):
                existing_payment.payment_item = (
                    session.query(PaymentItem)
                    .filter(PaymentItem.id == existing_payment.payment_item_id)
                    .first()
                )

            # Update status - now payment_item is available
            existing_payment.update_status()

            # Create partial payment record
            partial_payment = PartialPayment(
                payment_id=existing_payment.payment_id,
                amount=amount_to_pay,
                payment_date=datetime.strptime(
                    payment_data["payment_date"], "%Y-%m-%d"
                ).date(),
                payment_method=payment_data.get("payment_method", "cash"),
                reference_number=payment_data.get("reference_number"),
                notes=payment_data.get("partial_payment_notes"),
            )
            session.add(partial_payment)

            # Handle membership activation if now fully paid
            if (
                existing_payment.is_fully_paid()
                and existing_payment.payment_item.is_membership
            ):
                patron = existing_payment.patron
                PaymentService.activate_membership(session, patron, existing_payment)

            session.commit()

            # Prepare response message
            new_remaining = existing_payment.get_remaining_amount()
            if existing_payment.is_fully_paid():
                message = f"Final payment of KSh {amount_to_pay:.2f} completed for {existing_payment.payment_item.display_name}"
                if existing_payment.payment_item.is_membership:
                    message += f". Membership activated until {existing_payment.membership_expiry_date}"
            else:
                message = f"Partial payment of KSh {amount_to_pay:.2f} added. Remaining: KSh {new_remaining:.2f}"

            return {
                "success": True,
                "message": message,
                "payment_id": existing_payment.payment_id,
                "status": existing_payment.status.value,
                "amount_paid": existing_payment.amount_paid,
                "total_due": existing_payment.total_amount_due,
                "remaining": new_remaining,
            }

        except Exception as e:
            session.rollback()
            return {
                "success": False,
                "message": f"Error adding partial payment: {str(e)}",
            }

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

                # Update payment attributes
                for key, value in update_data.items():
                    if hasattr(payment, key):
                        setattr(payment, key, value)

                payment.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(payment)

                return {
                    "success": True,
                    "payment": payment,
                    "message": "Payment updated successfully",
                }

        except Exception as e:
            return {"success": False, "message": f"Error updating payment: {str(e)}"}

    def expire_memberships(self):
        """Expire all memberships that have passed their expiry date"""
        try:
            with self.db_manager.get_session() as session:
                expired_count = PaymentService.expire_old_memberships(session)
                return {
                    "success": True,
                    "message": f"Expired {expired_count} memberships",
                    "expired_count": expired_count,
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error expiring memberships: {str(e)}",
            }

    # ---------- DELETE ----------

    def delete_payment(self, payment_id):
        """Delete payment record (only if no partial payments made)"""
        try:
            with self.db_manager.get_session() as session:
                payment = (
                    session.query(Payment)
                    .options(joinedload(Payment.partial_payments))
                    .filter(Payment.payment_id == payment_id)
                    .first()
                )

                if not payment:
                    return {"success": False, "message": "Payment not found"}

                # Don't allow deletion if any amount has been paid
                if payment.amount_paid > 0:
                    return {
                        "success": False,
                        "message": f"Cannot delete payment with KSh {payment.amount_paid:.2f} already paid",
                    }

                session.delete(payment)
                session.commit()
                return {"success": True, "message": "Payment deleted successfully"}

        except Exception as e:
            return {"success": False, "message": f"Error deleting payment: {str(e)}"}

    # ---------- ENHANCED METHODS ----------

    def get_payment_summary(self, user_id: int) -> Dict:
        """Get comprehensive payment summary for a patron"""
        try:
            with self.db_manager.get_session() as session:
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()
                if not patron:
                    return {"success": False, "message": "Patron not found"}

                # Expire membership if needed
                patron.expire_membership_if_needed()

                payments = self.get_by_patron(user_id)
                incomplete_payments = [
                    p
                    for p in payments
                    if p.status in [PaymentStatus.PENDING, PaymentStatus.PARTIAL]
                ]

                # Calculate totals by payment item
                payment_totals = {}
                for payment in payments:
                    item_name = payment.payment_item.name
                    if item_name not in payment_totals:
                        payment_totals[item_name] = {
                            "display_name": payment.payment_item.display_name,
                            "total_paid": 0.0,
                            "payment_count": 0,
                            "incomplete_count": 0,
                            "incomplete_amount": 0.0,
                        }

                    payment_totals[item_name]["total_paid"] += payment.amount_paid
                    payment_totals[item_name]["payment_count"] += 1

                    if not payment.is_fully_paid():
                        payment_totals[item_name]["incomplete_count"] += 1
                        payment_totals[item_name][
                            "incomplete_amount"
                        ] += payment.get_remaining_amount()

                total_paid = sum(p.amount_paid for p in payments)
                total_outstanding = sum(
                    p.get_remaining_amount() for p in incomplete_payments
                )

                # Membership info
                membership_info = {
                    "status": patron.membership_status.value,
                    "type": patron.membership_type,
                    "start_date": patron.membership_start_date,
                    "expiry_date": patron.membership_expiry_date,
                    "days_remaining": patron.get_membership_days_remaining(),
                    "is_active": patron.is_membership_active(),
                }

                return {
                    "success": True,
                    "patron": patron,
                    "total_paid": total_paid,
                    "total_outstanding": total_outstanding,
                    "payment_count": len(payments),
                    "incomplete_payments_count": len(incomplete_payments),
                    "payment_breakdown": payment_totals,
                    "incomplete_payments": incomplete_payments,
                    "membership": membership_info,
                }

        except Exception as e:
            return {"success": False, "message": f"Error getting summary: {str(e)}"}

    def get_available_payment_items_for_patron(self, user_id: int) -> Dict:
        """Get payment items available for a specific patron with calculated amounts"""
        try:
            with self.db_manager.get_session() as session:
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()
                if not patron:
                    return {"success": False, "message": "Patron not found"}

                # Expire membership if needed
                patron.expire_membership_if_needed()

                payment_items = (
                    session.query(PaymentItem)
                    .filter(PaymentItem.is_active.is_(True))
                    .all()
                )

                available_items = []
                for item in payment_items:
                    amount = item.get_amount_for_patron(patron)
                    if amount is not None:
                        # Check for existing incomplete payment
                        existing_payment = (
                            PaymentService.get_existing_incomplete_payment(
                                session, user_id, item.name
                            )
                        )

                        if existing_payment:
                            remaining_amount = existing_payment.get_remaining_amount()
                            display_text = f"{item.display_name} - KSh {remaining_amount:.2f} remaining"
                            amount_to_show = remaining_amount
                            has_incomplete = True
                        else:
                            display_text = f"{item.display_name} - KSh {amount:.2f}"
                            amount_to_show = amount
                            has_incomplete = False

                        # For memberships, check if already active
                        if item.is_membership and patron.is_membership_active():
                            if patron.membership_type == item.name:
                                continue  # Skip if same membership type is active

                        available_items.append(
                            {
                                "id": item.id,
                                "name": item.name,
                                "display_name": item.display_name,
                                "description": item.description,
                                "amount": amount_to_show,
                                "total_amount": amount,
                                "supports_installments": item.supports_installments,
                                "max_installments": item.max_installments,
                                "formatted_display": display_text,
                                "has_incomplete_payment": has_incomplete,
                                "is_membership": item.is_membership,
                                "membership_duration_months": item.membership_duration_months,
                            }
                        )

                return {
                    "success": True,
                    "patron": patron,
                    "available_items": available_items,
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error getting available items: {str(e)}",
            }

    def get_payment_analytics(self, start_date=None, end_date=None):
        """Get payment analytics and insights"""
        try:
            with self.db_manager.get_session() as session:
                # Default to current month if no dates provided
                if not start_date:
                    start_date = date.today().replace(day=1)
                if not end_date:
                    end_date = date.today()

                # Convert strings to dates if needed
                if isinstance(start_date, str):
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                if isinstance(end_date, str):
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                payments = (
                    session.query(Payment)
                    .join(PaymentItem)
                    .filter(
                        Payment.payment_date >= start_date,
                        Payment.payment_date <= end_date,
                    )
                    .all()
                )

                # Analytics by payment item
                analytics = {}
                total_revenue = 0.0
                total_outstanding = 0.0

                for payment in payments:
                    item_name = payment.payment_item.name
                    if item_name not in analytics:
                        analytics[item_name] = {
                            "display_name": payment.payment_item.display_name,
                            "count": 0,
                            "total_collected": 0.0,
                            "total_outstanding": 0.0,
                            "avg_payment": 0.0,
                            "completed_count": 0,
                            "partial_count": 0,
                            "pending_count": 0,
                        }

                    analytics[item_name]["count"] += 1
                    analytics[item_name]["total_collected"] += payment.amount_paid
                    analytics[item_name][
                        "total_outstanding"
                    ] += payment.get_remaining_amount()

                    if payment.status == PaymentStatus.COMPLETED:
                        analytics[item_name]["completed_count"] += 1
                    elif payment.status == PaymentStatus.PARTIAL:
                        analytics[item_name]["partial_count"] += 1
                    elif payment.status == PaymentStatus.PENDING:
                        analytics[item_name]["pending_count"] += 1

                    total_revenue += payment.amount_paid
                    total_outstanding += payment.get_remaining_amount()

                # Calculate averages
                for item_data in analytics.values():
                    if item_data["count"] > 0:
                        item_data["avg_payment"] = (
                            item_data["total_collected"] / item_data["count"]
                        )

                return {
                    "success": True,
                    "period": {"start": start_date, "end": end_date},
                    "total_revenue": total_revenue,
                    "total_outstanding": total_outstanding,
                    "total_payments": len(payments),
                    "analytics_by_item": analytics,
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error generating analytics: {str(e)}",
            }


# Enhanced Payment Item Management Controller
class PaymentItemController:
    """Controller for managing payment items and their configurations"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def get_all(self):
        """Get all payment items with their category prices"""
        with self.db_manager.get_session() as session:
            return (
                session.query(PaymentItem)
                .options(joinedload(PaymentItem.category_prices))
                .order_by(PaymentItem.display_name)
                .all()
            )

    def get_all_active_items(self):
        """Get all active payment items with their category prices"""
        with self.db_manager.get_session() as session:
            return (
                session.query(PaymentItem)
                .options(joinedload(PaymentItem.category_prices))
                .filter(PaymentItem.is_active.is_(True))
                .order_by(PaymentItem.display_name)
                .all()
            )

    def get_payment_items_for_patron(self, patron):
        """Get all payment items with their amounts for a specific patron"""
        with self.db_manager.get_session() as session:
            items = (
                session.query(PaymentItem).filter(PaymentItem.is_active.is_(True)).all()
            )

            result = []
            for item in items:
                amount = item.get_amount_for_patron(patron)
                if amount is not None:
                    # Check for existing incomplete payment
                    existing_payment = PaymentService.get_existing_incomplete_payment(
                        session, patron.user_id, item.name
                    )

                    if existing_payment:
                        remaining_amount = existing_payment.get_remaining_amount()
                        display_text = f"{item.display_name} - KSh {remaining_amount:.2f} remaining"
                        amount_to_show = remaining_amount
                        has_incomplete = True
                    else:
                        display_text = f"{item.display_name} - KSh {amount:.2f}"
                        amount_to_show = amount
                        has_incomplete = False

                    result.append(
                        {
                            "item": item,
                            "amount": amount_to_show,
                            "total_amount": amount,
                            "formatted_display": display_text,
                            "supports_installments": item.supports_installments,
                            "max_installments": item.max_installments,
                            "has_incomplete_payment": has_incomplete,
                            "existing_payment": existing_payment,
                        }
                    )

            return result

    def initialize_default_payment_items(self):
        """Initialize default payment items for the system"""
        try:
            with self.db_manager.get_session() as session:
                PaymentService.create_default_payment_items(session)
                return {"success": True, "message": "Default payment items initialized"}
        except Exception as e:
            return {
                "success": False,
                "message": f"Error initializing payment items: {str(e)}",
            }
            session.rollback()
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    def _create_new_payment(
        self, session, patron, payment_item, amount_to_pay, payment_data
    ):
        """Create a new payment record"""
        try:
            # Get total amount due
            total_amount = PaymentService.get_payment_amount(payment_item, patron)
            if total_amount is None:
                return {
                    "success": False,
                    "message": f"No pricing configured for {payment_item.display_name} and patron category {patron.category.value}",
                }

            # Validate amount doesn't exceed total
            if amount_to_pay > total_amount:
                return {
                    "success": False,
                    "message": f"Payment amount (KSh {amount_to_pay:.2f}) cannot exceed total due (KSh {total_amount:.2f})",
                }

            # Calculate membership dates if applicable
            membership_start, membership_expiry = None, None
            if payment_item.is_membership:
                membership_start, membership_expiry = (
                    PaymentService.calculate_membership_dates(payment_item)
                )

            # Create payment record
            payment = Payment(
                user_id=patron.user_id,
                payment_item_id=payment_item.id,
                amount_paid=amount_to_pay,
                total_amount_due=total_amount,
                payment_date=datetime.strptime(
                    payment_data["payment_date"], "%Y-%m-%d"
                ).date(),
                membership_start_date=membership_start,
                membership_expiry_date=membership_expiry,
                notes=payment_data.get("notes"),
            )

            # Update status based on amount paid
            payment.update_status()

            session.add(payment)
            session.flush()  # Get payment ID

            # Create partial payment record
            partial_payment = PartialPayment(
                payment_id=payment.payment_id,
                amount=amount_to_pay,
                payment_date=payment.payment_date,
                payment_method=payment_data.get("payment_method", "cash"),
                reference_number=payment_data.get("reference_number"),
                notes=payment_data.get("partial_payment_notes"),
            )
            session.add(partial_payment)

            # Handle membership activation if fully paid
            if payment.is_fully_paid() and payment_item.is_membership:
                PaymentService.activate_membership(session, patron, payment)

            session.commit()

            # Prepare response message
            if payment.is_fully_paid():
                message = f"Payment of KSh {amount_to_pay:.2f} completed for {payment_item.display_name}"
                if payment_item.is_membership:
                    message += f". Membership activated until {membership_expiry}"
            else:
                remaining = payment.get_remaining_amount()
                message = f"Partial payment of KSh {amount_to_pay:.2f} recorded. Remaining: KSh {remaining:.2f}"

            return {
                "success": True,
                "message": message,
                "payment_id": payment.payment_id,
                "status": payment.status.value,
                "amount_paid": payment.amount_paid,
                "total_due": payment.total_amount_due,
                "remaining": payment.get_remaining_amount(),
            }

        except Exception as e:
            return {"success": False, "message": f"Error creating payment: {str(e)}"}
