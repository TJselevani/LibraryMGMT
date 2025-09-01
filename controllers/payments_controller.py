# Enhanced payments_controller.py
from datetime import datetime, date
from sqlalchemy.orm import joinedload
from db.models import (
    Payment,
    Patron,
    Installment,
    PaymentItem,
    PaymentItemPrice,
    PaymentService,
    PaymentStatus,
    Category,
)
from typing import Dict, List


class PaymentController:
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ---------- GET METHODS ----------

    def get_all(self):
        """Get all payments with patron, payment_item and installments eagerly loaded"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.payment_item),
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
                    joinedload(Payment.payment_item),
                    joinedload(Payment.installments),
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
                    joinedload(Payment.installments),
                )
                .filter(Payment.user_id == user_id)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_by_payment_item(self, payment_item_name):
        """Get all payments of a specific payment item type"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .join(PaymentItem)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.payment_item),
                    joinedload(Payment.installments),
                )
                .filter(PaymentItem.name == payment_item_name)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_by_status(self, status):
        """Get payments by status"""
        with self.db_manager.get_session() as session:
            return (
                session.query(Payment)
                .options(
                    joinedload(Payment.patron),
                    joinedload(Payment.payment_item),
                    joinedload(Payment.installments),
                )
                .filter(Payment.status == status)
                .order_by(Payment.payment_date.desc())
                .all()
            )

    def get_pending_installments(self, user_id=None):
        """Get pending installments, optionally filtered by patron"""
        with self.db_manager.get_session() as session:
            query = (
                session.query(Installment)
                .join(Payment)
                .options(
                    joinedload(Installment.payment).joinedload(Payment.patron),
                    joinedload(Installment.payment).joinedload(Payment.payment_item),
                )
                .filter(
                    Installment.is_paid.is_(False), Installment.due_date <= date.today()
                )
            )

            if user_id:
                query = query.filter(Payment.user_id == user_id)

            return query.order_by(Installment.due_date.asc()).all()

    # ---------- CREATE ----------
    def create(self, payment_data: Dict) -> Dict:
        """Create a new payment with enhanced validation"""
        with self.db_manager.get_session() as session:
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

                # 2. Validate payment item exists and is active
                payment_item = (
                    session.query(PaymentItem)
                    .filter(
                        PaymentItem.name == payment_data.get("payment_item_name"),
                        PaymentItem.is_active.is_(True),
                    )
                    .first()
                )
                if not payment_item:
                    return {
                        "success": False,
                        "message": f"Payment item '{payment_data.get('payment_item_name')}' not found or inactive",
                    }

                # 3. Validate payment data
                validation_errors = PaymentService.validate_payment_data(
                    payment_data, patron, payment_item
                )
                if validation_errors:
                    return {
                        "success": False,
                        "message": "Validation errors: " + "; ".join(validation_errors),
                    }

                # 4. Determine payment amount and status
                expected_amount = PaymentService.get_payment_amount(
                    payment_item, patron
                )
                installments_data = payment_data.get("installments", [])

                if installments_data:
                    # Installment payment
                    total_amount = sum(
                        inst.get("amount", 0) for inst in installments_data
                    )
                    status = (
                        PaymentStatus.PENDING
                    )  # Will be updated based on installments
                else:
                    # Full payment
                    total_amount = expected_amount
                    status = PaymentStatus.COMPLETED

                # 5. Create payment record
                payment = Payment(
                    user_id=payment_data["user_id"],
                    payment_item_id=payment_item.id,
                    amount=total_amount,
                    payment_date=datetime.strptime(
                        payment_data["payment_date"], "%Y-%m-%d"
                    ).date(),
                    status=status,
                    notes=payment_data.get("notes"),
                )

                session.add(payment)
                session.flush()  # Get payment ID

                # 6. Create installments if specified
                if installments_data:
                    installment_result = self._create_installments(
                        session, payment.payment_id, installments_data
                    )
                    if not installment_result["success"]:
                        session.rollback()
                        return installment_result

                    # Update payment status based on installments
                    payment.update_status()

                # 7. Handle post-payment actions (e.g., activate membership)
                self._handle_post_payment_actions(
                    session, payment, patron, payment_item
                )

                session.commit()

                return {
                    "success": True,
                    "message": f"Payment of KSh {payment.amount:.2f} for {payment_item.display_name} created successfully",
                    "payment_id": payment.payment_id,
                }

            except Exception as e:
                session.rollback()
                return {"success": False, "message": f"Unexpected error: {str(e)}"}

    def _create_installments(
        self, session, payment_id: int, installments_data: List[Dict]
    ) -> Dict:
        """Create installment records for a payment"""
        try:
            for installment_data in installments_data:
                installment = Installment(
                    payment_id=payment_id,
                    installment_number=installment_data["installment_number"],
                    amount=float(installment_data["amount"]),
                    due_date=datetime.strptime(
                        installment_data["date"], "%Y-%m-%d"
                    ).date(),
                    notes=installment_data.get("notes"),
                )
                session.add(installment)

            return {"success": True}

        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create installments: {str(e)}",
            }

    def _handle_post_payment_actions(self, session, payment, patron, payment_item):
        """Handle actions after successful payment creation"""
        # Activate membership for membership payments
        if (
            payment_item.name == "membership"
            and payment.status == PaymentStatus.COMPLETED
        ):
            patron.membership_status = "active"

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

    def mark_installment_paid(self, installment_id: int) -> Dict:
        """Mark an installment as paid and update payment status"""
        try:
            with self.db_manager.get_session() as session:
                installment = (
                    session.query(Installment)
                    .filter(Installment.installment_id == installment_id)
                    .first()
                )

                if not installment:
                    return {"success": False, "message": "Installment not found"}

                if installment.is_paid:
                    return {"success": False, "message": "Installment already paid"}

                # Mark installment as paid
                installment.is_paid = True
                installment.paid_date = date.today()

                # Update parent payment status
                payment = (
                    session.query(Payment)
                    .filter(Payment.payment_id == installment.payment_id)
                    .first()
                )
                payment.update_status()

                # Handle post-payment actions if payment is now complete
                if payment.status == PaymentStatus.COMPLETED:
                    self._handle_post_payment_actions(
                        session, payment, payment.patron, payment.payment_item
                    )

                session.commit()
                return {
                    "success": True,
                    "message": "Installment marked as paid",
                    "payment_status": payment.status.value,
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating installment: {str(e)}",
            }

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

                # Check if any installments are already paid
                paid_installments = [
                    inst for inst in payment.installments if inst.is_paid
                ]
                if paid_installments:
                    return {
                        "success": False,
                        "message": f"Cannot delete payment with {len(paid_installments)} paid installments",
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

                payments = self.get_by_patron(user_id)
                pending_installments = (
                    session.query(Installment)
                    .join(Payment)
                    .filter(Payment.user_id == user_id, Installment.is_paid.is_(False))
                    .all()
                )

                # Calculate totals by payment item
                payment_totals = {}
                for payment in payments:
                    item_name = payment.payment_item.name
                    if item_name not in payment_totals:
                        payment_totals[item_name] = {
                            "display_name": payment.payment_item.display_name,
                            "total_paid": 0.0,
                            "payment_count": 0,
                        }

                    payment_totals[item_name]["total_paid"] += payment.amount
                    payment_totals[item_name]["payment_count"] += 1

                total_paid = sum(p.amount for p in payments)
                total_outstanding = sum(i.amount for i in pending_installments)

                return {
                    "success": True,
                    "patron": patron,
                    "total_paid": total_paid,
                    "total_outstanding": total_outstanding,
                    "payment_count": len(payments),
                    "pending_installments_count": len(pending_installments),
                    "payment_breakdown": payment_totals,
                    "pending_installments": pending_installments,
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

                payment_items = (
                    session.query(PaymentItem)
                    .filter(PaymentItem.is_active.is_(True))
                    .all()
                )

                available_items = []
                for item in payment_items:
                    amount = item.get_amount_for_patron(patron)
                    if amount is not None:
                        available_items.append(
                            {
                                "id": item.id,
                                "name": item.name,
                                "display_name": item.display_name,
                                "description": item.description,
                                "amount": amount,
                                "supports_installments": item.supports_installments,
                                "max_installments": item.max_installments,
                                "formatted_display": f"{item.display_name} - KSh {amount:.2f}",
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

    def validate_patron_can_pay(self, user_id: int, payment_item_name: str) -> Dict:
        """Validate if patron can make a specific payment"""
        try:
            with self.db_manager.get_session() as session:
                patron = session.query(Patron).filter(Patron.user_id == user_id).first()
                if not patron:
                    return {"success": False, "message": "Patron not found"}

                payment_item = (
                    session.query(PaymentItem)
                    .filter(
                        PaymentItem.name == payment_item_name,
                        PaymentItem.is_active.is_(True),
                    )
                    .first()
                )
                if not payment_item:
                    return {
                        "success": False,
                        "message": f"Payment item '{payment_item_name}' not found or inactive",
                    }

                # Check for existing active membership (prevent duplicate memberships)
                if payment_item.name == "membership":
                    existing_membership = (
                        session.query(Payment)
                        .join(PaymentItem)
                        .filter(
                            Payment.user_id == user_id,
                            PaymentItem.name == "membership",
                            Payment.status.in_(
                                [PaymentStatus.COMPLETED, PaymentStatus.PARTIAL]
                            ),
                        )
                        .first()
                    )

                    if existing_membership and patron.membership_status == "active":
                        return {
                            "success": False,
                            "message": "Patron already has an active membership",
                        }

                # Check if patron has pending installments for the same item
                pending_installments = (
                    session.query(Installment)
                    .join(Payment)
                    .join(PaymentItem)
                    .filter(
                        Payment.user_id == user_id,
                        PaymentItem.name == payment_item_name,
                        Installment.is_paid.is_(False),
                    )
                    .count()
                )

                if pending_installments > 0:
                    return {
                        "success": False,
                        "message": f"Patron has {pending_installments} pending installments for {payment_item.display_name}",
                    }

                return {
                    "success": True,
                    "patron": patron,
                    "payment_item": payment_item,
                    "amount": payment_item.get_amount_for_patron(patron),
                }

        except Exception as e:
            return {"success": False, "message": f"Validation error: {str(e)}"}

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

                for payment in payments:
                    item_name = payment.payment_item.name
                    if item_name not in analytics:
                        analytics[item_name] = {
                            "display_name": payment.payment_item.display_name,
                            "count": 0,
                            "total_amount": 0.0,
                            "avg_amount": 0.0,
                            "completed_count": 0,
                            "pending_count": 0,
                            "partial_count": 0,
                        }

                    analytics[item_name]["count"] += 1
                    analytics[item_name]["total_amount"] += payment.amount

                    if payment.status == PaymentStatus.COMPLETED:
                        analytics[item_name]["completed_count"] += 1
                    elif payment.status == PaymentStatus.PENDING:
                        analytics[item_name]["pending_count"] += 1
                    elif payment.status == PaymentStatus.PARTIAL:
                        analytics[item_name]["partial_count"] += 1

                    total_revenue += payment.amount

                # Calculate averages
                for item_data in analytics.values():
                    if item_data["count"] > 0:
                        item_data["avg_amount"] = (
                            item_data["total_amount"] / item_data["count"]
                        )

                return {
                    "success": True,
                    "period": {"start": start_date, "end": end_date},
                    "total_revenue": total_revenue,
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

    def get_item_by_name(self, name):
        """Get payment item by name"""
        with self.db_manager.get_session() as session:
            return (
                session.query(PaymentItem)
                .options(joinedload(PaymentItem.category_prices))
                .filter(PaymentItem.name == name)
                .first()
            )

    def create_payment_item(self, item_data):
        """Create a new payment item"""
        try:
            with self.db_manager.get_session() as session:
                # Validate required fields
                required_fields = ["name", "display_name"]
                for field in required_fields:
                    if field not in item_data or not item_data[field]:
                        return {
                            "success": False,
                            "message": f"Missing required field: {field}",
                        }

                # Check for duplicate name
                existing = (
                    session.query(PaymentItem).filter_by(name=item_data["name"]).first()
                )
                if existing:
                    return {
                        "success": False,
                        "message": f"Payment item with name '{item_data['name']}' already exists",
                    }

                # Validate installment settings
                if item_data.get("supports_installments", False):
                    max_installments = item_data.get("max_installments", 1)
                    if max_installments < 1:
                        return {
                            "success": False,
                            "message": "Max installments must be at least 1",
                        }

                # Create payment item
                payment_item_data = {
                    k: v for k, v in item_data.items() if k != "category_prices"
                }
                payment_item = PaymentItem(**payment_item_data)
                session.add(payment_item)
                session.flush()  # Get ID

                # Create category prices if specified
                if item_data.get("category_prices"):
                    for price_data in item_data["category_prices"]:
                        if price_data["amount"] <= 0:
                            return {
                                "success": False,
                                "message": "Category price amounts must be positive",
                            }

                        price = PaymentItemPrice(
                            payment_item_id=payment_item.id,
                            category=Category(price_data["category"]),
                            amount=price_data["amount"],
                        )
                        session.add(price)

                session.commit()
                session.refresh(payment_item)

                return {
                    "success": True,
                    "payment_item": payment_item,
                    "message": f"Payment item '{payment_item.display_name}' created successfully",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error creating payment item: {str(e)}",
            }

    def update_payment_item(self, item_id, update_data):
        """Update a payment item"""
        try:
            with self.db_manager.get_session() as session:
                item = (
                    session.query(PaymentItem).filter(PaymentItem.id == item_id).first()
                )
                if not item:
                    return {"success": False, "message": "Payment item not found"}

                # Update basic fields
                for key, value in update_data.items():
                    if key != "category_prices" and hasattr(item, key):
                        setattr(item, key, value)

                # Update category prices if provided
                if "category_prices" in update_data:
                    # Remove existing prices
                    session.query(PaymentItemPrice).filter_by(
                        payment_item_id=item.id
                    ).delete()

                    # Add new prices
                    for price_data in update_data["category_prices"]:
                        price = PaymentItemPrice(
                            payment_item_id=item.id,
                            category=Category(price_data["category"]),
                            amount=price_data["amount"],
                        )
                        session.add(price)

                item.updated_at = datetime.utcnow()
                session.commit()
                session.refresh(item)

                return {
                    "success": True,
                    "payment_item": item,
                    "message": f"Payment item '{item.display_name}' updated successfully",
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error updating payment item: {str(e)}",
            }

    def deactivate_payment_item(self, item_id):
        """Deactivate a payment item (soft delete)"""
        return self.update_payment_item(item_id, {"is_active": False})

    def get_payment_items_for_patron(self, patron):
        """Get all payment items with their amounts for a specific patron"""
        with self.db_manager.get_session() as session:
            items = (
                session.query(PaymentItem).filter(PaymentItem.is_active.is_(True)).all()
            )

            result = []
            for item in items:
                amount = item.get_amount_for_patron(patron)
                if amount is not None:  # Only include items with valid pricing
                    result.append(
                        {
                            "item": item,
                            "amount": amount,
                            "formatted_display": f"{item.display_name} - KSh {amount:.2f}",
                            "supports_installments": item.supports_installments,
                            "max_installments": item.max_installments,
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


# Database migration helper
class PaymentSystemMigration:
    """Helper class for migrating from old payment system to new flexible system"""

    @staticmethod
    def migrate_existing_payments(db_manager):
        """Migrate existing payments to use PaymentItem references"""
        with db_manager.get_session() as session:
            try:
                # First, ensure default payment items exist
                PaymentService.create_default_payment_items(session)

                # Get payment items for mapping
                access_item = (
                    session.query(PaymentItem).filter_by(name="access").first()
                )
                study_item = (
                    session.query(PaymentItem).filter_by(name="study_room").first()
                )
                membership_item = (
                    session.query(PaymentItem).filter_by(name="membership").first()
                )

                if not all([access_item, study_item, membership_item]):
                    raise Exception("Default payment items not found")

                # Map old payment types to new items (if you have old data)
                # This would depend on your current Payment table structure
                # Uncomment and modify if you have existing data to migrate:

                # payments = session.query(Payment).filter(Payment.payment_item_id.is_(None)).all()
                # for payment in payments:
                #     if hasattr(payment, 'payment_type'):  # Old enum field
                #         if payment.payment_type == 'ACCESS':
                #             payment.payment_item_id = access_item.id
                #         elif payment.payment_type == 'STUDY_ROOM':
                #             payment.payment_item_id = study_item.id
                #         elif payment.payment_type == 'MEMBERSHIP':
                #             payment.payment_item_id = membership_item.id

                session.commit()
                return {"success": True, "message": "Migration completed successfully"}

            except Exception as e:
                session.rollback()
                return {"success": False, "message": f"Migration failed: {str(e)}"}
