# database_setup.py - Setup script for enhanced payment system

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import PaymentItem, PaymentItemPrice, Category, PaymentService, Payment
from db.database import Base
from datetime import datetime


class PaymentSystemSetup:
    """Setup and initialization for the enhanced payment system"""

    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all database tables"""
        try:
            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating tables: {str(e)}")
            return False

    def initialize_payment_items(self):
        """Initialize default payment items and pricing"""
        session = self.SessionLocal()
        try:
            # Create default payment items
            PaymentService.create_default_payment_items(session)

            # Add some additional example payment items
            additional_items = [
                {
                    "name": "equipment_rental",
                    "display_name": "Equipment Rental",
                    "description": "Rental fee for library equipment (laptops, tablets, etc.)",
                    "base_amount": 100.0,
                    "supports_installments": False,
                    "is_category_based": False,
                },
                {
                    "name": "workshop_fee",
                    "display_name": "Workshop Registration",
                    "description": "Fee for attending library workshops and training sessions",
                    "supports_installments": True,
                    "max_installments": 2,
                    "is_category_based": True,  # Different rates for different categories
                },
                {
                    "name": "printing_services",
                    "display_name": "Printing Services",
                    "description": "Fees for printing, scanning, and photocopying services",
                    "base_amount": 10.0,
                    "supports_installments": False,
                    "is_category_based": False,
                },
                {
                    "name": "research_assistance",
                    "display_name": "Research Assistance Fee",
                    "description": "Professional research assistance service",
                    "supports_installments": True,
                    "max_installments": 4,
                    "is_category_based": True,
                },
                {
                    "name": "event_registration",
                    "display_name": "Special Event Registration",
                    "description": "Registration for library events, lectures, and seminars",
                    "base_amount": 200.0,
                    "supports_installments": True,
                    "max_installments": 2,
                    "is_category_based": False,
                },
            ]

            for item_data in additional_items:
                existing = (
                    session.query(PaymentItem).filter_by(name=item_data["name"]).first()
                )
                if not existing:
                    item = PaymentItem(**item_data)
                    session.add(item)
                    session.flush()

                    # Add category pricing for category-based items
                    if item_data.get("is_category_based"):
                        category_prices = []

                        if item_data["name"] == "workshop_fee":
                            category_prices = [
                                {"category": Category.PUPIL, "amount": 50.0},
                                {"category": Category.STUDENT, "amount": 100.0},
                                {"category": Category.ADULT, "amount": 150.0},
                            ]
                        elif item_data["name"] == "research_assistance":
                            category_prices = [
                                {"category": Category.PUPIL, "amount": 300.0},
                                {"category": Category.STUDENT, "amount": 500.0},
                                {"category": Category.ADULT, "amount": 800.0},
                            ]

                        for price_data in category_prices:
                            price = PaymentItemPrice(
                                payment_item_id=item.id,
                                category=price_data["category"],
                                amount=price_data["amount"],
                            )
                            session.add(price)

            session.commit()
            print("Payment items initialized successfully")
            return True

        except Exception as e:
            session.rollback()
            print(f"Error initializing payment items: {str(e)}")
            return False
        finally:
            session.close()

    def validate_system_integrity(self):
        """Validate the payment system setup"""
        session = self.SessionLocal()
        try:
            validation_results = []

            # Check if default payment items exist
            required_items = ["access", "study_room", "membership"]
            for item_name in required_items:
                item = session.query(PaymentItem).filter_by(name=item_name).first()
                if item:
                    validation_results.append(f"✅ {item_name}: Found")

                    # Check category pricing for membership
                    if item_name == "membership" and item.is_category_based:
                        for category in Category:
                            price = (
                                session.query(PaymentItemPrice)
                                .filter_by(payment_item_id=item.id, category=category)
                                .first()
                            )
                            if price:
                                validation_results.append(
                                    f"  ✅ {category.value} pricing: KSh {price.amount:.2f}"
                                )
                            else:
                                validation_results.append(
                                    f"  ❌ Missing {category.value} pricing"
                                )
                else:
                    validation_results.append(f"❌ {item_name}: Missing")

            # Check for orphaned category prices
            orphaned_prices = (
                session.query(PaymentItemPrice)
                .filter(
                    ~PaymentItemPrice.payment_item_id.in_(
                        session.query(PaymentItem.id).filter(
                            PaymentItem.is_active._is(True)
                        )
                    )
                )
                .count()
            )

            if orphaned_prices > 0:
                validation_results.append(
                    f"⚠️  {orphaned_prices} orphaned category prices found"
                )

            print("\n🔍 System Validation Results:")
            print("-" * 40)
            for result in validation_results:
                print(result)

            return len([r for r in validation_results if r.startswith("❌")]) == 0

        except Exception as e:
            print(f"❌ Validation failed: {str(e)}")
            return False
        finally:
            session.close()


# Enhanced administration utilities
class PaymentAdminUtils:
    """Administrative utilities for payment system management"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def generate_payment_report(self, start_date=None, end_date=None):
        """Generate comprehensive payment report"""
        with self.db_manager.get_session() as session:
            try:
                from datetime import date, timedelta

                if not start_date:
                    start_date = date.today() - timedelta(days=30)
                if not end_date:
                    end_date = date.today()

                # Get payments in date range
                payments = (
                    session.query(Payment)
                    .join(PaymentItem)
                    .filter(
                        Payment.payment_date >= start_date,
                        Payment.payment_date <= end_date,
                    )
                    .all()
                )

                report = {
                    "period": {"start": start_date, "end": end_date},
                    "summary": {
                        "total_payments": len(payments),
                        "total_revenue": sum(p.amount for p in payments),
                        "completed_payments": len(
                            [p for p in payments if p.status.value == "completed"]
                        ),
                        "pending_payments": len(
                            [p for p in payments if p.status.value == "pending"]
                        ),
                    },
                    "by_payment_item": {},
                    "by_category": {},
                }

                # Group by payment item
                for payment in payments:
                    item_name = payment.payment_item.name
                    patron_category = payment.patron.category.value

                    if item_name not in report["by_payment_item"]:
                        report["by_payment_item"][item_name] = {
                            "display_name": payment.payment_item.display_name,
                            "count": 0,
                            "total_amount": 0.0,
                        }

                    report["by_payment_item"][item_name]["count"] += 1
                    report["by_payment_item"][item_name][
                        "total_amount"
                    ] += payment.amount

                    # Group by patron category
                    if patron_category not in report["by_category"]:
                        report["by_category"][patron_category] = {
                            "count": 0,
                            "total_amount": 0.0,
                        }

                    report["by_category"][patron_category]["count"] += 1
                    report["by_category"][patron_category][
                        "total_amount"
                    ] += payment.amount

                return {"success": True, "report": report}

            except Exception as e:
                return {
                    "success": False,
                    "message": f"Report generation failed: {str(e)}",
                }

    def update_payment_item_pricing(self, item_name, pricing_updates):
        """Bulk update pricing for a payment item"""
        with self.db_manager.get_session() as session:
            try:
                item = session.query(PaymentItem).filter_by(name=item_name).first()
                if not item:
                    return {
                        "success": False,
                        "message": f"Payment item '{item_name}' not found",
                    }

                if item.is_category_based:
                    # Update category prices
                    for category_str, new_amount in pricing_updates.items():
                        category = Category(category_str.lower())
                        price = (
                            session.query(PaymentItemPrice)
                            .filter_by(payment_item_id=item.id, category=category)
                            .first()
                        )

                        if price:
                            price.amount = new_amount
                        else:
                            # Create new price entry
                            new_price = PaymentItemPrice(
                                payment_item_id=item.id,
                                category=category,
                                amount=new_amount,
                            )
                            session.add(new_price)
                else:
                    # Update base amount
                    if "base_amount" in pricing_updates:
                        item.base_amount = pricing_updates["base_amount"]

                item.updated_at = datetime.utcnow()
                session.commit()

                return {
                    "success": True,
                    "message": f"Pricing updated for {item.display_name}",
                }

            except Exception as e:
                session.rollback()
                return {"success": False, "message": f"Pricing update failed: {str(e)}"}


