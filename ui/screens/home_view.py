from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QSizePolicy,
    QMessageBox,
    QGraphicsDropShadowEffect,
    QHeaderView,
    QTableWidgetItem,
    QPushButton,
)
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from config.ui_config import COLORS
from core.container import DependencyContainer
from datetime import date

from ui.widgets.table.material_table import MaterialTable


class MetricCard(QFrame):
    def __init__(self, title, value, subtitle="", trend=None):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
                padding: 18px;
            }}
        """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 12px; font-weight: bold;")

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(
            "color: gray; font-size: 16px; font-weight: bold; margin: 5px 0px; border: 2px solid gray;"
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        # Subtitle if provided
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #888; font-size: 16px;")
            layout.addWidget(subtitle_label)

        # Trend indicator if provided
        if trend:
            trend_label = QLabel(trend)
            if "+" in trend:
                trend_label.setStyleSheet(
                    "color: #4ade80; font-size: 11px; border: 2px solid gray;"
                )
            else:
                trend_label.setStyleSheet(
                    "color: #f87171; font-size: 11px; border: 2px solid gray;"
                )
            layout.addWidget(trend_label)

        layout.addStretch()
        self.setLayout(layout)


class ChartWidget(QFrame):
    def __init__(self, title, chart_type="line"):
        super().__init__()
        self.chart_type = chart_type
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 8px;
            }}
        """
        )

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: gray; font-size: 14px; font-weight: bold; margin-bottom: 15px;"
        )
        layout.addWidget(title_label)

        # Chart area (placeholder)
        chart_area = QWidget()
        chart_area.setMinimumHeight(200)
        chart_area.setStyleSheet("background-color: transparent; border-radius: 4px;")
        layout.addWidget(chart_area)

        self.setLayout(layout)


