# Enhanced payment form widget
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
    QGridLayout,
    QTextEdit,
    QCheckBox,
    QSpinBox,
    QDoubleSpinBox,
)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS


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


class InstallmentWidget(QFrame):
    """Enhanced widget for installment entry with validation"""

    def __init__(self, installment_number, max_amount=None):
        super().__init__()
        self.installment_number = installment_number
        self.max_amount = max_amount
        self.setup_ui()

    def setup_ui(self):
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface_variant', '#F8F8F8')};
                border: 1px solid {COLORS.get('outline_variant', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px;
                margin: 2px 0;
            }}
        """
        )

        layout = QHBoxLayout(self)
        layout.setSpacing(8)

        # Installment label
        label = QLabel(f"#{self.installment_number}")
        label.setStyleSheet(
            f"""
            QLabel {{
                font-weight: 600;
                color: {COLORS.get('on_surface', '#000000')};
                min-width: 30px;
                font-size: 12px;
            }}
        """
        )
        layout.addWidget(label)

        # Amount input with validation
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setDecimals(2)
        self.amount_input.setMinimum(0.01)
        if self.max_amount:
            self.amount_input.setMaximum(self.max_amount)
        else:
            self.amount_input.setMaximum(999999.99)
        self.amount_input.setStyleSheet(
            f"""
            QDoubleSpinBox {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 4px;
                padding: 6px 8px;
                background-color: white;
                font-size: 12px;
            }}
            QDoubleSpinBox:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        layout.addWidget(self.amount_input)

        # Date input
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumDate(QDate.currentDate())  # Prevent past dates
        self.date_input.setStyleSheet(
            f"""
            QDateEdit {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 4px;
                padding: 6px 8px;
                background-color: white;
                font-size: 12px;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        layout.addWidget(self.date_input)

    def get_data(self):
        """Get installment data with validation"""
        try:
            amount = self.amount_input.value()
            if amount <= 0:
                return None

            return {
                "installment_number": self.installment_number,
                "amount": amount,
                "date": self.date_input.date().toString("yyyy-MM-dd"),
            }
        except Exception:
            return None

    def set_amount(self, amount):
        """Set the amount value"""
        self.amount_input.setValue(amount)

    def set_due_date(self, date_obj):
        """Set the due date"""
        if isinstance(date_obj, QDate):
            self.date_input.setDate(date_obj)
        else:
            self.date_input.setDate(QDate.fromString(date_obj, "yyyy-MM-dd"))


class AddPaymentForm(QWidget):
    """Enhanced payment form that works with flexible payment items"""

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
        self.selected_payment_item = None
        self.installment_widgets = []
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

        subtitle = QLabel("Create a new payment record for library services")
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

        # Column 3: Payment Details & Installments
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

        # Installment options
        self.installment_checkbox = QCheckBox("Pay in installments")
        self.installment_checkbox.setStyleSheet(
            f"""
            QCheckBox {{
                font-size: 13px;
                font-weight: 500;
                spacing: 8px;
            }}
            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 3px;
                background-color: white;
            }}
            QCheckBox::indicator:checked {{
                background-color: {COLORS.get('primary', '#1976D2')};
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        self.installment_checkbox.stateChanged.connect(self.toggle_installments)
        item_layout.addWidget(self.installment_checkbox)

        item_layout.addStretch()
        return item_frame

    def create_payment_details_section(self):
        """Create payment details and installments section"""
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

        # Amount display
        amount_label = QLabel("Total Amount (KSh)")
        amount_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        details_grid.addWidget(amount_label, 0, 0)

        self.amount_display = QLabel("0.00")
        self.amount_display.setStyleSheet(
            f"""
            QLabel {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        details_grid.addWidget(self.amount_display, 1, 0)

        # Payment date
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
        details_grid.addWidget(date_label, 0, 1)

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
        details_grid.addWidget(self.payment_date, 1, 1)

        details_layout.addLayout(details_grid)

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
        self.notes_input.setPlaceholderText("Add any additional notes...")
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

        # Installments section
        self.installments_section = QFrame()
        installments_layout = QVBoxLayout(self.installments_section)

        installments_title = QLabel("Installment Schedule")
        installments_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {COLORS.get('tertiary', '#7B1FA2')};
                margin: 8px 0;
            }}
        """
        )
        installments_layout.addWidget(installments_title)

        # Number of installments spinner
        installments_controls = QHBoxLayout()

        installments_label = QLabel("Number of installments:")
        installments_label.setStyleSheet("font-size: 12px; font-weight: 500;")
        installments_controls.addWidget(installments_label)

        self.installments_count = QSpinBox()
        self.installments_count.setMinimum(2)
        self.installments_count.setMaximum(12)  # Will be updated based on payment item
        self.installments_count.setValue(3)
        self.installments_count.valueChanged.connect(self.update_installment_widgets)
        installments_controls.addWidget(self.installments_count)
        installments_controls.addStretch()

        installments_layout.addLayout(installments_controls)

        # Scrollable installments area
        installments_scroll = QScrollArea()
        installments_scroll.setWidgetResizable(True)
        installments_scroll.setMaximumHeight(200)
        installments_scroll.setStyleSheet("QScrollArea { border: none; }")

        self.installments_widget = QWidget()
        self.installments_layout = QVBoxLayout(self.installments_widget)
        self.installments_layout.setSpacing(4)

        installments_scroll.setWidget(self.installments_widget)
        installments_layout.addWidget(installments_scroll)

        self.installments_section.hide()  # Initially hidden
        details_layout.addWidget(self.installments_section)

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
        save_btn = MaterialButton("Save Payment", button_type="elevated")
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

            # Load payment items for initial display
            all_payment_items = self.payment_items_controller.get_all_active_items()
            self.update_payment_item_combo([])  # Empty until patron selected

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def on_patron_selected(self, patron):
        """Handle patron selection and load available payment items"""
        self.selected_patron = patron
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
        self.payment_item_combo.clear()
        self.payment_item_combo.addItem("Select a service...", None)

        for item_data in payment_items:
            display_text = item_data["formatted_display"]
            if item_data["supports_installments"]:
                display_text += " (Installments available)"

            self.payment_item_combo.addItem(display_text, item_data)

        # Connect signal after adding items
        self.payment_item_combo.currentIndexChanged.connect(
            self.on_payment_item_selected
        )

    def on_payment_item_selected(self):
        """Handle payment item selection"""
        current_data = self.payment_item_combo.currentData()
        if not current_data:
            self.selected_payment_item = None
            self.amount_display.setText("0.00")
            self.service_description.setText("Select a service...")
            self.installment_checkbox.hide()
            self.installments_section.hide()
            return

        self.selected_payment_item = current_data
        item = current_data["item"]
        amount = current_data["amount"]

        # Update amount display
        self.amount_display.setText(f"{amount:.2f}")

        # Update description
        description = item.description or "No description available"
        self.service_description.setText(description)

        # Show/hide installment option
        if item.supports_installments:
            self.installment_checkbox.show()
            self.installments_count.setMaximum(item.max_installments)
            self.installment_checkbox.setText(
                f"Pay in installments (max {item.max_installments})"
            )
        else:
            self.installment_checkbox.hide()
            self.installment_checkbox.setChecked(False)
            self.installments_section.hide()

    def toggle_installments(self, checked):
        """Toggle installment section visibility"""
        if checked and self.selected_payment_item:
            self.installments_section.show()
            self.update_installment_widgets()
        else:
            self.installments_section.hide()
            self.clear_installments()

    def update_installment_widgets(self):
        """Create/update installment widgets based on count"""
        if not self.selected_payment_item:
            return

        self.clear_installments()

        count = self.installments_count.value()
        total_amount = self.selected_payment_item["amount"]
        installment_amount = total_amount / count

        for i in range(1, count + 1):
            widget = InstallmentWidget(i, total_amount)
            widget.set_amount(installment_amount)

            # Set default due dates (monthly intervals)
            due_date = QDate.currentDate().addMonths(i - 1)
            widget.set_due_date(due_date)

            self.installments_layout.addWidget(widget)
            self.installment_widgets.append(widget)

    def clear_installments(self):
        """Remove all installment widgets"""
        for widget in self.installment_widgets:
            self.installments_layout.removeWidget(widget)
            widget.deleteLater()
        self.installment_widgets = []

    def validate_form(self):
        """Enhanced form validation"""
        errors = []

        if not self.selected_patron:
            errors.append("Please select a patron")

        if not self.selected_payment_item:
            errors.append("Please select a payment service")

        # Validate installments if enabled
        if self.installment_checkbox.isChecked() and self.installment_widgets:
            total_installments = 0
            installment_dates = []

            for widget in self.installment_widgets:
                data = widget.get_data()
                if data is None:
                    errors.append(
                        f"Invalid installment #{widget.installment_number} amount"
                    )
                else:
                    total_installments += data["amount"]
                    installment_dates.append(data["date"])

            # Check if installments sum matches total
            expected_total = self.selected_payment_item["amount"]
            if abs(total_installments - expected_total) > 0.01:
                errors.append(
                    f"Installments total ({total_installments:.2f}) must equal "
                    f"service amount ({expected_total:.2f})"
                )

            # Check for duplicate dates
            if len(installment_dates) != len(set(installment_dates)):
                errors.append("Installment due dates must be unique")

            # Check date ordering
            sorted_dates = sorted(installment_dates)
            if installment_dates != sorted_dates:
                errors.append("Installment due dates should be in chronological order")

        return errors

    def save_payment(self):
        """Save payment with enhanced validation"""
        # Validate form
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(self, "Validation Error", "\n".join(errors))
            return

        # Prepare payment data
        payment_data = {
            "user_id": self.selected_patron.user_id,
            "payment_item_name": self.selected_payment_item["item"].name,
            "payment_date": self.payment_date.date().toString("yyyy-MM-dd"),
            "notes": self.notes_input.toPlainText().strip() or None,
        }

        # Handle installments vs full payment
        if self.installment_checkbox.isChecked() and self.installment_widgets:
            installments = []
            for widget in self.installment_widgets:
                data = widget.get_data()
                if data:
                    installments.append(data)
            payment_data["installments"] = installments
            payment_data["amount"] = sum(inst["amount"] for inst in installments)
        else:
            payment_data["amount"] = self.selected_payment_item["amount"]

        # Save through controller
        try:
            result = self.payments_controller.create(payment_data)
            if result.get("success", False):
                QMessageBox.information(
                    self,
                    "Success",
                    result.get("message", "Payment saved successfully!"),
                )
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
        self.patron_search.search_input.clear()
        self.patron_search.search_results.clear()

        # Reset payment item selection
        self.payment_item_combo.clear()
        self.payment_item_combo.addItem("Select a patron first...", None)
        self.service_description.setText(
            "Select a patron first to see available services"
        )

        # Reset payment details
        self.amount_display.setText("0.00")
        self.payment_date.setDate(QDate.currentDate())
        self.notes_input.clear()

        # Reset installments
        self.installment_checkbox.setChecked(False)
        self.installment_checkbox.hide()
        self.installments_section.hide()
        self.clear_installments()


# Additional utility widget for managing payment items
class PaymentItemManagerWidget(QWidget):
    """Widget for administrators to manage payment items"""

    def __init__(self, payment_items_controller):
        super().__init__()
        self.payment_items_controller = payment_items_controller
        self.setup_ui()
        self.load_payment_items()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title = QLabel("Payment Items Management")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 20px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 16px;
            }}
        """
        )
        layout.addWidget(title)

        # Add new item button
        add_btn = MaterialButton("Add New Payment Item", button_type="elevated")
        add_btn.clicked.connect(self.show_add_item_dialog)
        layout.addWidget(add_btn)

        # Payment items list
        self.items_list = QListWidget()
        self.items_list.setStyleSheet(
            f"""
            QListWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 12px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
        """
        )
        layout.addWidget(self.items_list)

    def load_payment_items(self):
        """Load and display payment items"""
        try:
            items = self.payment_items_controller.get_all_active_items()
            self.items_list.clear()

            for item in items:
                if item.is_category_based:
                    # Show category prices
                    prices_text = ", ".join(
                        [
                            f"{price.category.value}: KSh {price.amount:.2f}"
                            for price in item.category_prices
                        ]
                    )
                    display_text = f"{item.display_name}\n{prices_text}"
                else:
                    display_text = f"{item.display_name}\nKSh {item.base_amount:.2f}"

                if item.supports_installments:
                    display_text += f" (Max {item.max_installments} installments)"

                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.UserRole, item)
                self.items_list.addItem(list_item)

        except Exception as e:
            QMessageBox.critical(
                self, "Error", f"Failed to load payment items: {str(e)}"
            )

    def show_add_item_dialog(self):
        """Show dialog for adding new payment item"""
        # This would open a separate dialog for creating payment items
        # Implementation depends on your UI framework preferences
        QMessageBox.information(
            self,
            "Add Payment Item",
            "This would open a dialog to add new payment items.\n"
            "You can implement this as a separate dialog window with fields for:\n"
            "- Name and display name\n"
            "- Description\n"
            "- Base amount or category-based pricing\n"
            "- Installment settings",
        )