# Usage example and testing
def setup_payment_system(database_url):
    """Main setup function"""
    setup = PaymentSystemSetup(database_url)
    return setup.run_full_setup()


# Quick start script
if __name__ == "__main__":
    # Replace with your actual database URL
    DATABASE_URL = "sqlite:///library.db"

    print("Enhanced Payment System Setup")
    print("=" * 40)

    # Run setup
    success = setup_payment_system(DATABASE_URL)

    if success:
        # Validate setup
        setup = PaymentSystemSetup(DATABASE_URL)
        setup.validate_system_integrity()

        print("\n🚀 Your enhanced payment system is ready!")
        print("\nKey improvements:")
        print("• Flexible payment items that can be added/modified")
        print("• Category-based pricing for different patron types")
        print("• Configurable installment options per payment type")
        print("• Enhanced payment tracking and status management")
        print("• Better validation and error handling")

        print("\n📝 To use in your application:")
        print("1. Replace your AddPaymentForm with EnhancedAddPaymentForm")
        print("2. Use PaymentItemController to manage payment services")
        print("3. Use enhanced PaymentController for payment operations")
    else:
        print("Setup failed. Please check the error messages and try again.")

    def create_sample_data(self):
        """Create sample payment items for testing"""
        session = self.SessionLocal()
        try:
            # Sample seasonal/event-based payment items
            seasonal_items = [
                {
                    "name": "summer_reading_program",
                    "display_name": "Summer Reading Program",
                    "description": "Registration fee for annual summer reading program",
                    "base_amount": 75.0,
                    "supports_installments": False,
                    "is_category_based": False,
                },
                {
                    "name": "computer_course",
                    "display_name": "Computer Skills Course",
                    "description": "6-week computer literacy course",
                    "supports_installments": True,
                    "max_installments": 3,
                    "is_category_based": True,
                },
                {
                    "name": "locker_rental",
                    "display_name": "Personal Locker Rental",
                    "description": "Monthly rental for personal storage locker",
                    "base_amount": 50.0,
                    "supports_installments": False,
                    "is_category_based": False,
                },
            ]

            for item_data in seasonal_items:
                existing = (
                    session.query(PaymentItem).filter_by(name=item_data["name"]).first()
                )
                if not existing:
                    item = PaymentItem(**item_data)
                    session.add(item)
                    session.flush()

                    # Add category pricing for computer course
                    if item_data["name"] == "computer_course":
                        course_prices = [
                            {"category": Category.PUPIL, "amount": 150.0},
                            {"category": Category.STUDENT, "amount": 250.0},
                            {"category": Category.ADULT, "amount": 400.0},
                        ]

                        for price_data in course_prices:
                            price = PaymentItemPrice(
                                payment_item_id=item.id,
                                category=price_data["category"],
                                amount=price_data["amount"],
                            )
                            session.add(price)

            session.commit()
            print("✅ Sample payment items created")
            return True

        except Exception as e:
            session.rollback()
            print(f"❌ Error creating sample data: {str(e)}")
            return False
        finally:
            session.close()

    def run_full_setup(self):
        """Run complete setup process"""
        print("🚀 Starting payment system setup...")

        success = True
        success &= self.create_tables()
        success &= self.initialize_payment_items()
        success &= self.create_sample_data()

        if success:
            print("🎉 Payment system setup completed successfully!")
            self.print_summary()
        else:
            print("❌ Setup completed with errors")

        return success

    def print_summary(self):
        """Print summary of available payment items"""
        session = self.SessionLocal()
        try:
            items = (
                session.query(PaymentItem).filter(PaymentItem.is_active.is_(True)).all()
            )

            print("\n📋 Available Payment Items:")
            print("-" * 50)

            for item in items:
                print(f"• {item.display_name}")
                print(f"  Name: {item.name}")

                if item.is_category_based:
                    print("  Category-based pricing:")
                    for price in item.category_prices:
                        print(
                            f"    - {price.category.value.title()}: KSh {price.amount:.2f}"
                        )
                else:
                    print(f"  Fixed price: KSh {item.base_amount:.2f}")

                if item.supports_installments:
                    print(f"  Installments: Up to {item.max_installments} payments")
                else:
                    print("  Payment: One-time only")

                print()

        except Exception as e:
            print(f"❌ Error printing summary: {str(e)}")
        finally:
            session.close()


