from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QMessageBox,
    QFrame,
    QGridLayout,
)
from PyQt5.QtCore import QDate
from ui.widgets.buttons.material_button import MaterialButton
from utils.constants import COLORS
from datetime import datetime
from db.models import Category


class AddPatronForm(QWidget):
    def __init__(self, patrons_controller, on_cancel, on_success):
        super().__init__()
        self.patrons_controller = patrons_controller
        self.on_cancel = on_cancel
        self.on_success = on_success
        self.setup_ui()

    def setup_ui(self):
        # Main layout with padding
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(24, 24, 24, 24)

        # Set widget background
        self.setStyleSheet(
            f"""
            QWidget {{
                background-color: {COLORS.get('surface', '#FAFAFA')};
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )

        # Title section - compact horizontal layout
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

        title = QLabel("👤 Add New Patron")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 24px;
                font-weight: 700;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                margin: 0;
            }}
        """
        )

        subtitle = QLabel("Create a new library patron account")
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

        # Main content area - 3 column layout
        content_frame = QFrame()
        content_layout = QHBoxLayout(content_frame)
        content_layout.setSpacing(20)

        # Left Column - Personal Information
        personal_frame = QFrame()
        personal_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('primary', '#1976D2')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        personal_layout = QVBoxLayout(personal_frame)
        personal_layout.setSpacing(12)

        personal_title = QLabel("📝 Personal Information")
        personal_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
            }}
        """
        )
        personal_layout.addWidget(personal_title)

        # First and Last Name
        name_grid = QGridLayout()
        name_grid.setSpacing(8)

        # First Name
        fname_label = QLabel("First Name")
        fname_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        name_grid.addWidget(fname_label, 0, 0)

        self.first_name = QLineEdit()
        self.first_name.setPlaceholderText("Enter first name")
        self.first_name.setStyleSheet(
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
        name_grid.addWidget(self.first_name, 1, 0)

        # Last Name
        lname_label = QLabel("Last Name")
        lname_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        name_grid.addWidget(lname_label, 0, 1)

        self.last_name = QLineEdit()
        self.last_name.setPlaceholderText("Enter last name")
        self.last_name.setStyleSheet(
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
        name_grid.addWidget(self.last_name, 1, 1)

        personal_layout.addLayout(name_grid)

        # Age and Gender
        age_gender_grid = QGridLayout()
        age_gender_grid.setSpacing(8)

        # Age
        age_label = QLabel("Age")
        age_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        age_gender_grid.addWidget(age_label, 0, 0)

        self.age = QLineEdit()
        self.age.setPlaceholderText("Age")
        self.age.setStyleSheet(
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
        age_gender_grid.addWidget(self.age, 1, 0)

        # Gender
        gender_label = QLabel("Gender")
        gender_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        age_gender_grid.addWidget(gender_label, 0, 1)

        self.gender = QComboBox()
        self.gender.addItems(["Male", "Female", "Other"])
        self.gender.setStyleSheet(
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
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {COLORS.get('on_surface', '#000000')};
                margin-right: 8px;
            }}
        """
        )
        age_gender_grid.addWidget(self.gender, 1, 1)

        personal_layout.addLayout(age_gender_grid)

        # Date of Birth
        dob_label = QLabel("Date of Birth")
        dob_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        personal_layout.addWidget(dob_label)

        self.dob = QDateEdit()
        self.dob.setCalendarPopup(True)
        self.dob.setDate(QDate.currentDate().addYears(-15))  # Default to 15 years ago
        self.dob.setStyleSheet(
            f"""
            QDateEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
                min-height: 16px;
            }}
            QDateEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        personal_layout.addWidget(self.dob)

        # Add stretch to push content to top
        personal_layout.addStretch()

        # Middle Column - Academic Information
        academic_frame = QFrame()
        academic_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('secondary', '#2E7D32')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        academic_layout = QVBoxLayout(academic_frame)
        academic_layout.setSpacing(12)

        academic_title = QLabel("🎓 Academic Information")
        academic_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('secondary', '#2E7D32')};
                margin-bottom: 8px;
            }}
        """
        )
        academic_layout.addWidget(academic_title)

        # Institution
        institution_label = QLabel("School/Institution")
        institution_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        academic_layout.addWidget(institution_label)

        self.institution = QLineEdit()
        self.institution.setPlaceholderText("Enter school or institution name")
        self.institution.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
        """
        )
        academic_layout.addWidget(self.institution)

        # Grade Level
        grade_label = QLabel("Grade Level")
        grade_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        academic_layout.addWidget(grade_label)

        self.grade_level = QLineEdit()
        self.grade_level.setPlaceholderText("e.g., Grade 8, Form 4, University")
        self.grade_level.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
        """
        )
        academic_layout.addWidget(self.grade_level)

        # Category
        category_label = QLabel("Category")
        category_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        academic_layout.addWidget(category_label)

        self.category = QComboBox()
        self.category.addItems(
            [Category.PUPIL.value, Category.STUDENT.value, Category.ADULT.value]
        )
        self.category.setStyleSheet(
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
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {COLORS.get('on_surface', '#000000')};
                margin-right: 8px;
            }}
        """
        )
        academic_layout.addWidget(self.category)

        # Membership Status
        membership_label = QLabel("Membership Status")
        membership_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        academic_layout.addWidget(membership_label)

        self.membership_status = QComboBox()
        self.membership_status.addItems(["inactive", "active", "expired", "suspended"])
        self.membership_status.setStyleSheet(
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
                border-color: {COLORS.get('secondary', '#2E7D32')};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 25px;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid {COLORS.get('on_surface', '#000000')};
                margin-right: 8px;
            }}
        """
        )
        academic_layout.addWidget(self.membership_status)

        # Add stretch to push content to top
        academic_layout.addStretch()

        # Right Column - Contact Information
        contact_frame = QFrame()
        contact_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 2px solid {COLORS.get('tertiary', '#7B1FA2')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setSpacing(12)

        contact_title = QLabel("📞 Contact Information")
        contact_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('tertiary', '#7B1FA2')};
                margin-bottom: 8px;
            }}
        """
        )
        contact_layout.addWidget(contact_title)

        # Phone Number
        phone_label = QLabel("Phone Number")
        phone_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        contact_layout.addWidget(phone_label)

        self.phone_number = QLineEdit()
        self.phone_number.setPlaceholderText("e.g., +254700123456")
        self.phone_number.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('tertiary', '#7B1FA2')};
            }}
        """
        )
        contact_layout.addWidget(self.phone_number)

        # Residence
        residence_label = QLabel("Residence")
        residence_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        contact_layout.addWidget(residence_label)

        self.residence = QLineEdit()
        self.residence.setPlaceholderText("Enter residential address")
        self.residence.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                background-color: white;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('tertiary', '#7B1FA2')};
            }}
        """
        )
        contact_layout.addWidget(self.residence)

        # Fee Information (read-only display)
        fee_label = QLabel("Membership Fee")
        fee_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        contact_layout.addWidget(fee_label)

        self.fee_display = QLabel("KSh 0")
        self.fee_display.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('tertiary_container', '#F3E5F5')};
                border: 1px solid {COLORS.get('tertiary', '#7B1FA2')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 13px;
                font-weight: 600;
                color: {COLORS.get('on_tertiary_container', '#4A148C')};
            }}
        """
        )
        contact_layout.addWidget(self.fee_display)

        # Auto-generated ID display
        id_label = QLabel("Patron ID (Auto-generated)")
        id_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 13px;
                font-weight: 500;
                color: {COLORS.get('on_surface', '#000000')};
            }}
        """
        )
        contact_layout.addWidget(id_label)

        self.patron_id_display = QLabel("Will be generated automatically")
        self.patron_id_display.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 12px;
                font-style: italic;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        contact_layout.addWidget(self.patron_id_display)

        # Add stretch to push content to top
        contact_layout.addStretch()

        # Add columns to content layout
        content_layout.addWidget(personal_frame)
        content_layout.addWidget(academic_frame)
        content_layout.addWidget(contact_frame)

        main_layout.addWidget(content_frame)

        # Action buttons section - compact
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

        cancel_btn = MaterialButton("Cancel", button_type="outlined")
        save_btn = MaterialButton("👤 Create Patron", button_type="elevated")
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
        save_btn.clicked.connect(self.save_user)
        self.category.currentTextChanged.connect(self.update_fee_display)
        self.dob.dateChanged.connect(self.calculate_age_from_dob)

    def update_fee_display(self):
        """Update membership fee display based on category"""
        category = self.category.currentText().lower()
        fee_map = {
            "pupil": 200,
            "student": 450,
            "adult": 600,
        }
        fee = fee_map.get(category, 450)
        self.fee_display.setText(f"KSh {fee}")

    def calculate_age_from_dob(self):
        """Auto-calculate age from date of birth"""
        try:
            dob = self.dob.date().toPyDate()
            today = datetime.now().date()
            age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )
            self.age.setText(str(age))
        except ValueError:
            pass

    def validate_form(self):
        """Validate form data before saving"""
        errors = []

        # Required fields validation
        if not self.first_name.text().strip():
            errors.append("First name is required")

        if not self.last_name.text().strip():
            errors.append("Last name is required")

        if not self.institution.text().strip():
            errors.append("Institution is required")

        if not self.grade_level.text().strip():
            errors.append("Grade level is required")

        # Age validation
        try:
            age = int(self.age.text().strip())
            if age < 1 or age > 120:
                errors.append("Age must be between 1 and 120")
        except ValueError:
            errors.append("Age must be a valid number")

        # Phone number validation (basic)
        phone = self.phone_number.text().strip()
        if phone and len(phone) < 10:
            errors.append("Phone number must be at least 10 digits")

        # Date of birth validation
        dob = self.dob.date().toPyDate()
        today = datetime.now().date()
        if dob >= today:
            errors.append("Date of birth must be in the past")

        # Check if calculated age matches entered age
        try:
            calculated_age = (
                today.year
                - dob.year
                - ((today.month, today.day) < (dob.month, dob.day))
            )
            entered_age = int(self.age.text().strip())
            if (
                abs(calculated_age - entered_age) > 1
            ):  # Allow 1 year difference for birthday timing
                errors.append("Age doesn't match date of birth")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")
            pass

        return errors

    def save_user(self):
        """Save patron with comprehensive validation"""
        # Validate form
        errors = self.validate_form()
        if errors:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please fix the following issues:\n\n"
                + "\n".join(f"• {error}" for error in errors),
            )
            return

        # Prepare patron data
        data = {
            "first_name": self.first_name.text().strip(),
            "last_name": self.last_name.text().strip(),
            "institution": self.institution.text().strip(),
            "grade_level": self.grade_level.text().strip(),
            "category": self.category.currentText().lower(),
            "age": int(self.age.text().strip()),
            "gender": self.gender.currentText(),
            "date_of_birth": self.dob.date().toString("yyyy-MM-dd"),
            "residence": (
                self.residence.text().strip() if self.residence.text().strip() else None
            ),
            "phone_number": (
                self.phone_number.text().strip()
                if self.phone_number.text().strip()
                else None
            ),
            "membership_status": self.membership_status.currentText().lower(),
        }

        # Save through controller
        try:
            result = self.patrons_controller.create(data)
            if result.get("success", False):
                patron = result.get("patron")
                success_msg = (
                    f"Patron created successfully!\n\n"
                    f"👤 Name: {data['first_name']} {data['last_name']}\n"
                    f"🆔 Patron ID: {patron.patron_id if patron else 'Generated'}\n"
                    f"🎓 Category: {data['category'].title()}\n"
                    f"📞 Phone: {data['phone_number'] or 'Not provided'}"
                )
                QMessageBox.information(self, "Success", success_msg)
                self.on_success()
            else:
                QMessageBox.warning(
                    self,
                    "Error",
                    result.get("message", "Failed to create patron"),
                )
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

    def reset_form(self):
        """Reset form to initial state"""
        self.first_name.clear()
        self.last_name.clear()
        self.institution.clear()
        self.grade_level.clear()
        self.age.clear()
        self.gender.setCurrentIndex(0)
        self.category.setCurrentIndex(0)
        self.membership_status.setCurrentIndex(0)
        self.dob.setDate(QDate.currentDate().addYears(-15))
        self.residence.clear()
        self.phone_number.clear()
        self.fee_display.setText("KSh 200")  # Default pupil fee
        self.patron_id_display.setText("Will be generated automatically")
