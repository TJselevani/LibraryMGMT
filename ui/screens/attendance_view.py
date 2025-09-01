# ui/screens/attendance_view_material.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QFrame,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QHeaderView,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from datetime import date
from controllers.attendance_controller import AttendanceController
from controllers.patrons_controller import PatronsController
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
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 12px;
                padding: 16px;
            }}
        """
        )

        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # Title
        title = QLabel("Add Patron to Attendance")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 4px;
            }}
        """
        )
        layout.addWidget(title)

        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by name, ID, or institution...")
        self.search_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px 16px;
                font-size: 14px;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                min-height: 16px;
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: white;
            }}
        """
        )
        layout.addWidget(self.search_input)

        # Search results
        self.search_results = QListWidget()
        self.search_results.setMaximumHeight(150)
        self.search_results.setStyleSheet(
            f"""
            QListWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                background-color: white;
                font-size: 13px;
            }}
            QListWidget::item {{
                padding: 12px 16px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
            QListWidget::item:hover {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
            }}
            QListWidget::item:selected {{
                background-color: {COLORS.get('primary', '#1976D2')};
                color: white;
            }}
        """
        )
        layout.addWidget(self.search_results)

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
                font-size: 13px;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        layout.addWidget(self.selected_label)

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
                background-color: {COLORS.get('success_container', '#E8F5E8')};
                border: 2px solid {COLORS.get('success', '#2E7D32')};
                border-radius: 8px;
                padding: 12px;
                font-weight: 600;
                font-size: 13px;
                color: {COLORS.get('success', '#2E7D32')};
            }}
        """
        )
        self.search_results.clear()
        self.search_input.clear()
        self.patron_selected.emit(self.selected_patron)

    def clear_selection(self):
        """Clear current selection"""
        self.selected_patron = None
        self.selected_label.setText("No patron selected")
        self.selected_label.setStyleSheet(
            f"""
            QLabel {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                padding: 12px;
                font-weight: 500;
                font-size: 13px;
                color: {COLORS.get('on_surface_variant', '#666666')};
            }}
        """
        )
        self.search_input.clear()
        self.search_results.clear()


