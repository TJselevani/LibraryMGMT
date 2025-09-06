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
import plotly.express as px
from plotly.offline import plot
import json
from plotly.utils import PlotlyJSONEncoder


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
        self._build_bottom_layout_with_analytics()

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

    def _build_bottom_layout_with_analytics(self):
        """Enhanced bottom layout with integrated Plotly analytics"""
        try:
            # Bottom section with analytics
            bottom_layout = QHBoxLayout()
            bottom_layout.setSpacing(15)

            # Analytics section with Plotly integration
            analytics_frame = AnalyticsFrame(self.container)
            analytics_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Recent activity section (your existing code)
            activity_frame = QFrame()
            activity_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

            for activity in recent_activities[:5]:  # Show only 5 recent activities
                activity_label = QLabel(f"• {activity}")
                activity_label.setStyleSheet(
                    "color: #888; font-size: 12px; margin: 3px 0px;"
                )
                activity_layout.addWidget(activity_label)

            activity_frame.setLayout(activity_layout)

            bottom_layout.addWidget(analytics_frame, 2)  # Analytics takes 2/3 of space
            bottom_layout.addWidget(activity_frame, 1)  # Activity takes 1/3 of space
            self.content_layout.addLayout(bottom_layout)

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

    def _handle_error(self, error_message: str):
        """Handle errors gracefully"""
        print(f"Error: {error_message}")  # Log error
        QMessageBox.warning(self, "Error", error_message)


