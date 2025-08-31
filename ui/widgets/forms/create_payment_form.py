from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QListWidget,
    QMessageBox,
    QFrame,
    QScrollArea,
    QListWidgetItem,
    QSizePolicy,
    QSpacerItem,
    QGroupBox,
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
# from PyQt5.QtGui import QFont, QPalette
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


class PatronSearchWidget(QFrame):
    """Custom widget for patron search with Material Design styling"""

    patron_selected = pyqtSignal(object)  # Emits selected patron object

    def __init__(self):
        super().__init__()
        self.all_patrons = []
        self.selected_patron = None
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface', '#FFFFFF')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search patron by name or ID...")
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: white;
            }}
        """
        )
        layout.addWidget(self.search_input)

        # Selected patron display
        self.selected_label = QLabel("No patron selected")
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px;
                font-weight: 500;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        layout.addWidget(self.selected_label)

        # Search results
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(200)
        self.search_results.setStyleSheet(
            f"""
            QListWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                background-color: white;
                alternate-background-color: {COLORS.get('surface_variant', '#F8F8F8')};
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
        """
        )
        layout.addWidget(self.search_results)

        # Connect signals
        self.search_input.textChanged.connect(self.filter_patrons)
        self.search_results.itemClicked.connect(self.select_patron)

    def load_patrons(self, patrons):
        """Load patrons list"""
        self.all_patrons = patrons
        self.update_search_results()

    def filter_patrons(self):
        """Filter patrons based on search text"""
        self.update_search_results()

    def update_search_results(self):
        """Update the search results list"""
        search_text = self.search_input.text().lower()
        self.search_results.clear()

        if (
            len(search_text) < 2
        ):  # Only show results when user types at least 2 characters
            return

        for patron in self.all_patrons:
            # Create searchable text
            searchable = f"{patron.first_name} {patron.last_name} {patron.patron_id} {patron.institution}".lower()

            if search_text in searchable:
                display_text = f"{patron.first_name} {patron.last_name}"
                detail_text = f"ID: {patron.patron_id} | {patron.institution} | {patron.grade_level}"

                item = QListWidgetItem(f"{display_text}\n{detail_text}")
                item.setData(Qt.UserRole, patron)  # Store patron object
                self.search_results.addItem(item)

    def select_patron(self, item):
        """Handle patron selection"""
        self.selected_patron = item.data(Qt.UserRole)
        self.selected_label.setText(
            f"✓ Selected: {self.selected_patron.first_name} {self.selected_patron.last_name} "
            f"(ID: {self.selected_patron.patron_id})"
        )
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                border: 1px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 8px;
                padding: 12px;
                font-weight: 500;
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
        """
        )
        self.search_results.clear()  # Hide results after selection
        self.search_input.clear()
        self.patron_selected.emit(self.selected_patron)


