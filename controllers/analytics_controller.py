# controllers/analytics_controller.py
"""
Analytics controller for handling data visualization requests in the LibraryMGMT system.
"""

from typing import Dict, Any, Optional
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from core.base.controller import BaseController
from services.analytics_service import AnalyticsService, create_analytics_service
from infrastructure.database.connection import DatabaseManager
from utils.error_handler import handle_exceptions
import json


class AnalyticsWorker(QThread):
    """Worker thread for analytics operations to prevent UI blocking."""

    result_ready = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, analytics_service: AnalyticsService, operation: str, **kwargs):
        super().__init__()
        self.analytics_service = analytics_service
        self.operation = operation
        self.kwargs = kwargs

    def run(self):
        """Execute analytics operation in background thread."""
        try:
            if self.operation == "borrowing_trends":
                result = self.analytics_service.get_borrowing_trends(
                    days=self.kwargs.get("days", 30)
                )
            elif self.operation == "popular_books":
                result = self.analytics_service.get_popular_books(
                    limit=self.kwargs.get("limit", 10)
                )
            elif self.operation == "patron_activity":
                result = self.analytics_service.get_patron_activity()
            elif self.operation == "overdue_analysis":
                result = self.analytics_service.get_overdue_analysis()
            elif self.operation == "financial_overview":
                result = self.analytics_service.get_financial_overview(
                    months=self.kwargs.get("months", 12)
                )
            elif self.operation == "dashboard":
                result = self.analytics_service.get_library_dashboard()
            else:
                raise ValueError(f"Unknown operation: {self.operation}")

            self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))


class AnalyticsController(BaseController):
    """Controller for analytics and data visualization operations."""

    # Signals for communication with the view
    analytics_data_ready = pyqtSignal(dict)
    analytics_error = pyqtSignal(str)
    loading_started = pyqtSignal()
    loading_finished = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self.analytics_service = create_analytics_service(db_manager)
        self.current_worker = None

    @handle_exceptions
    def get_borrowing_trends(self, days: int = 30) -> None:
        """Get borrowing trends data."""
        self._execute_analytics_operation("borrowing_trends", days=days)

    @handle_exceptions
    def get_popular_books(self, limit: int = 10) -> None:
        """Get popular books data."""
        self._execute_analytics_operation("popular_books", limit=limit)

    @handle_exceptions
    def get_patron_activity(self) -> None:
        """Get patron activity analysis."""
        self._execute_analytics_operation("patron_activity")

    @handle_exceptions
    def get_overdue_analysis(self) -> None:
        """Get overdue books analysis."""
        self._execute_analytics_operation("overdue_analysis")

    @handle_exceptions
    def get_financial_overview(self, months: int = 12) -> None:
        """Get financial overview."""
        self._execute_analytics_operation("financial_overview", months=months)

    @handle_exceptions
    def get_dashboard_data(self) -> None:
        """Get comprehensive dashboard data."""
        self._execute_analytics_operation("dashboard")

    def _execute_analytics_operation(self, operation: str, **kwargs) -> None:
        """Execute analytics operation in background thread."""
        # Clean up previous worker
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()

        # Create and start new worker
        self.current_worker = AnalyticsWorker(
            self.analytics_service, operation, **kwargs
        )
        self.current_worker.result_ready.connect(self._on_result_ready)
        self.current_worker.error_occurred.connect(self._on_error_occurred)

        self.loading_started.emit()
        self.current_worker.start()

    def _on_result_ready(self, result: Dict[str, Any]) -> None:
        """Handle analytics result."""
        self.loading_finished.emit()
        self.analytics_data_ready.emit(result)

    def _on_error_occurred(self, error_message: str) -> None:
        """Handle analytics error."""
        self.loading_finished.emit()
        self.analytics_error.emit(error_message)

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait()


# ui/screens/analytics_view.py
"""
Analytics view for displaying data visualizations in the LibraryMGMT system.
"""

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLabel,
    QScrollArea,
    QFrame,
    QSpinBox,
    QTabWidget,
    QSplashScreen,
    QProgressBar,
    QMessageBox,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QTimer
from PyQt5.QtGui import QFont, QPalette, QPixmap
from ui.screens.base_screen import BaseScreen
from ui.widgets.cards.material_card import MaterialCard
from ui.widgets.buttons.material_button import MaterialButton
from controllers.analytics_controller import AnalyticsController
from infrastructure.database.connection import DatabaseManager
import plotly.graph_objects as go
import plotly.offline as pyo
import tempfile
import os
import json


