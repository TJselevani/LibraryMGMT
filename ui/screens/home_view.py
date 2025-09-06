import sip
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
    QComboBox,
    QCheckBox,
)
from PyQt5.QtGui import QColor
from config.ui_config import COLORS
from core.container import DependencyContainer
from datetime import date

from ui.widgets.table.material_table import MaterialTable

from datetime import datetime
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal, QTimer, Qt
import plotly.graph_objects as go
import json
from plotly.utils import PlotlyJSONEncoder


class ThemeManager:
    """Centralized theme management"""

    def __init__(self):
        self.is_dark_theme = False
        self.theme_callbacks = []

    def get_colors(self):
        """Get current theme colors"""
        if self.is_dark_theme:
            return {
                "primary": "#42A5F5",  # Lighter blue for dark theme
                "primary_dark": "#1976D2",
                "primary_light": "#64B5F6",
                "secondary": "#03DAC6",
                "background": "#121212",  # Dark background
                "surface": "#1E1E1E",  # Dark surface
                "surface_variant": "#2D2D2D",
                "on_surface": "#FFFFFF",  # White text
                "on_surface_variant": "#B0B0B0",
                "outline": "#404040",
                "error": "#CF6679",
                "success": "#81C784",
                "warning": "#FFB74D",
                "info": "#64B5F6",
                "text": "#FFFFFF",
                "on_primary": "#000000",
                "on_secondary": "#000000",
                "on_background": "#FFFFFF",
                "on_error": "#000000",
                "on_success": "#000000",
                "on_warning": "#000000",
            }
        else:
            return COLORS  # Your existing light theme colors

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        self.is_dark_theme = not self.is_dark_theme
        for callback in self.theme_callbacks:
            callback()

    def register_callback(self, callback):
        """Register callback for theme changes"""
        self.theme_callbacks.append(callback)


# Global theme manager instance
theme_manager = ThemeManager()


class MetricCard(QFrame):
    def __init__(self, title, value, subtitle="", trend=None):
        super().__init__()
        self.title_text = title
        self.value_text = value
        self.subtitle_text = subtitle
        self.trend_text = trend

        # Register for theme updates
        theme_manager.register_callback(self.update_theme)

        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)

        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(16)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        self.title_label = QLabel(self.title_text)

        # Value
        self.value_label = QLabel(self.value_text)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)

        # Subtitle if provided
        if self.subtitle_text:
            self.subtitle_label = QLabel(self.subtitle_text)
            layout.addWidget(self.subtitle_label)

        # Trend indicator if provided
        if self.trend_text:
            self.trend_label = QLabel(self.trend_text)
            layout.addWidget(self.trend_label)

        layout.addStretch()
        self.setLayout(layout)

    def update_theme(self):
        """Update theme colors"""
        colors = theme_manager.get_colors()

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {colors['surface']};
                border-radius: 12px;
                padding: 18px;
            }}
        """
        )

        self.title_label.setStyleSheet(
            f"color: {colors['on_surface_variant']}; font-size: 12px; font-weight: bold;"
        )

        self.value_label.setStyleSheet(
            f"""
            color: {colors['on_surface']}; 
            font-size: 16px; 
            font-weight: bold; 
            margin: 5px 0px; 
            border: 2px solid {colors['outline']};
        """
        )

        if hasattr(self, "subtitle_label"):
            self.subtitle_label.setStyleSheet(
                f"color: {colors['on_surface_variant']}; font-size: 16px;"
            )

        if hasattr(self, "trend_label"):
            color = colors["success"] if "+" in self.trend_text else colors["error"]
            self.trend_label.setStyleSheet(
                f"""
                color: {color}; 
                font-size: 11px; 
                border: 2px solid {colors['outline']};
            """
            )


class ChartWidget(QFrame):
    def __init__(self, title, chart_type="line"):
        super().__init__()
        self.title_text = title
        self.chart_type = chart_type

        # Register for theme updates
        theme_manager.register_callback(self.update_theme)

        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)

        # Add shadow effect
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(16)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel(self.title_text)
        layout.addWidget(self.title_label)

        # Chart area
        self.chart_area = QWidget()
        self.chart_area.setMinimumHeight(200)
        layout.addWidget(self.chart_area)

        self.setLayout(layout)

    def update_theme(self):
        """Update theme colors"""
        colors = theme_manager.get_colors()

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {colors['surface']};
                border-radius: 8px;
            }}
        """
        )

        self.title_label.setStyleSheet(
            f"""
            color: {colors['on_surface']}; 
            font-size: 14px; 
            font-weight: bold; 
            margin-bottom: 15px;
        """
        )

        self.chart_area.setStyleSheet(
            f"background-color: {colors['surface_variant']}; border-radius: 4px;"
        )