# Migration utilities
class PaymentSystemMigration:
    """Helper for migrating from old payment system"""

    def __init__(self, database_url):
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def backup_existing_payments(self):
        """Create backup of existing payment data before migration"""
        session = self.SessionLocal()
        try:
            # This would depend on your current table structure
            # Example: Export to JSON or create backup table
            payments = session.query(Payment).all()

            backup_data = []
            for payment in payments:
                backup_data.append(
                    {
                        "payment_id": payment.payment_id,
                        "user_id": payment.user_id,
                        "amount": payment.amount,
                        "payment_date": payment.payment_date.isoformat(),
                        # Add other fields as needed
                    }
                )

            # Save backup (implement based on your needs)
            import json

            with open(
                f"payment_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w"
            ) as f:
                json.dump(backup_data, f, indent=2)

            print(f"✅ Backed up {len(backup_data)} payment records")
            return True

        except Exception as e:
            print(f"❌ Backup failed: {str(e)}")
            return False
        finally:
            session.close()

    def add_payment_item_columns(self):
        """Add new columns to existing payment table if needed"""
        # This would contain ALTER TABLE statements
        # Example SQL migrations you might need:

        migration_sql = [
            "ALTER TABLE payments ADD COLUMN payment_item_id INTEGER;",
            "ALTER TABLE payments ADD COLUMN status VARCHAR(20) DEFAULT 'completed';",
            "ALTER TABLE payments ADD COLUMN notes TEXT;",
            "ALTER TABLE payments ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            # Create foreign key constraint after populating data
            "ALTER TABLE payments ADD CONSTRAINT fk_payment_item "
            "FOREIGN KEY (payment_item_id) REFERENCES payment_items(id);",
        ]

        print("SQL migrations needed:")
        for sql in migration_sql:
            print(f"  {sql}")

        return migration_sql