class PlotlyWidget(QWebEngineView):
    """Custom widget for displaying Plotly charts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(400)
        self.temp_file = None

    def show_plot(self, figure_json: dict):
        """Display a Plotly figure from JSON data."""
        if not figure_json:
            self.show_empty_state()
            return

        try:
            # Create Plotly figure from JSON
            fig = go.Figure(figure_json)

            # Generate HTML
            html_content = pyo.plot(fig, output_type="div", include_plotlyjs="cdn")

            # Create temporary file
            if self.temp_file:
                os.unlink(self.temp_file)

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False
            ) as f:
                f.write(
                    f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Analytics Chart</title>
                    <style>
                        body {{ margin: 0; padding: 10px; font-family: Arial, sans-serif; }}
                        .chart-container {{ width: 100%; height: 100vh; }}
                    </style>
                </head>
                <body>
                    <div class="chart-container">
                        {html_content}
                    </div>
                </body>
                </html>
                """
                )
                self.temp_file = f.name

            # Load the HTML file
            self.load(QUrl.fromLocalFile(self.temp_file))

        except Exception as e:
            self.show_error(f"Error displaying chart: {str(e)}")

    def show_empty_state(self):
        """Show empty state when no data is available."""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>No Data</title>
            <style>
                body {
                    margin: 0; padding: 0; font-family: Arial, sans-serif;
                    display: flex; align-items: center; justify-content: center;
                    height: 100vh; background-color: #f5f5f5;
                }
                .empty-state {
                    text-align: center; color: #666;
                }
                .empty-icon { font-size: 48px; margin-bottom: 16px; }
            </style>
        </head>
        <body>
            <div class="empty-state">
                <div class="empty-icon">📊</div>
                <h3>No Data Available</h3>
                <p>There's no data to display for this visualization.</p>
            </div>
        </body>
        </html>
        """

        if self.temp_file:
            os.unlink(self.temp_file)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html_content)
            self.temp_file = f.name

        self.load(QUrl.fromLocalFile(self.temp_file))

    def show_error(self, error_message: str):
        """Show error state."""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Error</title>
            <style>
                body {{
                    margin: 0; padding: 20px; font-family: Arial, sans-serif;
                    display: flex; align-items: center; justify-content: center;
                    height: 100vh; background-color: #fff5f5;
                }}
                .error-state {{
                    text-align: center; color: #e74c3c; max-width: 400px;
                }}
                .error-icon {{ font-size: 48px; margin-bottom: 16px; }}
            </style>
        </head>
        <body>
            <div class="error-state">
                <div class="error-icon">⚠️</div>
                <h3>Error Loading Chart</h3>
                <p>{error_message}</p>
            </div>
        </body>
        </html>
        """

        if self.temp_file:
            os.unlink(self.temp_file)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            f.write(html_content)
            self.temp_file = f.name

        self.load(QUrl.fromLocalFile(self.temp_file))

    def closeEvent(self, event):
        """Clean up temporary files on close."""
        if self.temp_file and os.path.exists(self.temp_file):
            os.unlink(self.temp_file)
        super().closeEvent(event)


class KPICard(MaterialCard):
    """Card widget for displaying Key Performance Indicators."""

    def __init__(self, title: str, value: str, icon: str = "📊", parent=None):
        super().__init__(parent)
        self.setup_ui(title, value, icon)

    def setup_ui(self, title: str, value: str, icon: str):
        """Setup the KPI card UI."""
        layout = QVBoxLayout()

        # Header with icon
        header_layout = QHBoxLayout()
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Arial", 24))
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10))
        title_label.setStyleSheet("color: #666;")

        header_layout.addWidget(icon_label)
        header_layout.addStretch()
        header_layout.addWidget(title_label)

        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setStyleSheet("color: #333; margin: 10px 0;")

        layout.addLayout(header_layout)
        layout.addWidget(value_label)
        layout.addStretch()

        self.setLayout(layout)
        self.setFixedHeight(120)