class TableWidget(QFrame):
    def __init__(self, title, users=None, books=None, chart_type="line"):
        super().__init__()
        self.title_text = title
        self.users = users
        self.books = books
        self.chart_type = chart_type

        # Register for theme updates
        theme_manager.register_callback(self.update_theme)

        self.setup_ui()
        self.update_theme()

    def setup_ui(self):
        self.setFrameStyle(QFrame.Box)

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setBlurRadius(16)
        self.shadow.setColor(QColor(0, 0, 0, 40))
        self.shadow.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel(self.title_text)
        layout.addWidget(self.title_label)

        if self.users:
            layout.addWidget(self._create_users_table(self.users), stretch=1)
        elif self.books:
            layout.addWidget(self._create_books_table(self.books), stretch=1)
        else:
            self.chart_area = QWidget()
            self.chart_area.setFixedHeight(300)
            layout.addWidget(self.chart_area, stretch=1)

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

        table_layout.addWidget(self.table)
        return container

    def update_theme(self):
        """Update theme colors"""
        colors = theme_manager.get_colors()

        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {colors['surface']};
                border-radius: 8px;
            }}
        """
        )

        self.title_label.setStyleSheet(
            f"""
            color: {colors['on_surface']}; 
            font-size: 14px; 
            font-weight: bold; 
            margin-bottom: 15px;
        """
        )

        if hasattr(self, "table"):
            self.table.setStyleSheet(
                f"""
                QTableWidget {{
                    background-color: {colors['surface']};
                    border: none;
                    gridline-color: {colors['outline']};
                    color: {colors['on_surface']};
                }}
                QHeaderView::section {{
                    background-color: transparent;
                    color: {colors['on_surface']};
                    font-weight: bold;
                    border: none;
                    padding: 8px;
                    text-align: left;
                    alignment: left;
                }}
                QTableWidget::item {{
                    border-bottom: 1px solid {colors['outline']};
                    color: {colors['on_surface']};
                    padding: 8px;
                    text-align: left;
                }}
            """
            )

        if hasattr(self, "chart_area"):
            self.chart_area.setStyleSheet(
                f"background-color: {colors['surface_variant']}; border-radius: 4px;"
            )


class HomeView(QWidget):
    def __init__(self, container: DependencyContainer):
        super().__init__()
        self.attendance_date = date.today()
        self.container = container

        # Register for theme updates
        theme_manager.register_callback(self.update_theme)

        self.initUI()

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
        self._build_bottom_layout_with_analytics()

        # Apply initial theme
        self.update_theme()

    def _build_header(self):
        try:
            # Header
            header_layout = QHBoxLayout()

            self.title = QLabel("Dashboard")

            # Theme toggle
            theme_toggle = QCheckBox("Dark Theme")
            theme_toggle.setChecked(theme_manager.is_dark_theme)
            theme_toggle.stateChanged.connect(lambda: theme_manager.toggle_theme())

            # User info
            self.user_info = QLabel("Welcome back, User")

            header_layout.addWidget(self.title)
            header_layout.addStretch()
            header_layout.addWidget(theme_toggle)
            header_layout.addWidget(self.user_info)
            self.content_layout.addLayout(header_layout)
        except Exception as e:
            self._handle_error(f"Error building header: {e}")

    def _build_stats_cards(self):
        """Build statistics cards for dashboard"""
        try:
            from ui.widgets.cards.material_card import MaterialStatCard

            self.stats_layout = QHBoxLayout()
            self.stats_layout.setSpacing(20)

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

            self.stat_cards = []
            colors = theme_manager.get_colors()
            cards_data = [
                ("Total Users", patrons_count, "👥", colors["primary"]),
                ("Borrowed Books", b_books_count, "📖", colors["success"]),
                ("Overdue Books", o_books_count, "⚠️", colors["warning"]),
                ("Attendance", attendances, "✨", colors["secondary"]),
            ]

            for title, value, icon, color in cards_data:
                card = MaterialStatCard(title, value, icon, color)
                self.stat_cards.append(card)
                self.stats_layout.addWidget(card)

            self.content_layout.addLayout(self.stats_layout)

        except Exception as e:
            self._handle_error(f"Error building stats cards: {e}")

    def _build_metrics_cards(self):
        """Build statistics cards for dashboard"""
        try:
            # Top metrics row
            self.metrics_layout = QHBoxLayout()
            self.metrics_layout.setSpacing(15)

            self.metric_cards = []
            cards_data = [
                ("Total Revenue", "$45,231.89", "From previous month", "+20.1%"),
                ("Subscriptions", "+2350", "From last month", "+180.1%"),
                ("Sales", "+12,234", "From last month", "+19%"),
                ("Active Now", "+573", "From last hour", "+201"),
            ]

            for title, value, subtitle, trend in cards_data:
                card = MetricCard(title, value, subtitle, trend)
                card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                self.metric_cards.append(card)
                self.metrics_layout.addWidget(card)

            self.content_layout.addLayout(self.metrics_layout)

        except Exception as e:
            self._handle_error(f"Error building metrics cards: {e}")

    def _build_charts_cards(self):
        try:
            users = self.container.get_controller("patrons").get_all()

            # Middle section - Charts
            self.charts_layout = QHBoxLayout()
            self.charts_layout.setSpacing(15)

            # Overview chart (larger)
            self.overview_chart = ChartWidget(title="Overview", chart_type="line")
            self.overview_chart.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )

            # Recent sales (smaller)
            self.sales_chart = TableWidget(
                title="Users List", users=users, books=None, chart_type="Bar"
            )
            self.sales_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            self.charts_layout.addWidget(self.sales_chart, 1)
            self.charts_layout.addWidget(self.overview_chart, 1)
            self.content_layout.addLayout(self.charts_layout)
        except Exception as e:
            self._handle_error(f"Error building charts cards: {e}")

    def _build_bottom_layout_with_analytics(self):
        """Enhanced bottom layout with integrated Plotly analytics"""
        try:
            # Bottom section with analytics
            self.bottom_layout = QHBoxLayout()
            self.bottom_layout.setSpacing(15)

            # Analytics section with Plotly integration
            self.analytics_frame = AnalyticsFrame(self.container)
            self.analytics_frame.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )

            # Recent activity section
            self.activity_frame = QFrame()
            self.activity_frame.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )

            self.activity_layout = QVBoxLayout()

            self.activity_title = QLabel("Recent Activity")
            self.activity_layout.addWidget(self.activity_title)

            # Sample activity items with real data
            try:
                recent_activities = self._get_recent_activities()
            except Exception:
                recent_activities = [
                    "New user registered",
                    "Payment received from John Doe",
                    "System backup completed",
                    "New feature deployed",
                    "Server maintenance scheduled",
                ]

            self.activity_labels = []
            for activity in recent_activities[:5]:
                activity_label = QLabel(f"• {activity}")
                self.activity_labels.append(activity_label)
                self.activity_layout.addWidget(activity_label)

            self.activity_frame.setLayout(self.activity_layout)

            self.bottom_layout.addWidget(self.analytics_frame, 2)
            self.bottom_layout.addWidget(self.activity_frame, 1)
            self.content_layout.addLayout(self.bottom_layout)

        except Exception as e:
            self._handle_error(f"Error building bottom section: {e}")

    def _get_recent_activities(self):
        """Get recent activities from database"""
        activities = []
        try:
            # Get recent patrons
            recent_patrons = self.container.get_controller("patrons").get_all()[-3:]
            for patron in recent_patrons:
                activities.append(
                    f"New patron registered: {patron.first_name} {patron.last_name}"
                )

            # Get recent borrowings
            recent_borrowings = self.container.get_controller(
                "borrowed_books"
            ).get_all()[-2:]
            for borrowing in recent_borrowings:
                if hasattr(borrowing, "book") and hasattr(borrowing, "patron"):
                    activities.append(f"Book borrowed: {borrowing.book.title}")

            # Get recent payments
            recent_payments = self.container.get_controller("payments").get_all()[-2:]
            for payment in recent_payments:
                activities.append(f"Payment received: ${payment.amount_paid}")

        except Exception as e:
            print(f"Error getting recent activities: {e}")

        return (
            activities
            if activities
            else [
                "System initialized successfully",
                "Database connection established",
                "Welcome to Library Management System",
            ]
        )

    def update_theme(self):
        """Update theme colors for main elements"""
        colors = theme_manager.get_colors()

        # Update main widget background
        self.setStyleSheet(f"QWidget {{ background-color: {colors['background']}; }}")

        # Update header elements
        if hasattr(self, "title"):
            self.title.setStyleSheet(
                f"font-size: 24px; font-weight: bold; color: {colors['on_background']};"
            )

        if hasattr(self, "user_info"):
            self.user_info.setStyleSheet(
                f"font-size: 14px; color: {colors['on_surface_variant']};"
            )

        # Update activity frame
        if hasattr(self, "activity_frame"):
            self.activity_frame.setStyleSheet(
                f"""
                QFrame {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['outline']};
                    border-radius: 8px;
                    padding: 20px;
                }}
            """
            )

        if hasattr(self, "activity_title"):
            self.activity_title.setStyleSheet(
                f"""
                color: {colors['on_surface']}; 
                font-size: 16px; 
                font-weight: bold; 
                margin-bottom: 15px;
            """
            )

        if hasattr(self, "activity_labels"):
            for label in self.activity_labels:
                label.setStyleSheet(
                    f"color: {colors['on_surface_variant']}; font-size: 12px; margin: 3px 0px;"
                )

    def _handle_error(self, error_message: str):
        """Handle errors gracefully"""
        print(f"Error: {error_message}")
        QMessageBox.warning(self, "Error", error_message)


class SafeAnalyticsWorker(QThread):
    """Safe analytics worker with proper error handling"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, container):
        super().__init__()
        self.container = container
        self._is_cancelled = False

    def cancel(self):
        """Cancel the worker safely"""
        self._is_cancelled = True

    def run(self):
        try:
            if self._is_cancelled:
                return

            self.progress.emit("Generating analytics...")

            analytics_data = {
                "generated_at": datetime.now().isoformat(),
                "summary_stats": {},
                "charts": {},
            }

            # Get basic statistics with error handling
            try:
                patrons = self.container.get_controller("patrons").get_all()
                borrowings = self.container.get_controller("borrowed_books").get_all()
                payments = self.container.get_controller("payments").get_all()

                if self._is_cancelled:
                    return

                analytics_data["summary_stats"] = {
                    "total_patrons": len(patrons),
                    "total_borrowings": len(borrowings),
                    "total_payments": len(payments),
                }

                # Chart colors
                chart_colors = ["#1976D2", "#03DAC6", "#4CAF50", "#FF9800", "#F44336"]

                # Gender distribution
                gender_counts = {}
                for patron in patrons:
                    if self._is_cancelled:
                        return
                    gender = patron.gender or "Unknown"
                    gender_counts[gender] = gender_counts.get(gender, 0) + 1

                if gender_counts and not self._is_cancelled:
                    analytics_data["charts"]["gender_distribution"] = {
                        "type": "pie",
                        "title": "Patron Gender Distribution",
                        "labels": list(gender_counts.keys()),
                        "values": list(gender_counts.values()),
                        "colors": chart_colors,
                    }

                # Institution distribution (top 10)
                if not self._is_cancelled:
                    institution_counts = {}
                    for patron in patrons:
                        if self._is_cancelled:
                            return
                        institution = patron.institution or "Unknown"
                        institution_counts[institution] = (
                            institution_counts.get(institution, 0) + 1
                        )

                    sorted_institutions = sorted(
                        institution_counts.items(), key=lambda x: x[1], reverse=True
                    )[:10]

                    if sorted_institutions:
                        analytics_data["charts"]["institution_distribution"] = {
                            "type": "bar",
                            "title": "Top Institutions",
                            "x": [item[0] for item in sorted_institutions],
                            "y": [item[1] for item in sorted_institutions],
                            "color": "#1976D2",
                        }

                # Payment status distribution
                if not self._is_cancelled and payments:
                    payment_status_counts = {}
                    for payment in payments:
                        if self._is_cancelled:
                            return
                        status = (
                            payment.status.value
                            if hasattr(payment.status, "value")
                            else str(payment.status)
                        )
                        payment_status_counts[status] = (
                            payment_status_counts.get(status, 0) + 1
                        )

                    if payment_status_counts:
                        analytics_data["charts"]["payment_status"] = {
                            "type": "doughnut",
                            "title": "Payment Status Distribution",
                            "labels": list(payment_status_counts.keys()),
                            "values": list(payment_status_counts.values()),
                            "colors": chart_colors,
                        }

                # Category distribution
                if not self._is_cancelled:
                    category_counts = {}
                    for patron in patrons:
                        if self._is_cancelled:
                            return
                        category = (
                            patron.category.value
                            if hasattr(patron.category, "value")
                            else str(patron.category)
                        )
                        category_counts[category] = category_counts.get(category, 0) + 1

                    if category_counts:
                        analytics_data["charts"]["category_distribution"] = {
                            "type": "bar",
                            "title": "Patron Category Distribution",
                            "x": list(category_counts.keys()),
                            "y": list(category_counts.values()),
                            "color": "#03DAC6",
                        }

            except Exception as e:
                if not self._is_cancelled:
                    analytics_data["error"] = str(e)

            if not self._is_cancelled:
                self.finished.emit(analytics_data)

        except Exception as e:
            if not self._is_cancelled:
                self.error.emit(f"Analytics processing failed: {str(e)}")