def create_custom_payment_item_example():
    """Example of how to create custom payment items programmatically"""

    # Example: Create a library card replacement fee
    card_replacement_item = {
        "name": "card_replacement",
        "display_name": "Library Card Replacement",
        "description": "Fee for replacing lost or damaged library cards",
        "base_amount": 25.0,
        "supports_installments": False,
        "is_category_based": False,
    }

    # Example: Create a tutoring service with category-based pricing
    tutoring_item = {
        "name": "tutoring_service",
        "display_name": "One-on-One Tutoring",
        "description": "Personal tutoring sessions with library staff",
        "supports_installments": True,
        "max_installments": 6,
        "is_category_based": True,
        "category_prices": [
            {"category": "pupil", "amount": 300.0},
            {"category": "student", "amount": 500.0},
            {"category": "adult", "amount": 700.0},
        ],
    }

    return [card_replacement_item, tutoring_item]


# Quick test/demo script
if __name__ == "__main__":
    # Example usage
    DATABASE_URL = "sqlite:///library.db"  # Adjust for your database

    print("Setting up enhanced payment system...")
    success = setup_payment_system(DATABASE_URL)

    if success:
        print("\n🎯 Next steps:")
        print("1. Update your existing forms to use EnhancedAddPaymentForm")
        print("2. Run any necessary data migrations")
        print("3. Test the new payment item system")
        print("4. Add custom payment items as needed")
    else:
        print("\n❌ Setup failed. Check error messages above.")
