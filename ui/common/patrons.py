from PyQt5.QtWidgets import (
    QTableWidgetItem,
    QHeaderView,
)
from PyQt5.QtGui import QColor  # , QPalette

# from PyQt5.QtCore import Qt
from controllers.patrons_controller import PatronsController
from ui.widgets.table.entity_view import EntityView
from utils.constants import COLORS


class PatronsView(EntityView):
    def __init__(self, db_manager):
        super().__init__(
            PatronsController(db_manager),
            "Search patrons...",
            ["All", "Active", "Inactive", "Recent"],
        )

    def populate_table(self, patrons):
        self.table.setRowCount(len(patrons))
        self.table.setColumnCount(10)
        headers = [
            "Patron ID",
            "First Name",
            "Last Name",
            "Gender",
            "DOB",
            "Institution",
            "Grade",
            "Residence",
            "Phone",
            "Membership",
        ]
        self.table.setHorizontalHeaderLabels(headers)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        for row, patron in enumerate(patrons):
            self.table.setItem(row, 0, QTableWidgetItem(str(patron.patron_id)))
            self.table.setItem(row, 1, QTableWidgetItem(patron.first_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(patron.last_name or ""))
            self.table.setItem(row, 3, QTableWidgetItem(patron.gender or ""))
            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(patron.date_of_birth) if patron.date_of_birth else "N/A"
                ),
            )
            self.table.setItem(row, 5, QTableWidgetItem(patron.institution or "N/A"))
            self.table.setItem(row, 6, QTableWidgetItem(patron.grade_level or "N/A"))
            self.table.setItem(row, 7, QTableWidgetItem(patron.residence or "N/A"))
            self.table.setItem(row, 8, QTableWidgetItem(patron.phone_number or "N/A"))

            membership = patron.membership_status or "Unknown"
            item = QTableWidgetItem(membership)
            if membership.lower() == "active":
                item.setForeground(QColor(COLORS["success"]))
            elif membership.lower() == "inactive":
                item.setForeground(QColor(COLORS["error"]))
            elif membership.lower() == "pending":
                item.setForeground(QColor(COLORS["warning"]))
            self.table.setItem(row, 9, item)

    def matches_search(self, patron, text):
        searchable = f"{patron.first_name} {patron.last_name} {patron.phone_number or ''} {patron.institution or ''}".lower()
        return text in searchable

    def matches_filter(self, patron, filter_type):
        if filter_type == "All":
            return True
        status = (patron.membership_status or "").lower()
        return (
            (filter_type == "Active" and status == "active")
            or (filter_type == "Inactive" and status == "inactive")
            or (filter_type == "Recent" and status in ["pending", "new"])
        )