class AnalyticsFrame(QFrame):
    """Analytics frame with robust lifecycle management"""

    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container
        self._is_closing = False
        self._web_view_ready = False

        self.setup_ui()

        # Data
        self.analytics_data = {}
        self.current_chart = "gender_distribution"

        # Worker
        self.worker = None

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.safe_refresh_analytics)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes

        # Initial load with delay to ensure proper initialization
        QTimer.singleShot(500, self.safe_refresh_analytics)

    def setup_ui(self):
        """Setup UI with proper error handling"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #FFFFFF;
                border-radius: 12px;
            }
        """
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(16)
        shadow.setColor(QColor(0, 0, 0, 40))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Header
        self._setup_header()

        # Web view for charts
        self._setup_webview()

        # Status
        self._setup_status()

    def _setup_header(self):
        """Setup header with controls"""
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Analytics")
        self.title_label.setStyleSheet(
            """
            color: #212121; 
            font-size: 16px; 
            font-weight: bold;
        """
        )

        self.chart_selector = QComboBox()
        self.chart_selector.addItems(
            [
                "Gender Distribution",
                "Institution Distribution",
                "Payment Status",
                "Category Distribution",
            ]
        )
        self.chart_selector.setStyleSheet(
            """
            QComboBox {
                background-color: #1976D2;
                color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                min-width: 120px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #FFFFFF;
                color: #212121;
                selection-background-color: #1976D2;
            }
        """
        )
        self.chart_selector.currentTextChanged.connect(self.on_chart_changed)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:disabled {
                background-color: #E0E0E0;
                color: #757575;
            }
        """
        )
        self.refresh_btn.clicked.connect(self.safe_refresh_analytics)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.chart_selector)
        header_layout.addWidget(self.refresh_btn)

        self.layout.addLayout(header_layout)

    def _setup_webview(self):
        """Setup web view with Plotly integration that fits container margins"""
        try:
            self.web_view = QWebEngineView(self)
            self.web_view.setMinimumHeight(300)

            html_shell = """
            <!doctype html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    html, body {
                        margin: 0;
                        padding: 0;
                        background: #FFFFFF;
                        height: 100%;
                        width: 100%;
                        overflow: hidden;
                    }
                    #chart {
                        width: 100%;
                        height: 100%;
                    }
                </style>
                <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
            </head>
            <body>
                <div id="chart"></div>
                <script>
                window.renderPlotly = function(fig) {
                    var data = fig.data || [];
                    var layout = Object.assign({
                        paper_bgcolor: '#FFFFFF',
                        plot_bgcolor: '#FFFFFF',
                        margin: {l:40, r:40, t:50, b:40},
                        font: {color: '#212121'}
                    }, fig.layout || {});
                    
                    var config = Object.assign({
                        displayModeBar: true,
                        displaylogo: false,
                        responsive: true
                    }, fig.config || {});
                    
                    Plotly.react('chart', data, layout, config).then(function() {
                        requestAnimationFrame(function() {
                            Plotly.Plots.resize('chart');
                        });
                    });
                };
                window.addEventListener('resize', function() {
                    Plotly.Plots.resize('chart');
                });
                </script>
            </body>
            </html>
            """
            self.web_view.setHtml(html_shell)
            self.web_view.loadFinished.connect(self._on_web_view_loaded)
            self.layout.addWidget(self.web_view)

        except Exception as e:
            print(f"Error setting up web view: {e}")
            self.web_view = QLabel("Analytics unavailable")
            self.web_view.setStyleSheet("color: #757575; text-align: center;")
            self.layout.addWidget(self.web_view)

    def _on_web_view_loaded(self, success):
        """Handle web view load completion"""
        if success:
            self._web_view_ready = True
            print("WebView loaded successfully")
        else:
            print("WebView failed to load")

    def _setup_status(self):
        """Setup status label"""
        self.status_label = QLabel("Initializing...")
        self.status_label.setStyleSheet("color: #757575; font-size: 11px;")
        self.layout.addWidget(self.status_label)

    def safe_refresh_analytics(self):
        """Safely refresh analytics data"""
        if self._is_closing:
            return

        try:
            if hasattr(self, "refresh_btn") and not sip.isdeleted(self.refresh_btn):
                self.refresh_btn.setEnabled(False)

            if hasattr(self, "status_label") and not sip.isdeleted(self.status_label):
                self.status_label.setText("Loading analytics...")

            # Cancel existing worker
            if self.worker and self.worker.isRunning():
                self.worker.cancel()
                self.worker.quit()
                self.worker.wait(1000)  # Wait up to 1 second

            # Start new worker
            self.worker = SafeAnalyticsWorker(self.container)
            self.worker.finished.connect(
                self.on_analytics_finished, Qt.QueuedConnection
            )
            self.worker.error.connect(self.on_analytics_error, Qt.QueuedConnection)
            self.worker.start()

        except Exception as e:
            print(f"Error starting analytics refresh: {e}")
            self.on_analytics_error(f"Failed to start analytics: {str(e)}")

    def on_analytics_finished(self, data):
        """Handle analytics completion safely"""
        if self._is_closing or not self.isVisible():
            return

        try:
            self.analytics_data = data

            # Re-enable refresh button
            if hasattr(self, "refresh_btn") and not sip.isdeleted(self.refresh_btn):
                self.refresh_btn.setEnabled(True)

            # Update status
            if hasattr(self, "status_label") and not sip.isdeleted(self.status_label):
                if "error" in data:
                    self.status_label.setText(f"Error: {data['error']}")
                else:
                    self.status_label.setText(
                        f"Updated: {datetime.now().strftime('%H:%M')}"
                    )

            # Render chart with delay to ensure web view is ready
            if "error" not in data and self._web_view_ready:
                QTimer.singleShot(200, self.safe_render_current_chart)

        except Exception as e:
            print(f"Error in analytics finished handler: {e}")

    def on_analytics_error(self, error):
        """Handle analytics errors safely"""
        if self._is_closing:
            return

        try:
            # Re-enable refresh button
            if hasattr(self, "refresh_btn") and not sip.isdeleted(self.refresh_btn):
                self.refresh_btn.setEnabled(True)

            # Update status
            if hasattr(self, "status_label") and not sip.isdeleted(self.status_label):
                self.status_label.setText(f"Error: {error}")

            # Show error in web view
            if hasattr(self, "web_view") and not sip.isdeleted(self.web_view):
                error_html = f"""
                <html>
                <body style="background:#FFFFFF;color:#212121;font-family:Arial;display:flex;align-items:center;justify-content:center;height:100vh;margin:0;">
                    <div style="text-align:center;">
                        <h3>Analytics unavailable</h3>
                        <p>{error}</p>
                    </div>
                </body>
                </html>
                """
                self.web_view.setHtml(error_html)

        except Exception as e:
            print(f"Error in analytics error handler: {e}")

    def on_chart_changed(self, chart_name):
        """Handle chart selection change safely"""
        if self._is_closing:
            return

        chart_mapping = {
            "Gender Distribution": "gender_distribution",
            "Institution Distribution": "institution_distribution",
            "Payment Status": "payment_status",
            "Category Distribution": "category_distribution",
        }

        self.current_chart = chart_mapping.get(chart_name, "gender_distribution")

        if self.analytics_data and self._web_view_ready:
            QTimer.singleShot(100, self.safe_render_current_chart)

    def safe_render_current_chart(self):
        """Safely render the current chart"""
        if self._is_closing or not self._web_view_ready:
            return

        try:
            # Check if web view still exists
            if not hasattr(self, "web_view") or sip.isdeleted(self.web_view):
                return

            # Check if we have data
            if not self.analytics_data or "charts" not in self.analytics_data:
                return

            chart_data = self.analytics_data["charts"].get(self.current_chart, {})
            if not chart_data:
                js_code = """
                document.getElementById('chart').innerHTML = 
                '<div style="display:flex;align-items:center;justify-content:center;height:100%;color:#212121;font-family:Arial;"><h3>No data available</h3></div>';
                """
                self.web_view.page().runJavaScript(js_code)
                return

            # Create figure
            fig = self.create_plotly_figure(chart_data)
            fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)

            # Execute JavaScript to render chart
            js_code = f"""
            if (typeof window.renderPlotly === 'function') {{
                window.renderPlotly({fig_json});
            }} else {{
                console.error('renderPlotly function not available');
                document.getElementById('chart').innerHTML = 
                '<div style="color:#F44336;text-align:center;padding:20px;">Chart rendering unavailable</div>';
            }}
            """

            self.web_view.page().runJavaScript(js_code)

        except Exception as e:
            print(f"Error rendering chart: {e}")
            if hasattr(self, "status_label") and not sip.isdeleted(self.status_label):
                self.status_label.setText(f"Render error: {str(e)}")

    def create_plotly_figure(self, chart_data):
        """Create Plotly figure from chart data"""
        chart_type = chart_data.get("type", "bar")
        title = chart_data.get("title", "Chart")

        # Common layout settings
        layout_settings = {
            "title": {
                "text": title,
                "font": {"color": "#212121", "size": 16},
                "x": 0.5,
            },
            "paper_bgcolor": "#FFFFFF",
            "plot_bgcolor": "#FFFFFF",
            "font": {"color": "#212121", "size": 12},
            "margin": {"l": 50, "r": 40, "t": 60, "b": 50},
            "showlegend": True,
            "legend": {
                "font": {"color": "#212121"},
                "bgcolor": "rgba(255,255,255,0.8)",
            },
        }

        # Color palette
        colors = ["#1976D2", "#03DAC6", "#4CAF50", "#FF9800", "#F44336"]

        try:
            if chart_type == "pie":
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=chart_data.get("labels", []),
                            values=chart_data.get("values", []),
                            marker_colors=chart_data.get("colors", colors),
                            textinfo="label+percent",
                            textfont={"size": 12},
                            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
                        )
                    ]
                )

            elif chart_type == "doughnut":
                fig = go.Figure(
                    data=[
                        go.Pie(
                            labels=chart_data.get("labels", []),
                            values=chart_data.get("values", []),
                            hole=0.4,
                            marker_colors=chart_data.get("colors", colors),
                            textinfo="label+percent",
                            textfont={"size": 12},
                            hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percent: %{percent}<extra></extra>",
                        )
                    ]
                )

            elif chart_type == "bar":
                layout_settings.update(
                    {
                        "xaxis": {"gridcolor": "#E0E0E0", "color": "#212121"},
                        "yaxis": {"gridcolor": "#E0E0E0", "color": "#212121"},
                    }
                )

                fig = go.Figure(
                    data=[
                        go.Bar(
                            x=chart_data.get("x", []),
                            y=chart_data.get("y", []),
                            marker_color=chart_data.get("color", "#1976D2"),
                            hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
                        )
                    ]
                )

            else:
                # Default fallback
                fig = go.Figure(
                    data=[go.Bar(x=["No Data"], y=[0], marker_color="#E0E0E0")]
                )

            fig.update_layout(**layout_settings)
            return fig

        except Exception as e:
            print(f"Error creating Plotly figure: {e}")
            # Return a simple error figure
            return go.Figure(
                data=[go.Bar(x=["Error"], y=[0], marker_color="#F44336")],
                layout={"title": "Chart Error", "paper_bgcolor": "#FFFFFF"},
            )

    def closeEvent(self, event):
        """Clean up resources when closing"""
        self._is_closing = True

        try:
            # Stop timer
            if hasattr(self, "refresh_timer"):
                self.refresh_timer.stop()

            # Cancel and cleanup worker
            if self.worker:
                self.worker.cancel()
                if self.worker.isRunning():
                    self.worker.quit()
                    self.worker.wait(1000)

                # Disconnect signals to prevent callbacks on deleted objects
                try:
                    self.worker.finished.disconnect()
                    self.worker.error.disconnect()
                except:
                    pass

        except Exception as e:
            print(f"Error during cleanup: {e}")

        super().closeEvent(event)