class AnalyticsView(BaseScreen):
    """Main analytics view with tabs for different visualizations."""

    refresh_requested = pyqtSignal()

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.controller = AnalyticsController(db_manager)
        self.setup_ui()
        self.connect_signals()

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_dashboard)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes

    def setup_ui(self):
        """Setup the analytics view UI."""
        layout = QVBoxLayout()

        # Header
        header_layout = QHBoxLayout()
        title_label = QLabel("📊 Library Analytics")
        title_label.setFont(QFont("Arial", 18, QFont.Bold))

        refresh_btn = MaterialButton("🔄 Refresh", "primary")
        refresh_btn.clicked.connect(self.refresh_dashboard)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(refresh_btn)

        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Tab widget
        self.tab_widget = QTabWidget()

        # Dashboard tab
        self.dashboard_tab = self.create_dashboard_tab()
        self.tab_widget.addTab(self.dashboard_tab, "📈 Dashboard")

        # Borrowing trends tab
        self.trends_tab = self.create_trends_tab()
        self.tab_widget.addTab(self.trends_tab, "📚 Borrowing Trends")

        # Popular content tab
        self.popular_tab = self.create_popular_tab()
        self.tab_widget.addTab(self.popular_tab, "🏆 Popular Content")

        # Financial tab
        self.financial_tab = self.create_financial_tab()
        self.tab_widget.addTab(self.financial_tab, "💰 Financial")

        # Patron analysis tab
        self.patron_tab = self.create_patron_tab()
        self.tab_widget.addTab(self.patron_tab, "👥 Patron Analysis")

        layout.addLayout(header_layout)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.tab_widget)

        self.setLayout(layout)

    def create_dashboard_tab(self) -> QWidget:
        """Create the dashboard tab with KPIs and overview charts."""
        widget = QWidget()
        layout = QVBoxLayout()

        # KPI Cards container
        kpi_layout = QHBoxLayout()
        self.kpi_container = kpi_layout

        # Placeholder KPI cards
        self.kpi_cards = []
        for i in range(5):
            card = KPICard(f"Metric {i+1}", "Loading...", "📊")
            self.kpi_cards.append(card)
            kpi_layout.addWidget(card)

        # Charts container
        charts_layout = QVBoxLayout()

        # Borrowing trends chart
        trends_card = MaterialCard()
        trends_layout = QVBoxLayout()
        trends_layout.addWidget(QLabel("Borrowing Trends (Last 30 Days)"))
        self.dashboard_trends_chart = PlotlyWidget()
        trends_layout.addWidget(self.dashboard_trends_chart)
        trends_card.setLayout(trends_layout)

        # Popular books chart
        popular_card = MaterialCard()
        popular_layout = QVBoxLayout()
        popular_layout.addWidget(QLabel("Top 5 Popular Books"))
        self.dashboard_popular_chart = PlotlyWidget()
        popular_layout.addWidget(self.dashboard_popular_chart)
        popular_card.setLayout(popular_layout)

        charts_layout.addWidget(trends_card)
        charts_layout.addWidget(popular_card)

        layout.addLayout(kpi_layout)
        layout.addLayout(charts_layout)

        widget.setLayout(layout)
        return widget

    def create_trends_tab(self) -> QWidget:
        """Create the borrowing trends tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Time Period (days):"))

        self.trends_days_spinbox = QSpinBox()
        self.trends_days_spinbox.setRange(7, 365)
        self.trends_days_spinbox.setValue(30)
        controls_layout.addWidget(self.trends_days_spinbox)

        trends_update_btn = MaterialButton("Update", "secondary")
        trends_update_btn.clicked.connect(self.update_borrowing_trends)
        controls_layout.addWidget(trends_update_btn)

        controls_layout.addStretch()

        # Chart
        self.trends_chart = PlotlyWidget()

        layout.addLayout(controls_layout)
        layout.addWidget(self.trends_chart)

        widget.setLayout(layout)
        return widget

    def create_popular_tab(self) -> QWidget:
        """Create the popular content tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Number of books:"))

        self.popular_limit_spinbox = QSpinBox()
        self.popular_limit_spinbox.setRange(5, 50)
        self.popular_limit_spinbox.setValue(10)
        controls_layout.addWidget(self.popular_limit_spinbox)

        popular_update_btn = MaterialButton("Update", "secondary")
        popular_update_btn.clicked.connect(self.update_popular_books)
        controls_layout.addWidget(popular_update_btn)

        controls_layout.addStretch()

        # Chart
        self.popular_chart = PlotlyWidget()

        layout.addLayout(controls_layout)
        layout.addWidget(self.popular_chart)

        widget.setLayout(layout)
        return widget

    def create_financial_tab(self) -> QWidget:
        """Create the financial analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Controls
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Time Period (months):"))

        self.financial_months_spinbox = QSpinBox()
        self.financial_months_spinbox.setRange(1, 24)
        self.financial_months_spinbox.setValue(12)
        controls_layout.addWidget(self.financial_months_spinbox)

        financial_update_btn = MaterialButton("Update", "secondary")
        financial_update_btn.clicked.connect(self.update_financial_overview)
        controls_layout.addWidget(financial_update_btn)

        controls_layout.addStretch()

        # Chart
        self.financial_chart = PlotlyWidget()

        layout.addLayout(controls_layout)
        layout.addWidget(self.financial_chart)

        widget.setLayout(layout)
        return widget

    def create_patron_tab(self) -> QWidget:
        """Create the patron analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout()

        # Controls
        controls_layout = QHBoxLayout()
        patron_update_btn = MaterialButton("🔄 Update Analysis", "secondary")
        patron_update_btn.clicked.connect(self.update_patron_activity)
        controls_layout.addWidget(patron_update_btn)
        controls_layout.addStretch()

        # Chart
        self.patron_chart = PlotlyWidget()

        layout.addLayout(controls_layout)
        layout.addWidget(self.patron_chart)

        widget.setLayout(layout)
        return widget

    def connect_signals(self):
        """Connect controller signals to view methods."""
        self.controller.analytics_data_ready.connect(self.handle_analytics_data)
        self.controller.analytics_error.connect(self.handle_analytics_error)
        self.controller.loading_started.connect(self.show_loading)
        self.controller.loading_finished.connect(self.hide_loading)

    def show_loading(self):
        """Show loading indicator."""
        self.progress_bar.setVisible(True)

    def hide_loading(self):
        """Hide loading indicator."""
        self.progress_bar.setVisible(False)

    def handle_analytics_data(self, data: dict):
        """Handle analytics data from controller."""
        # Determine which chart to update based on current operation
        current_tab = self.tab_widget.currentIndex()

        if "kpis" in data:  # Dashboard data
            self.update_kpi_cards(data["kpis"])
            if "borrowing_trends" in data:
                self.dashboard_trends_chart.show_plot(data["borrowing_trends"])
            if "popular_books" in data:
                self.dashboard_popular_chart.show_plot(data["popular_books"])
        elif "figure" in data:  # Single chart data
            if current_tab == 1:  # Trends tab
                self.trends_chart.show_plot(data["figure"])
            elif current_tab == 2:  # Popular tab
                self.popular_chart.show_plot(data["figure"])
            elif current_tab == 3:  # Financial tab
                self.financial_chart.show_plot(data["figure"])
            elif current_tab == 4:  # Patron tab
                self.patron_chart.show_plot(data["figure"])

    def handle_analytics_error(self, error_message: str):
        """Handle analytics errors."""
        QMessageBox.warning(
            self, "Analytics Error", f"Error loading analytics data:\n{error_message}"
        )

    def update_kpi_cards(self, kpis: list):
        """Update KPI cards with new data."""
        for i, kpi_data in enumerate(kpis):
            if i < len(self.kpi_cards):
                card = self.kpi_cards[i]
                # Remove old card and create new one with updated data
                old_card = self.kpi_container.itemAt(i).widget()
                if old_card:
                    old_card.setParent(None)

                new_card = KPICard(
                    kpi_data.get("title", ""),
                    kpi_data.get("value", ""),
                    kpi_data.get("icon", "📊"),
                )
                self.kpi_container.insertWidget(i, new_card)
                self.kpi_cards[i] = new_card

    def refresh_dashboard(self):
        """Refresh dashboard data."""
        self.controller.get_dashboard_data()

    def update_borrowing_trends(self):
        """Update borrowing trends chart."""
        days = self.trends_days_spinbox.value()
        self.controller.get_borrowing_trends(days)

    def update_popular_books(self):
        """Update popular books chart."""
        limit = self.popular_limit_spinbox.value()
        self.controller.get_popular_books(limit)

    def update_financial_overview(self):
        """Update financial overview chart."""
        months = self.financial_months_spinbox.value()
        self.controller.get_financial_overview(months)

    def update_patron_activity(self):
        """Update patron activity chart."""
        self.controller.get_patron_activity()

    def showEvent(self, event):
        """Called when the view is shown."""
        super().showEvent(event)
        # Auto-load dashboard data when view is first shown
        QTimer.singleShot(100, self.refresh_dashboard)

    def closeEvent(self, event):
        """Clean up resources when closing."""
        self.refresh_timer.stop()
        self.controller.cleanup()
        super().closeEvent(event)
