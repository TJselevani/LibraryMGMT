# Simplified payment form widget - No complex installments
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
    QListWidgetItem,
    QGridLayout,
    QTextEdit,
    QDoubleSpinBox,
    QGroupBox,
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS
from db.models import PaymentItem


class PatronSearchWidget(QFrame):
    """Custom widget for patron search with Material Design styling"""

    patron_selected = pyqtSignal(object)

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
                border-radius: 8px;
                padding: 12px;
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search patron...")
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
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
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        layout.addWidget(self.selected_label)

        # Search results
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(100)
        self.search_results.setStyleSheet(
            f"""
            QListWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                background-color: white;
                font-size: 12px;
            }}
            QListWidget::item {{
                padding: 8px 12px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                color: {COLORS.get('on_primary_container', '#1565C0')};
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

        if len(search_text) < 2:
            return

        for patron in self.all_patrons:
            searchable = f"{patron.first_name} {patron.last_name} {patron.patron_id} {patron.institution}".lower()
            if search_text in searchable:
                display_text = f"{patron.first_name} {patron.last_name}"
                detail_text = f"ID: {patron.patron_id} | {patron.institution}"
                item = QListWidgetItem(f"{display_text}\n{detail_text}")
                item.setData(Qt.UserRole, patron)
                self.search_results.addItem(item)

    def select_patron(self, item):
        """Handle patron selection"""
        self.selected_patron = item.data(Qt.UserRole)
        self.selected_label.setText(
            f"Selected: {self.selected_patron.first_name} {self.selected_patron.last_name} "
            f"(ID: {self.selected_patron.patron_id})"
        )
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                border: 1px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
        """
        )
        self.search_results.clear()
        self.search_input.clear()
        self.patron_selected.emit(self.selected_patron)