class AttendanceView(QWidget):
    """Material Design styled Attendance view with patron search functionality"""

    def __init__(self, db_manager):
        super().__init__()
        self.controller = AttendanceController(db_manager)
        self.patrons_controller = PatronsController(db_manager)
        self.attendance_date = date.today()
        self.all_patrons = []
        self.attended_patrons = []
        self.init_ui()
        self.load_data()

    def init_ui(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(20)
        self.setStyleSheet(f"background-color: {COLORS.get('background', '#FAFAFA')};")

        # Header section
        header_frame = self.create_header()
        main_layout.addWidget(header_frame)

        # Content area - Two columns
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        # Left column - Patron search
        search_frame = self.create_search_section()
        content_layout.addWidget(search_frame, 1)

        # Right column - Attendance list
        attendance_frame = self.create_attendance_section()
        content_layout.addWidget(attendance_frame, 2)

        main_layout.addLayout(content_layout)

        # Action buttons
        action_frame = self.create_action_section()
        main_layout.addWidget(action_frame)

    def create_header(self):
        """Create header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet(
            f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS.get('primary', '#1976D2')}, 
                    stop:1 {COLORS.get('primary_variant', '#1565C0')});
                border-radius: 16px;
                padding: 20px;
            }}
        """
        )

        header_layout = QHBoxLayout(header_frame)

        # Left side - Title and date
        left_layout = QVBoxLayout()

        title = QLabel("Library Attendance")
        title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 28px;
                font-weight: 700;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                margin-bottom: 4px;
            }}
        """
        )
        left_layout.addWidget(title)

        date_label = QLabel(self.attendance_date.strftime("%A, %d %B %Y"))
        date_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 16px;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                opacity: 0.9;
            }}
        """
        )
        left_layout.addWidget(date_label)

        header_layout.addLayout(left_layout)
        header_layout.addStretch()

        # Right side - Stats
        stats_layout = QVBoxLayout()
        stats_layout.setAlignment(Qt.AlignRight)

        self.attendance_count_label = QLabel("0 Present Today")
        self.attendance_count_label.setStyleSheet(
            f"""
            QLabel {{
                font-size: 18px;
                font-weight: 600;
                color: {COLORS.get('on_primary', '#FFFFFF')};
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 8px;
                padding: 8px 16px;
            }}
        """
        )
        stats_layout.addWidget(self.attendance_count_label)

        header_layout.addLayout(stats_layout)

        return header_frame

    def create_search_section(self):
        """Create patron search section"""
        search_frame = QFrame()
        search_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 16px;
                padding: 8px;
            }}
        """
        )

        search_layout = QVBoxLayout(search_frame)
        search_layout.setSpacing(16)

        # Patron search widget
        self.patron_search = PatronSearchWidget()
        self.patron_search.patron_selected.connect(self.add_patron_to_attendance)
        search_layout.addWidget(self.patron_search)

        # Quick stats
        stats_frame = QFrame()
        stats_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                border-radius: 8px;
                padding: 12px;
            }}
        """
        )
        stats_layout = QVBoxLayout(stats_frame)

        stats_title = QLabel("Quick Stats")
        stats_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 14px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
                margin-bottom: 8px;
            }}
        """
        )
        stats_layout.addWidget(stats_title)

        self.total_patrons_label = QLabel("Total Patrons: 0")
        self.total_patrons_label.setStyleSheet("font-size: 12px; color: #666666;")
        stats_layout.addWidget(self.total_patrons_label)

        self.present_today_label = QLabel("Present Today: 0")
        self.present_today_label.setStyleSheet("font-size: 12px; color: #666666;")
        stats_layout.addWidget(self.present_today_label)

        search_layout.addWidget(stats_frame)
        search_layout.addStretch()

        return search_frame

    def create_attendance_section(self):
        """Create attendance list section"""
        attendance_frame = QFrame()
        attendance_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 16px;
                padding: 16px;
            }}
        """
        )

        attendance_layout = QVBoxLayout(attendance_frame)
        attendance_layout.setSpacing(16)

        # Section header
        section_header = QHBoxLayout()

        attendance_title = QLabel("Today's Attendance")
        attendance_title.setStyleSheet(
            f"""
            QLabel {{
                font-size: 18px;
                font-weight: 600;
                color: {COLORS.get('primary', '#1976D2')};
            }}
        """
        )
        section_header.addWidget(attendance_title)

        section_header.addStretch()

        # Filter input for existing attendance
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Filter attendance list...")
        self.filter_input.setMaximumWidth(200)
        self.filter_input.setStyleSheet(
            f"""
            QLineEdit {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 12px;
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
            }}
            QLineEdit:focus {{
                border-color: {COLORS.get('primary', '#1976D2')};
                background-color: white;
            }}
        """
        )
        self.filter_input.textChanged.connect(self.filter_attendance_table)
        section_header.addWidget(self.filter_input)

        attendance_layout.addLayout(section_header)

        # Attendance table
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(
            ["Time", "Patron ID", "Name", "Institution"]
        )

        # Configure table appearance
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.verticalHeader().setVisible(False)

        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Time
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Patron ID
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)  # Institution

        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                border: 1px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 8px;
                font-size: 13px;
                gridline-color: {COLORS.get('outline_variant', '#F0F0F0')};
                selection-background-color: {COLORS.get('primary_container', '#E3F2FD')};
            }}
            QHeaderView::section {{
                background-color: {COLORS.get('primary', '#1976D2')};
                color: white;
                font-weight: 600;
                border: none;
                padding: 12px 8px;
                font-size: 13px;
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {COLORS.get('outline_variant', '#F0F0F0')};
            }}
            QTableWidget::item:selected {{
                background-color: {COLORS.get('primary_container', '#E3F2FD')};
                color: {COLORS.get('on_primary_container', '#1565C0')};
            }}
            QTableWidget::alternateBase {{
                background-color: {COLORS.get('surface_variant', '#FAFAFA')};
            }}
        """
        )

        attendance_layout.addWidget(self.table)

        return attendance_frame

    def create_action_section(self):
        """Create action buttons section"""
        action_frame = QFrame()
        action_frame.setStyleSheet(
            f"""
            QFrame {{
                background-color: white;
                border-top: 2px solid {COLORS.get('outline', '#E0E0E0')};
                border-radius: 12px;
                padding: 16px 20px;
            }}
        """
        )

        action_layout = QHBoxLayout(action_frame)

        # Left side - Remove selected button
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.get('error_container', '#FFEBEE')};
                color: {COLORS.get('error', '#D32F2F')};
                border: 2px solid {COLORS.get('error', '#D32F2F')};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('error', '#D32F2F')};
                color: white;
            }}
            QPushButton:disabled {{
                background-color: {COLORS.get('surface_variant', '#F5F5F5')};
                color: {COLORS.get('on_surface_variant', '#999999')};
                border-color: {COLORS.get('outline', '#E0E0E0')};
            }}
        """
        )
        self.remove_btn.clicked.connect(self.remove_selected_attendance)
        self.remove_btn.setEnabled(False)
        action_layout.addWidget(self.remove_btn)

        action_layout.addStretch()

        # Right side - Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS.get('secondary_container', '#E8F5E8')};
                color: {COLORS.get('secondary', '#2E7D32')};
                border: 2px solid {COLORS.get('secondary', '#2E7D32')};
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COLORS.get('secondary', '#2E7D32')};
                color: white;
            }}
        """
        )
        refresh_btn.clicked.connect(self.load_data)
        action_layout.addWidget(refresh_btn)

        # Table selection change handler
        self.table.itemSelectionChanged.connect(self.on_table_selection_changed)

        return action_frame

    def load_data(self):
        """Load all data"""
        try:
            # Load all patrons
            self.all_patrons = self.patrons_controller.get_all()
            self.patron_search.load_patrons(self.all_patrons)

            # Load today's attendance
            self.load_attendance()

            # Update stats
            self.update_stats()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load data: {str(e)}")

    def load_attendance(self):
        """Load attendance for today"""
        try:
            attendances = self.controller.get_attendance_by_date(self.attendance_date)
            self.attended_patrons = [att.patron for att in attendances]

            self.populate_table(attendances)
            self.update_stats()

        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load attendance: {str(e)}")

    def populate_table(self, attendances):
        """Populate attendance table"""
        self.table.setRowCount(len(attendances))

        for row, attendance in enumerate(attendances):
            patron = attendance.patron

            # Time (you may want to add a time field to your Attendance model)
            time_item = QTableWidgetItem(
                "Today"
            )  # Placeholder - add actual time if available
            time_item.setFont(QFont("", 0, QFont.Bold))
            self.table.setItem(row, 0, time_item)

            # Patron ID
            id_item = QTableWidgetItem(str(patron.patron_id))
            self.table.setItem(row, 1, id_item)

            # Name
            name_item = QTableWidgetItem(f"{patron.first_name} {patron.last_name}")
            name_item.setFont(QFont("", 0, QFont.Bold))
            self.table.setItem(row, 2, name_item)

            # Institution
            institution_item = QTableWidgetItem(patron.institution)
            self.table.setItem(row, 3, institution_item)

            # Store attendance ID for removal
            time_item.setData(Qt.UserRole, attendance.id)

    def filter_attendance_table(self):
        """Filter attendance table based on search text"""
        filter_text = self.filter_input.text().lower()

        for row in range(self.table.rowCount()):
            show_row = False

            if not filter_text:
                show_row = True
            else:
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    if item and filter_text in item.text().lower():
                        show_row = True
                        break

            self.table.setRowHidden(row, not show_row)

    def add_patron_to_attendance(self, patron):
        """Add patron to today's attendance"""
        try:
            # Check if patron is already marked present
            if any(p.user_id == patron.user_id for p in self.attended_patrons):
                QMessageBox.information(
                    self,
                    "Already Present",
                    f"{patron.first_name} {patron.last_name} is already marked as present today.",
                )
                self.patron_search.clear_selection()
                return

            # Mark attendance
            attendance = self.controller.mark_attendance(
                patron.user_id, self.attendance_date
            )

            if attendance:
                QMessageBox.information(
                    self,
                    "Success",
                    f"{patron.first_name} {patron.last_name} has been marked present.",
                )

                # Reload attendance
                self.load_attendance()
                self.patron_search.clear_selection()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to mark attendance: {str(e)}")

    def remove_selected_attendance(self):
        """Remove selected attendance record"""
        current_row = self.table.currentRow()
        if current_row < 0:
            return

        # Get attendance ID
        attendance_id = self.table.item(current_row, 0).data(Qt.UserRole)
        patron_name = self.table.item(current_row, 2).text()

        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you want to remove {patron_name} from today's attendance?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            try:
                # Remove from database using the controller method
                success = self.controller.remove_attendance(attendance_id)

                if success:
                    # Reload attendance
                    self.load_attendance()
                    QMessageBox.information(
                        self,
                        "Success",
                        f"{patron_name} has been removed from attendance.",
                    )
                else:
                    QMessageBox.warning(
                        self, "Error", "Could not find attendance record to remove."
                    )

            except Exception as e:
                QMessageBox.critical(
                    self, "Error", f"Failed to remove attendance: {str(e)}"
                )

    def on_table_selection_changed(self):
        """Handle table selection change"""
        self.remove_btn.setEnabled(self.table.currentRow() >= 0)

    def update_stats(self):
        """Update statistics displays"""
        total_patrons = len(self.all_patrons)
        present_today = len(self.attended_patrons)

        self.total_patrons_label.setText(f"Total Patrons: {total_patrons}")
        self.present_today_label.setText(f"Present Today: {present_today}")
        self.attendance_count_label.setText(f"{present_today} Present Today")