class InstallmentWidget(QFrame):
    """Widget for a single installment entry"""

    def __init__(self, installment_number):
        super().__init__()
        self.installment_number = installment_number
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface_variant', '#F8F8F8')};
                border: 1px solid {COLORS.get('outline_variant', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px;
                margin: 4px 0;
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setSpacing(12)

        # Installment label
        label = QLabel(f"Installment {self.installment_number}")
        label.setStyleSheet(
            f"""
            QLabel {{
                font-weight: 600;
                color: {COLORS.get('on_surface', '#000000')};
                min-width: 100px;
            }}
        """
        )
        layout.addWidget(label)

        # Amount input
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        layout.addWidget(self.amount_input)

        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setStyleSheet(
            f"""
            QDateEdit {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                background-color: white;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        layout.addWidget(self.date_input)

    def get_data(self):
        """Get installment data"""
        try:
            return {
                "installment_number": self.installment_number,
                "amount": float(self.amount_input.text()),
                "date": self.date_input.date().toString("yyyy-MM-dd"),
            }
        except ValueError:
            return None


class AddPaymentForm(QWidget):
    # Payment configurations
    PAYMENT_CONFIGS = {
        "access": {"amount": 20, "description": "Daily Access Fee"},
        "study_room": {"amount": 150, "description": "Study Room Access"},
        "membership": {
            "description": "Annual Membership",
            "installments_allowed": True,
        },
    }

    MEMBERSHIP_FEES = {"pupil": 200, "student": 450, "adult": 600}

    def __init__(self, payments_controller, patrons_controller, on_cancel, on_success):
        super().__init__()
        self.payments_controller = payments_controller
        self.patrons_controller = patrons_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.selected_patron = None
        self.installment_widgets = []
        self.setup_ui()
        self.load_patrons()

    def setup_ui(self):
        # Main layout with padding
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(32, 32, 32, 32)

        # Set widget background
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {COLORS.get('surface', '#FAFAFA')};
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )

        # Title section
        title_frame = QFrame()
        title_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('primary', '#1976D2')};
                border-radius: 12px;
                padding: 24px;
            }}
        """
        )
        title_layout = QVBoxLayout(title_frame)

        title = QLabel("💳 Add Payment")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 32px;
                font-weight: 700;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                margin: 0;
            }}
        """
        )

        subtitle = QLabel("Create a new payment record for library services")
        subtitle.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                margin-top: 8px;
                opacity: 0.9;
            }}
        """
        )

        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        main_layout.addWidget(title_frame)

        # Content area with scroll
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")

        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(24)

        # Patron selection section
        patron_group = QGroupBox("👤 Select Patron")
        patron_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 18px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: {COLORS.get('surface', '#FAFAFA')};
            }}
        """
        )
        patron_layout = QVBoxLayout(patron_group)

        self.patron_search = PatronSearchWidget()
        self.patron_search.patron_selected.connect(self.on_patron_selected)
        patron_layout.addWidget(self.patron_search)
        content_layout.addWidget(patron_group)

        # Payment details section
        payment_group = QGroupBox("💰 Payment Details")
        payment_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 18px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: {COLORS.get('surface', '#FAFAFA')};
            }}
        """
        )
        payment_layout = QVBoxLayout(payment_group)
        payment_layout.setSpacing(16)

        # Payment type selection
        type_layout = QVBoxLayout()
        type_label = QLabel("Payment Type")
        type_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
                margin-bottom: 4px;
            }}
        """
        )
        type_layout.addWidget(type_label)

        self.payment_type = QComboBox()
        self.payment_type.addItems(
            [
                "access - Daily Access Fee (KSh 20)",
                "study_room - Study Room Access (KSh 150)",
                "membership - Annual Membership (Variable)",
            ]
        )
        self.payment_type.setStyleSheet(
            f"""
            QComboBox {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }}
            QComboBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 30px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS.get('on_surface', '#000000')};
                margin-right: 10px;
            }}
        """
        )
        type_layout.addWidget(self.payment_type)
        payment_layout.addLayout(type_layout)

        # Amount and date in a row
        amount_date_layout = QHBoxLayout()
        amount_date_layout.setSpacing(16)

        # Amount
        amount_col = QVBoxLayout()
        amount_label = QLabel("Amount (KSh)")
        amount_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
                margin-bottom: 4px;
            }}
        """
        )
        amount_col.addWidget(amount_label)

        self.amount = QLineEdit()
        self.amount.setPlaceholderText("0.00")
        self.amount.setReadOnly(True)  # Auto-calculated
        self.amount.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                font-weight: 600;
            }}
        """
        )
        amount_col.addWidget(self.amount)
        amount_date_layout.addLayout(amount_col)

        # Payment date
        date_col = QVBoxLayout()
        date_label = QLabel("Payment Date")
        date_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
                margin-bottom: 4px;
            }}
        """
        )
        date_col.addWidget(date_label)

        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setStyleSheet(
            f"""
            QDateEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: white;
                min-height: 20px;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        date_col.addWidget(self.payment_date)
        amount_date_layout.addLayout(date_col)

        payment_layout.addLayout(amount_date_layout)
        content_layout.addWidget(payment_group)

        # Installments section (initially hidden)
        self.installments_group = QGroupBox("📅 Payment Installments")
        self.installments_group.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 18px;
                font-weight: 600;
                color: {COLORS.get('secondary', '#7B1FA2')};
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 12px;
                margin-top: 12px;
                padding-top: 16px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 16px;
                padding: 0 8px;
                background-color: {COLORS.get('surface', '#FAFAFA')};
            }}
        """
        )
        self.installments_layout = QVBoxLayout(self.installments_group)
        self.installments_group.hide()  # Initially hidden
        content_layout.addWidget(self.installments_group)

        # Spacer
        content_layout.addSpacerItem(
            QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)

        # Action buttons
        button_frame = QFrame()
        button_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border-top: 1px solid {COLORS.get('outline', '#E0E0E0')};
                padding: 16px 0;
            }}
        """
        )
        button_layout = QHBoxLayout(button_frame)
        button_layout.addSpacerItem(
            QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        save_btn = MaterialButton("💾 Save Payment", button_type="elevated")
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.get('primary', '#1976D2')};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                min-width: 140px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('primary_variant', '#1565C0')};
            }}
        """
        )

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        main_layout.addWidget(button_frame)

        # Connect signals
        cancel_btn.clicked.connect(self.on_cancel)
        save_btn.clicked.connect(self.save_payment)
        self.payment_type.currentTextChanged.connect(self.update_payment_details)

    def load_patrons(self):
        """Load all patrons from the database"""
        try:
            self.all_patrons = self.patrons_controller.get_all()
            self.patron_search.load_patrons(self.all_patrons)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load patrons: {str(e)}")

    def on_patron_selected(self, patron):
        """Handle patron selection"""
        self.selected_patron = patron
        self.update_payment_details()  # Update amounts based on patron

    def update_payment_details(self):
        """Update payment amount and installments based on type and patron"""
        payment_type_text = self.payment_type.currentText()
        payment_type = payment_type_text.split(" - ")[
            0
        ]  # Extract type from display text

        # Clear existing installments
        self.clear_installments()

        if payment_type == "access":
            self.amount.setText("20.00")
            self.installments_group.hide()

        elif payment_type == "study_room":
            self.amount.setText("150.00")
            self.installments_group.hide()

        elif payment_type == "membership":
            if self.selected_patron:
                grade_level = self.selected_patron.grade_level.lower()
                amount = self.MEMBERSHIP_FEES.get(grade_level, 450)
                self.amount.setText(f"{amount:.2f}")

                # Show installments
                self.installments_group.show()
                self.create_installment_widgets(amount)
            else:
                self.amount.setText("0.00")
                self.installments_group.hide()

    def create_installment_widgets(self, total_amount):
        """Create installment input widgets"""
        self.installment_widgets = []

        # Calculate default installment amounts (equal parts)
        installment_amount = total_amount / 3

        for i in range(1, 4):
            widget = InstallmentWidget(i)
            widget.amount_input.setText(f"{installment_amount:.2f}")
            # Set default dates (monthly intervals)
            date = QDate.currentDate().addMonths(i - 1)
            widget.date_input.setDate(date)

            self.installments_layout.addWidget(widget)
            self.installment_widgets.append(widget)

    def clear_installments(self):
        """Remove all installment widgets"""
        for widget in self.installment_widgets:
            self.installments_layout.removeWidget(widget)
            widget.deleteLater()
        self.installment_widgets = []

    def validate_form(self):
        """Validate form data before saving"""
        errors = []

        if not self.selected_patron:
            errors.append("Please select a patron")

        try:
            amount = float(self.amount.text())
            if amount <= 0:
                errors.append("Amount must be greater than 0")
        except ValueError:
            errors.append("Invalid amount format")

        # Validate installments if membership
        payment_type = self.payment_type.currentText().split(" - ")[0]
        if payment_type == "membership" and self.installment_widgets:
            total_installments = 0
            for widget in self.installment_widgets:
                data = widget.get_data()
                if data is None:
                    errors.append(
                        f"Invalid installment {widget.installment_number} amount"
                    )
                else:
                    total_installments += data["amount"]

            # Check if installments sum matches total
            try:
                total_amount = float(self.amount.text())
                if (
                    abs(total_installments - total_amount) > 0.01
                ):  # Allow small rounding differences
                    errors.append(
                        f"Installments total ({total_installments:.2f}) doesn't match payment amount ({total_amount:.2f})"
                    )
            except ValueError:
                pass  # Already handled above

        return errors

    def save_payment(self):
        """Save payment with validation"""
        # Validate form
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Prepare payment data
        payment_type = self.payment_type.currentText().split(" - ")[0]

        payment_data = {
            "user_id": self.selected_patron.user_id,
            "payment_type": payment_type,
            "amount": float(self.amount.text()),
            "payment_date": self.payment_date.date().toString("yyyy-MM-dd"),
        }

        # Add installments for membership
        if payment_type == "membership" and self.installment_widgets:
            installments = []
            for widget in self.installment_widgets:
                data = widget.get_data()
                if data:
                    installments.append(data)
            payment_data["installments"] = installments

        # Save through controller
        try:
            result = self.payments_controller.create(payment_data)
            if result.get("success", False):
                QMessageBox.information(
                    self,
                    "Success",
                    f"Payment of KSh {payment_data['amount']:.2f} saved successfully!",
                )
                self.on_success()
            else:
                QMessageBox.warning(
                    self, "Error", result.get("message", "Failed to save payment")
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def reset_form(self):
        """Reset form to initial state"""
        self.selected_patron = None
        self.patron_search.selected_patron = None
        self.patron_search.selected_label.setText("No patron selected")
        self.patron_search.search_input.clear()
        self.patron_search.search_results.clear()
        self.payment_type.setCurrentIndex(0)
        self.amount.clear()
        self.payment_date.setDate(QDate.currentDate())
        self.clear_installments()
        self.installments_group.hide()