class AddPaymentForm(QWidget):
    """Simplified payment form for partial payments"""

    def __init__(
        self,
        payments_controller,
        patrons_controller,
        payment_items_controller,
        on_cancel,
        on_success,
    ):
        super().__init__()
        self.payments_controller = payments_controller
        self.patrons_controller = patrons_controller
        self.payment_items_controller = payment_items_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.selected_patron = None
        self.available_payment_items = []
        self.selected_payment_item: PaymentItem = None
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Set background
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
                padding: 16px;
            }}
        """
        )
        title_layout = QHBoxLayout(title_frame)

        title = QLabel("Add Payment")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {COLORS.get('on_primary', '#FFFFFF')};
            }}
        """
        )

        subtitle = QLabel("Make full or partial payments for library services")
        subtitle.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                opacity: 0.9;
            }}
        """
        )

        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(subtitle)
        main_layout.addWidget(title_frame)

        # Content area with 3 columns
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)

        # Column 1: Patron Selection
        patron_frame = self.create_patron_section()
        content_layout.addWidget(patron_frame)

        # Column 2: Payment Item Selection
        payment_item_frame = self.create_payment_item_section()
        content_layout.addWidget(payment_item_frame)

        # Column 3: Payment Details
        details_frame = self.create_payment_details_section()
        content_layout.addWidget(details_frame)

        main_layout.addWidget(content_frame)

        # Action buttons
        button_frame = self.create_button_section()
        main_layout.addWidget(button_frame)

    def create_patron_section(self):
        """Create patron selection section"""
        patron_frame = QFrame()
        patron_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        patron_layout = QVBoxLayout(patron_frame)

        patron_title = QLabel("Select Patron")
        patron_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
            }}
        """
        )
        patron_layout.addWidget(patron_title)

        self.patron_search = PatronSearchWidget()
        self.patron_search.patron_selected.connect(self.on_patron_selected)
        patron_layout.addWidget(self.patron_search)

        # Membership status display
        self.membership_status = QLabel("")
        self.membership_status.setWordWrap(True)
        self.membership_status.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {COLORS.get('on_surface_variant', '#666666')};
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border-radius: 4px;
                padding: 6px;
                margin-top: 8px;
            }}
        """
        )
        patron_layout.addWidget(self.membership_status)

        patron_layout.addStretch()
        return patron_frame

    def create_payment_item_section(self):
        """Create payment item selection section"""
        item_frame = QFrame()
        item_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('secondary', '#2E7D32')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        item_layout = QVBoxLayout(item_frame)

        item_title = QLabel("Select Service")
        item_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('secondary', '#2E7D32')};
                margin-bottom: 8px;
            }}
        """
        )
        item_layout.addWidget(item_title)

        # Payment item dropdown
        self.payment_item_combo = QComboBox()
        self.payment_item_combo.setStyleSheet(
            f"""
            QComboBox {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-height: 16px;
            }}
            QComboBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        item_layout.addWidget(self.payment_item_combo)

        # Service description
        self.service_description = QLabel(
            "Select a patron first to see available services"
        )
        self.service_description.setWordWrap(True)
        self.service_description.setStyleSheet(
            f"""
            QLabel {{
                font-size: 12px;
                color: {COLORS.get('on_surface_variant', '#666666')};
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border-radius: 4px;
                padding: 8px;
                margin-top: 8px;
            }}
        """
        )
        item_layout.addWidget(self.service_description)

        # Payment status for existing incomplete payments
        self.payment_status_label = QLabel("")
        self.payment_status_label.setWordWrap(True)
        self.payment_status_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {COLORS.get('error', '#D32F2F')};
                background-color: {COLORS.get('error_container', '#FFEBEE')};
                border-radius: 4px;
                padding: 6px;
                margin-top: 4px;
            }}
        """
        )
        self.payment_status_label.hide()
        item_layout.addWidget(self.payment_status_label)

        item_layout.addStretch()
        return item_frame

    def create_payment_details_section(self):
        """Create payment details section"""
        details_frame = QFrame()
        details_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('tertiary', '#7B1FA2')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        details_layout = QVBoxLayout(details_frame)

        details_title = QLabel("Payment Details")
        details_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('tertiary', '#7B1FA2')};
                margin-bottom: 8px;
            }}
        """
        )
        details_layout.addWidget(details_title)

        # Payment details grid
        details_grid = QGridLayout()
        details_grid.setSpacing(12)

        # Total amount display
        total_label = QLabel("Total Required (KSh)")
        total_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        details_grid.addWidget(total_label, 0, 0)

        self.total_amount_display = QLabel("0.00")
        self.total_amount_display.setStyleSheet(
            f"""
            QLabel {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        details_grid.addWidget(self.total_amount_display, 1, 0)

        # Already paid display (for existing payments)
        paid_label = QLabel("Already Paid (KSh)")
        paid_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        details_grid.addWidget(paid_label, 0, 1)

        self.paid_amount_display = QLabel("0.00")
        self.paid_amount_display.setStyleSheet(
            f"""
            QLabel {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                background-color: {COLORS.get('success_container', '#E8F5E8')};
                color: {COLORS.get('success', '#2E7D32')};
            }}
        """
        )
        details_grid.addWidget(self.paid_amount_display, 1, 1)

        details_layout.addLayout(details_grid)

        # Amount to pay input
        amount_section = QGroupBox("Payment Amount")
        amount_section.setStyleSheet(
            f"""
            QGroupBox {{
                font-size: 14px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 8px;
                padding-top: 12px;
                margin-top: 8px;
            }}
        """
        )
        amount_layout = QVBoxLayout(amount_section)

        # Amount input with validation
        amount_input_layout = QHBoxLayout()

        amount_label = QLabel("Amount (KSh):")
        amount_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        amount_input_layout.addWidget(amount_label)

        self.amount_input = QDoubleSpinBox()
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimum(0.01)
        self.amount_input.setMaximum(999999.99)
        self.amount_input.setStyleSheet(
            f"""
            QDoubleSpinBox {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                background-color: white;
            }}
            QDoubleSpinBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        self.amount_input.valueChanged.connect(self.validate_amount)
        amount_input_layout.addWidget(self.amount_input)

        # Quick amount buttons for full payment
        self.full_payment_btn = MaterialButton("Pay Remaining", button_type="outlined")
        self.full_payment_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                color: {COLORS.get('primary', '#1976D2')};
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('primary', '#1976D2')};
                color: white;
            }}
        """
        )
        self.full_payment_btn.clicked.connect(self.set_full_payment)
        self.full_payment_btn.hide()  # Initially hidden
        amount_input_layout.addWidget(self.full_payment_btn)

        amount_layout.addLayout(amount_input_layout)

        # Validation message
        self.amount_validation = QLabel("")
        self.amount_validation.setWordWrap(True)
        self.amount_validation.setStyleSheet(
            f"""
            QLabel {{
                font-size: 11px;
                color: {COLORS.get('error', '#D32F2F')};
                margin-top: 4px;
            }}
        """
        )
        amount_layout.addWidget(self.amount_validation)

        details_layout.addWidget(amount_section)

        # Payment date and method
        payment_info_layout = QHBoxLayout()

        # Payment date
        date_layout = QVBoxLayout()
        date_label = QLabel("Payment Date")
        date_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        date_layout.addWidget(date_label)

        self.payment_date = QDateEdit()
        self.payment_date.setCalendarPopup(True)
        self.payment_date.setDate(QDate.currentDate())
        self.payment_date.setStyleSheet(
            f"""
            QDateEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        date_layout.addWidget(self.payment_date)
        payment_info_layout.addLayout(date_layout)

        # Payment method
        method_layout = QVBoxLayout()
        method_label = QLabel("Payment Method")
        method_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        method_layout.addWidget(method_label)

        self.payment_method = QComboBox()
        self.payment_method.addItems(["Cash", "M-Pesa", "Bank Transfer", "Card"])
        self.payment_method.setStyleSheet(
            f"""
            QComboBox {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QComboBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        method_layout.addWidget(self.payment_method)
        payment_info_layout.addLayout(method_layout)

        details_layout.addLayout(payment_info_layout)

        # Reference number (optional)
        ref_label = QLabel("Reference Number (Optional)")
        ref_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
                margin-top: 8px;
            }}
        """
        )
        details_layout.addWidget(ref_label)

        self.reference_input = QLineEdit()
        self.reference_input.setPlaceholderText("Transaction ID, receipt number, etc.")
        self.reference_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        details_layout.addWidget(self.reference_input)

        # Notes section
        notes_label = QLabel("Notes (Optional)")
        notes_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
                margin-top: 8px;
            }}
        """
        )
        details_layout.addWidget(notes_label)

        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("Additional notes about this payment...")
        self.notes_input.setStyleSheet(
            f"""
            QTextEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px;
                font-size: 12px;
                background-color: white;
            }}
            QTextEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        details_layout.addWidget(self.notes_input)

        details_layout.addStretch()
        return details_frame

    def create_button_section(self):
        """Create action buttons section"""
        button_frame = QFrame()
        button_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border-top: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                margin-top: 8px;
            }}
        """
        )
        button_layout = QHBoxLayout(button_frame)
        button_layout.addStretch()

        # Cancel button
        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        cancel_btn.clicked.connect(self.on_cancel)

        # Save button
        save_btn = MaterialButton("Record Payment", button_type="elevated")
        save_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.get('primary', '#1976D2')};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('primary_variant', '#1565C0')};
            }}
        """
        )
        save_btn.clicked.connect(self.save_payment)

        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)

        return button_frame

    def load_data(self):
        """Load patrons and payment items"""
        try:
            # Load patrons
            all_patrons = self.patrons_controller.get_all()
            self.patron_search.load_patrons(all_patrons)

            # Initialize payment item combo
            self.payment_item_combo.addItem("Select a patron first...", None)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def on_patron_selected(self, patron):
        """Handle patron selection and load available payment items"""
        self.selected_patron = patron

        # Update membership status display
        if patron.is_membership_active():
            days_remaining = patron.get_membership_days_remaining()
            self.membership_status.setText(
                f"Membership: {patron.membership_status.value.title()} "
                f"({patron.membership_type}) - {days_remaining} days remaining"
            )
            self.membership_status.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 11px;
                    color: {COLORS.get('success', '#2E7D32')};
                    background-color: {COLORS.get('success_container', '#E8F5E8')};
                    border-radius: 4px;
                    padding: 6px;
                    margin-top: 8px;
                }}
            """
            )
        else:
            self.membership_status.setText(
                f"Membership: {patron.membership_status.value.title()}"
            )
            self.membership_status.setStyleSheet(
                f"""
                QLabel {{
                    font-size: 11px;
                    color: {COLORS.get('warning', '#F57C00')};
                    background-color: {COLORS.get('warning_container', '#FFF3E0')};
                    border-radius: 4px;
                    padding: 6px;
                    margin-top: 8px;
                }}
            """
            )

        try:
            # Get available payment items for this patron
            result = self.payment_items_controller.get_payment_items_for_patron(patron)
            self.available_payment_items = result
            self.update_payment_item_combo(result)
        except Exception as e:
            QMessageBox.warning(
                self, "Error", f"Could not load payment items: {str(e)}"
            )

    def update_payment_item_combo(self, payment_items):
        """Update payment item combobox"""
        # Disconnect signal to prevent recursion
        try:
            self.payment_item_combo.currentIndexChanged.disconnect()
        except Exception as e:
            print(e)
            pass

        self.payment_item_combo.clear()
        self.payment_item_combo.addItem("Select a service...", None)

        for item_data in payment_items:
            display_text = item_data["formatted_display"]

            # Add indicator for installment support
            if item_data["supports_installments"]:
                display_text += " (Partial payments allowed)"

            self.payment_item_combo.addItem(display_text, item_data)

        # Reconnect signal
        self.payment_item_combo.currentIndexChanged.connect(
            self.on_payment_item_selected
        )

    def on_payment_item_selected(self):
        """Handle payment item selection"""
        current_data = self.payment_item_combo.currentData()
        if not current_data:
            self.selected_payment_item = None
            self.reset_payment_details()
            return

        self.selected_payment_item = current_data
        item = current_data["item"]

        # Update displays
        self.total_amount_display.setText(f"{current_data['total_amount']:.2f}")

        # Show existing payment info if applicable
        if current_data["has_incomplete_payment"]:
            existing_payment = current_data["existing_payment"]
            paid_amount = existing_payment.amount_paid
            remaining = existing_payment.get_remaining_amount()

            self.paid_amount_display.setText(f"{paid_amount:.2f}")
            self.payment_status_label.setText(
                f"Existing payment found: KSh {paid_amount:.2f} already paid. "
                f"Remaining: KSh {remaining:.2f}"
            )
            self.payment_status_label.show()

            # Set max amount to remaining amount
            self.amount_input.setMaximum(remaining)
            self.full_payment_btn.setText(f"Pay Remaining (KSh {remaining:.2f})")
            self.full_payment_btn.show()

        else:
            self.paid_amount_display.setText("0.00")
            self.payment_status_label.hide()
            self.amount_input.setMaximum(current_data["total_amount"])
            self.full_payment_btn.setText("Pay Full Amount")

            # Only show full payment button if installments are supported
            if item.supports_installments:
                self.full_payment_btn.show()
            else:
                self.full_payment_btn.hide()
                # For non-installment items, set amount to full amount
                self.amount_input.setValue(current_data["amount"])

        # Update description
        description = item.description or "No description available"
        if item.is_membership:
            description += f" (Duration: {item.membership_duration_months} months)"
        self.service_description.setText(description)

    def set_full_payment(self):
        """Set amount to remaining/full payment amount"""
        if self.selected_payment_item:
            self.amount_input.setValue(self.selected_payment_item["amount"])

    def validate_amount(self):
        """Validate payment amount"""
        if not self.selected_payment_item:
            return

        amount = self.amount_input.value()
        max_amount = self.selected_payment_item["amount"]

        if amount <= 0:
            self.amount_validation.setText("Amount must be greater than 0")
            self.amount_validation.setStyleSheet(
                f"QLabel {{ color: {COLORS.get('error', '#D32F2F')}; font-size: 11px; }}"
            )
        elif amount > max_amount:
            self.amount_validation.setText(f"Amount cannot exceed KSh {max_amount:.2f}")
            self.amount_validation.setStyleSheet(
                f"QLabel {{ color: {COLORS.get('error', '#D32F2F')}; font-size: 11px; }}"
            )
        else:
            # Check if partial payment is allowed
            item = self.selected_payment_item["item"]
            if not item.supports_installments and amount < max_amount:
                self.amount_validation.setText(
                    f"{item.display_name} requires full payment of KSh {max_amount:.2f}"
                )
                self.amount_validation.setStyleSheet(
                    f"QLabel {{ color: {COLORS.get('warning', '#F57C00')}; font-size: 11px; }}"
                )
            else:
                self.amount_validation.setText("")

    def reset_payment_details(self):
        """Reset payment details section"""
        self.total_amount_display.setText("0.00")
        self.paid_amount_display.setText("0.00")
        self.amount_input.setValue(0.00)
        self.amount_input.setMaximum(999999.99)
        self.payment_status_label.hide()
        self.full_payment_btn.hide()
        self.service_description.setText("Select a service...")
        self.amount_validation.setText("")

    def validate_form(self):
        """Validate form before submission"""
        errors = []

        if not self.selected_patron:
            errors.append("Please select a patron")

        if not self.selected_payment_item:
            errors.append("Please select a payment service")
        else:
            amount = self.amount_input.value()
            max_amount = self.selected_payment_item["amount"]
            item = self.selected_payment_item["item"]

            if amount <= 0:
                errors.append("Payment amount must be greater than 0")
            elif amount > max_amount:
                errors.append(f"Payment amount cannot exceed KSh {max_amount:.2f}")
            elif not item.supports_installments and amount < max_amount:
                errors.append(f"{item.display_name} requires full payment")

        return errors

    def save_payment(self):
        """Save payment with validation"""
        # Validate form
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Prepare payment data
        payment_data = {
            "user_id": self.selected_patron.user_id,
            "payment_item_name": self.selected_payment_item["item"].name,
            "payment_item_id": self.selected_payment_item["item"].id,
            "amount": self.amount_input.value(),
            "payment_date": self.payment_date.date().toString("yyyy-MM-dd"),
            "payment_method": self.payment_method.currentText().lower(),
            "reference_number": self.reference_input.text().strip() or None,
            "notes": self.notes_input.toPlainText().strip() or None,
        }

        # Save through controller
        try:
            result = self.payments_controller.create(payment_data)
            if result.get("success", False):
                # Show success message with details
                message = result.get("message", "Payment saved successfully!")
                if result.get("remaining", 0) > 0:
                    message += f"\n\nRemaining balance: KSh {result['remaining']:.2f}"

                QMessageBox.information(self, "Success", message)
                self.reset_form()
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
        self.selected_payment_item = None
        self.available_payment_items = []

        # Reset patron search
        self.patron_search.selected_patron = None
        self.patron_search.selected_label.setText("No patron selected")
        self.patron_search.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px;
                font-weight: 500;
                font-size: 12px;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        self.patron_search.search_input.clear()
        self.patron_search.search_results.clear()
        self.membership_status.setText("")

        # Reset payment item selection
        try:
            self.payment_item_combo.currentIndexChanged.disconnect()
        except Exception as e:
            print(e)
            pass
        self.payment_item_combo.clear()
        self.payment_item_combo.addItem("Select a patron first...", None)
        self.service_description.setText(
            "Select a patron first to see available services"
        )

        # Reset payment details
        self.reset_payment_details()
        self.payment_date.setDate(QDate.currentDate())
        self.payment_method.setCurrentIndex(0)
        self.reference_input.clear()
        self.notes_input.clear()