class TableWidget(QFrame):
    def __init__(self, title, users=None, books=None, chart_type="line"):
        super().__init__()
        self.chart_type = chart_type
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 8px;
            }}
        """
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: gray; font-size: 14px; font-weight: bold; margin-bottom: 15px;"
        )
        layout.addWidget(title_label)

        if users:
            layout.addWidget(self._create_users_table(users), stretch=1)
        elif books:
            layout.addWidget(self._create_books_table(books), stretch=1)
        else:
            chart_area = QWidget()
            chart_area.setFixedHeight(300)
            chart_area.setStyleSheet(
                "background-color: transparent; border-radius: 4px;"
            )
            layout.addWidget(chart_area, stretch=1)

    def _create_users_table(self, users):
        """Creates a material-style table for patrons with action buttons."""
        container = QWidget()
        table_layout = QVBoxLayout(container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        table_layout.setSpacing(0)

        # Material styled table
        self.table = MaterialTable()
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.resizeRowsToContents()
        self.table.setColumnCount(5)
        headers = ["Patron ID", "Username", "Gender", "Level of Study", "Actions"]
        self.table.setHorizontalHeaderLabels(headers)

        # Style: no vertical borders, only bottom row border
        self.table.setStyleSheet(
            f"""
            QTableWidget {{
                background-color: {COLORS['surface']};
                border: none;
                gridline-color: {COLORS['outline']};
                color: #fff;
            }}
            QHeaderView::section {{
                background-color: transparent;
                color: #111;
                font-weight: bold;
                border: none;
                padding: 8px;
                text-align: left;
                alignment: left;
            }}
            QTableWidget::item {{
                border-bottom: 1px solid {COLORS['outline']};
                color: gray;
                padding: 8px;
                text-align: left;
            }}
            """
        )

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        # Load patrons
        self.users_data = users
        self.table.setRowCount(len(users))

        for row, user in enumerate(users):
            # Patron ID
            self.table.setItem(row, 0, QTableWidgetItem(str(user.patron_id)))

            # Username (First + Last)
            username = f"{user.first_name} {user.last_name}"
            self.table.setItem(row, 1, QTableWidgetItem(username))

            # Gender
            self.table.setItem(row, 2, QTableWidgetItem(user.gender or "N/A"))

            # Level of Study
            self.table.setItem(row, 3, QTableWidgetItem(user.grade_level or "N/A"))

            # Action Buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(8)

            btn_view = QPushButton("View")
            btn_edit = QPushButton("Edit")
            btn_delete = QPushButton("Delete")

            for btn in (btn_view, btn_edit, btn_delete):
                btn.setCursor(Qt.PointingHandCursor)
                btn.setStyleSheet(
                    """
                    QPushButton {
                        background-color: transparent;
                        border: none;
                        #color: #2196F3;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        text-decoration: underline;
                    }
                    """
                )

            action_layout.addWidget(btn_view)
            action_layout.addWidget(btn_edit)
            action_layout.addWidget(btn_delete)
            action_layout.addStretch()

            # self.table.setCellWidget(row, 4, action_widget)

        table_layout.addWidget(self.table)
        return container


class HomeView(QWidget):
    def __init__(self, container: DependencyContainer):
        super().__init__()
        self.attendance_date = date.today()
        self.container = container
        self.initUI()

        # Initialize controllers

    def initUI(self):
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        self.content_layout = main_layout

        # Add all sections to main layout
        self._build_header()
        self._build_stats_cards()
        self._build_metrics_cards()
        self._build_charts_cards()
        self._build_bottom_layout()

    def _build_bottom_layout(self):
        try:
            # Bottom section - Additional info
            bottom_layout = QHBoxLayout()
            bottom_layout.setSpacing(15)

            # Analytics section
            analytics_frame = QFrame()
            analytics_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # analytics_frame.setFrameStyle(QFrame.Box)
            analytics_frame.setStyleSheet(
                """
                QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 8px;
                    padding: 20px;
                }
            """
            )

            analytics_layout = QVBoxLayout()

            analytics_title = QLabel("Analytics")
            analytics_title.setStyleSheet(
                "color: #fff; font-size: 16px; font-weight: bold; margin-bottom: 15px;"
            )

            # Sample analytics items
            for i, (metric, value, change) in enumerate(
                [
                    ("Page Views", "1,234", "+5.2%"),
                    ("Unique Visitors", "856", "+12.5%"),
                    ("Bounce Rate", "42.3%", "-2.1%"),
                    ("Session Duration", "2m 34s", "+8.1%"),
                ]
            ):
                item_layout = QHBoxLayout()

                metric_label = QLabel(metric)
                metric_label.setStyleSheet("color: #888; font-size: 12px;")

                value_label = QLabel(value)
                value_label.setStyleSheet(
                    "color: #fff; font-size: 14px; font-weight: bold;"
                )

                change_label = QLabel(change)
                color = "#4ade80" if "+" in change else "#f87171"
                change_label.setStyleSheet(f"color: {color}; font-size: 11px;")

                item_layout.addWidget(metric_label)
                item_layout.addStretch()
                item_layout.addWidget(value_label)
                item_layout.addWidget(change_label)

                analytics_layout.addLayout(item_layout)

            analytics_frame.setLayout(analytics_layout)

            # Recent activity section
            activity_frame = QFrame()
            activity_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            # activity_frame.setFrameStyle(QFrame.Box)
            activity_frame.setStyleSheet(
                """
                QFrame {
                    background-color: #1e1e1e;
                    border: 1px solid #333;
                    border-radius: 8px;
                    padding: 20px;
                }
            """
            )

            activity_layout = QVBoxLayout()

            activity_title = QLabel("Recent Activity")
            activity_title.setStyleSheet(
                "color: #fff; font-size: 16px; font-weight: bold; margin-bottom: 15px;"
            )
            activity_layout.addWidget(activity_title)

            # Sample activity items
            activities = [
                "New user registered",
                "Payment received from John Doe",
                "System backup completed",
                "New feature deployed",
                "Server maintenance scheduled",
            ]

            for activity in activities:
                activity_label = QLabel(f"• {activity}")
                activity_label.setStyleSheet(
                    "color: #888; font-size: 12px; margin: 3px 0px;"
                )
                activity_layout.addWidget(activity_label)

            activity_frame.setLayout(activity_layout)

            bottom_layout.addWidget(analytics_frame, 1)
            bottom_layout.addWidget(activity_frame, 1)
            self.content_layout.addLayout(bottom_layout)
        except Exception as e:
            self._handle_error(f"Error building bottom section: {e}")

    def _build_charts_cards(self):
        try:

            users = self.container.get_controller("patrons").get_all()

            # Middle section - Charts
            charts_layout = QHBoxLayout()
            charts_layout.setSpacing(15)

            # Overview chart (larger)
            overview_chart = ChartWidget(title="List", chart_type="line")
            overview_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Recent sales (smaller)
            sales_chart = TableWidget(
                title="Users List", users=users, books=None, chart_type="Bar"
            )
            sales_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            charts_layout.addWidget(sales_chart, 1)
            charts_layout.addWidget(overview_chart, 1)
            self.content_layout.addLayout(charts_layout)
        except Exception as e:
            self._handle_error(f"Error building stats cards: {e}")

    def _build_header(self):
        try:
            # Header
            header_layout = QHBoxLayout()

            title = QLabel("Dashboard")
            title.setStyleSheet("font-size: 24px; font-weight: bold; color: #111;")

            # User info
            user_info = QLabel("Welcome back, User")
            user_info.setStyleSheet("font-size: 14px; color: #888;")

            header_layout.addWidget(title)
            header_layout.addStretch()
            header_layout.addWidget(user_info)
            self.content_layout.addLayout(header_layout)
        except Exception as e:
            self._handle_error(f"Error building header: {e}")

    def _build_metrics_cards(self):
        """Build statistics cards for dashboard"""

        try:

            # Top metrics row
            metrics_layout = QHBoxLayout()
            metrics_layout.setSpacing(15)

            for card in [
                MetricCard(
                    "Total Revenue", "$45,231.89", "From previous month", "+20.1%"
                ),
                MetricCard("Subscriptions", "+2350", "From last month", "+180.1%"),
                MetricCard("Sales", "+12,234", "From last month", "+19%"),
                MetricCard("Active Now", "+573", "From last hour", "+201"),
            ]:
                card.setSizePolicy(
                    QSizePolicy.Expanding, QSizePolicy.Fixed
                )  # ✅ flexible
                metrics_layout.addWidget(card)
            self.content_layout.addLayout(metrics_layout)

        except Exception as e:
            self._handle_error(f"Error building stats cards: {e}")

    def _build_stats_cards(self):
        """Build statistics cards for dashboard"""
        try:
            from ui.widgets.cards.material_card import MaterialStatCard

            stats_layout = QHBoxLayout()
            stats_layout.setSpacing(20)

            # Get statistics
            patrons_count = len(self.container.get_controller("patrons").get_all())
            b_books_count = len(
                self.container.get_controller("borrowed_books").get_all()
            )
            o_books_count = len(
                self.container.get_controller("borrowed_books").get_overdue_books()
            )
            attendances = len(
                self.container.get_controller("attendance").get_attendance_by_date(
                    self.attendance_date
                )
            )
            # Add other statistics as needed

            cards_data = [
                ("Total Users", patrons_count, "👥", COLORS["primary"]),
                ("Borrowed Books", b_books_count, "📖", COLORS["success"]),
                ("Overdue Books", o_books_count, "⚠️", COLORS["warning"]),
                ("Attendance", attendances, "✨", COLORS["secondary"]),
            ]

            for title, value, icon, color in cards_data:
                card = MaterialStatCard(title, value, icon, color)
                stats_layout.addWidget(card)

            self.content_layout.addLayout(stats_layout)

        except Exception as e:
            self._handle_error(f"Error building stats cards: {e}")

    def _handle_error(self, error_message: str):
        """Handle errors gracefully"""
        print(f"Error: {error_message}")  # Log error
        QMessageBox.warning(self, "Error", error_message)