class QuickAnalyticsWorker(QThread):
    """Lightweight analytics worker for quick processing"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, container):
        super().__init__()

        self.container = container

    def run(self):
        try:
            self.progress.emit("Generating analytics...")

            analytics_data = {
                "generated_at": datetime.now().isoformat(),
                "summary_stats": {},
                "charts": {},
            }

            # Get basic statistics
            try:
                patrons = self.container.get_controller("patrons").get_all()
                borrowings = self.container.get_controller("borrowed_books").get_all()
                payments = self.container.get_controller("payments").get_all()

                analytics_data["summary_stats"] = {
                    "total_patrons": len(patrons),
                    "total_borrowings": len(borrowings),
                    "total_payments": len(payments),
                }

                # Gender distribution
                gender_counts = {}
                for patron in patrons:
                    gender = patron.gender or "Unknown"
                    gender_counts[gender] = gender_counts.get(gender, 0) + 1

                if gender_counts:
                    analytics_data["charts"]["gender_distribution"] = {
                        "type": "pie",
                        "title": "Patron Gender Distribution",
                        "labels": list(gender_counts.keys()),
                        "values": list(gender_counts.values()),
                        "colors": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#96CEB4"],
                    }

                # Institution distribution
                institution_counts = {}
                for patron in patrons:
                    institution = patron.institution or "Unknown"
                    institution_counts[institution] = (
                        institution_counts.get(institution, 0) + 1
                    )

                # Get top 10 institutions
                sorted_institutions = sorted(
                    institution_counts.items(), key=lambda x: x[1], reverse=True
                )[:10]

                if sorted_institutions:
                    analytics_data["charts"]["institution_distribution"] = {
                        "type": "bar",
                        "title": "Top Institutions",
                        "x": [item[0] for item in sorted_institutions],
                        "y": [item[1] for item in sorted_institutions],
                        "color": "#4ECDC4",
                    }

                # Payment status distribution
                payment_status_counts = {}
                for payment in payments:
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
                        "colors": ["#96CEB4", "#FFEAA7", "#FF6B6B", "#DDA0DD"],
                    }

                # Category distribution
                category_counts = {}
                for patron in patrons:
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
                        "color": "#45B7D1",
                    }

            except Exception as e:
                print(f"Error in analytics processing: {e}")
                analytics_data["error"] = str(e)

            self.finished.emit(analytics_data)

        except Exception as e:
            self.error.emit(f"Analytics processing failed: {str(e)}")


class AnalyticsFrame(QFrame):
    """Self-contained analytics frame for easy integration"""

    def __init__(self, container, parent=None):
        super().__init__(parent)
        self.container = container
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border-radius: 12px;
            }}
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

        # Data
        self.analytics_data = {}
        self.current_chart = "gender_distribution"

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(600000)  # Refresh every 10 minutes

        # Initial load
        self.refresh_analytics()

    def _setup_header(self):
        """Setup header with controls"""
        header_layout = QHBoxLayout()

        self.title_label = QLabel("Analytics")
        self.title_label.setStyleSheet(
            """
            color: gray; 
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
            f"""
            QComboBox {{
                background-color: {COLORS['primary']};
                color: #fff;
                border: 1px solid gray;
                border-radius: 4px;
                padding: 5px;
                min-width: 120px;
            }}
        """
        )
        self.chart_selector.currentTextChanged.connect(self.on_chart_changed)

        self.refresh_btn = QPushButton("↻")
        self.refresh_btn.setMaximumWidth(30)
        self.refresh_btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {COLORS['primary']};
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: #45B7D1;
            }}
        """
        )
        self.refresh_btn.clicked.connect(self.refresh_analytics)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.chart_selector)
        header_layout.addWidget(self.refresh_btn)

        self.layout.addLayout(header_layout)

    # def _setup_webview(self):
    #     """Setup web view for displaying charts"""
    #     self.web_view = QWebEngineView(self)
    #     # self.web_view.setHtml(
    #     #     "<html><body><h1 style='color:gray'>TEST</h1></body></html>"
    #     # )
    #     self.web_view.setMinimumHeight(300)
    #     self.layout.addWidget(self.web_view)
    def _setup_webview(self):
        self.web_view = QWebEngineView(self)
        self.web_view.setMinimumHeight(300)

        html_shell = """
        <!doctype html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
            html, body { margin:0; padding:0; background:#FFFFFF; height:100%; }
            #chart { width:100vw; height:100vh; }
            </style>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div id="chart"></div>
            <script>
            window.renderPlotly = function(fig){
                var data = fig.data || [];
                var layout = Object.assign({paper_bgcolor:'#FFFFFF', plot_bgcolor:'#2d2d2d'}, fig.layout || {});
                var config = Object.assign({displayModeBar:false, displaylogo:false}, fig.config || {});
                Plotly.react('chart', data, layout, config).then(function(){
                // Ensure correct sizing after Qt lays out the view
                requestAnimationFrame(function(){ Plotly.Plots.resize('chart'); });
                });
            };
            window.addEventListener('resize', function(){ Plotly.Plots.resize('chart'); });
            </script>
        </body>
        </html>
        """
        self.web_view.setHtml(html_shell)
        self.layout.addWidget(self.web_view)

    def _setup_status(self):
        """Setup status label"""
        self.status_label = QLabel("Loading...")
        self.status_label.setStyleSheet("color: #888; font-size: 11px;")
        self.layout.addWidget(self.status_label)

    def refresh_analytics(self):
        """Refresh analytics data"""
        self.refresh_btn.setEnabled(False)
        self.status_label.setText("Loading analytics...")

        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()

        # Start worker
        self.worker = QuickAnalyticsWorker(self.container)
        # self.worker.finished.connect(self.on_analytics_finished)
        # self.worker.error.connect(self.on_analytics_error)
        self.worker.finished.connect(self.on_analytics_finished, Qt.QueuedConnection)
        self.worker.error.connect(self.on_analytics_error, Qt.QueuedConnection)
        self.worker.start()

    def on_analytics_finished(self, data):
        """Handle analytics completion"""
        if not self.isVisible() or not self.web_view or sip.isdeleted(self.web_view):
            print("⚠️ AnalyticsFrame already closed, ignoring finished signal")
            return

        self.analytics_data = data
        self.refresh_btn.setEnabled(True)

        if "error" in data:
            self.status_label.setText(f"Error: {data['error']}")
        else:
            self.status_label.setText(f"Updated: {datetime.now().strftime('%H:%M')}")
            self.render_current_chart()

    def on_analytics_error(self, error):
        """Handle analytics errors"""
        self.refresh_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error}")
        self.web_view.setHtml(
            "<html><body><h3>Analytics unavailable</h3></body></html>"
        )

    def on_chart_changed(self, chart_name):
        """Handle chart selection change"""
        chart_mapping = {
            "Gender Distribution": "gender_distribution",
            "Institution Distribution": "institution_distribution",
            "Payment Status": "payment_status",
            "Category Distribution": "category_distribution",
        }

        self.current_chart = chart_mapping.get(chart_name, "gender_distribution")
        if self.analytics_data:
            self.render_current_chart()

    def render_current_chart(self):
        if not self.web_view or sip.isdeleted(self.web_view):
            return
        if not self.analytics_data or "charts" not in self.analytics_data:
            return

        chart_data = self.analytics_data["charts"].get(self.current_chart, {})
        if not chart_data:
            self.web_view.page().runJavaScript(
                f"document.getElementById('chart').innerHTML='<h3 style=\"color:{COLORS['surface']};font-family:sans-serif\">No data</h3>';"
            )
            return

        fig = self.create_plotly_figure(chart_data)
        fig_json = json.dumps(fig, cls=PlotlyJSONEncoder)  # serialize
        js = f"window.renderPlotly({fig_json});"
        self.web_view.page().runJavaScript(js)

    def create_plotly_figure(self, chart_data):
        """Create Plotly figure from chart data"""
        chart_type = chart_data.get("type", "bar")
        title = chart_data.get("title", "Chart")

        # Common layout for dark theme
        layout_settings = {
            "title": {
                "text": title,
                "font": {"color": "#ffffff", "size": 14},
                "x": 0.5,
            },
            "paper_bgcolor": "#F5F5F5",
            "plot_bgcolor": "#F5F5F5",
            "font": {"color": "#ffffff", "size": 10},
            "margin": {"l": 40, "r": 40, "t": 50, "b": 40},
            "xaxis": {"gridcolor": "#404040", "color": "#ffffff"},
            "yaxis": {"gridcolor": "#404040", "color": "#ffffff"},
        }

        if chart_type == "pie":
            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=chart_data.get("labels", []),
                        values=chart_data.get("values", []),
                        marker_colors=chart_data.get(
                            "colors", px.colors.qualitative.Set3
                        ),
                        textinfo="label+percent",
                        textfont={"size": 10},
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
                        marker_colors=chart_data.get(
                            "colors", px.colors.qualitative.Set3
                        ),
                        textinfo="label+percent",
                        textfont={"size": 10},
                    )
                ]
            )

        elif chart_type == "line":
            fig = go.Figure(
                data=[
                    go.Scatter(
                        x=chart_data.get("x", []),
                        y=chart_data.get("y", []),
                        mode="lines+markers",
                        line={"color": chart_data.get("color", "#4ECDC4"), "width": 2},
                        marker={"size": 4},
                    )
                ]
            )

        elif chart_type == "bar":
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=chart_data.get("x", []),
                        y=chart_data.get("y", []),
                        marker_color=chart_data.get("color", "#4ECDC4"),
                    )
                ]
            )

        else:
            # Default fallback
            fig = go.Figure(data=[go.Bar(x=["No Data"], y=[0], marker_color="#666666")])

        fig.update_layout(**layout_settings)
        return fig

    def closeEvent(self, event):
        try:
            if hasattr(self, "worker"):
                self.worker.finished.disconnect(self.on_analytics_finished)
                self.worker.error.disconnect(self.on_analytics_error)
                if self.worker.isRunning():
                    self.worker.terminate()
                    self.worker.wait()
        except Exception:
            pass
        super().closeEvent(event)
