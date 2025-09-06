# PyQt5 Plotly Integration Component
"""
Integrates Plotly graphs into PyQt5 application using QWebEngineView
Handles analytics data loading and chart rendering
"""

import importlib
import json
import os
import sys
import subprocess

# import tempfile
from typing import Dict, Any
from datetime import datetime

from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QProgressBar,
    QMessageBox,
    QFrame,
    QSizePolicy,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QThread, pyqtSignal, QTimer

# from PyQt5.QtGui import QFont

import plotly.graph_objects as go
import plotly.express as px
from plotly.offline import plot


class AnalyticsWorker(QThread):
    """Background worker for running analytics"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, db_path: str, notebook_path: str = None):
        super().__init__()
        self.db_path = db_path
        self.notebook_path = notebook_path or "library_analytics.py"

    def run(self):
        try:
            self.progress.emit("Starting analytics processing...")

            # Method 1: Direct Python execution (if notebook is converted to .py)
            if self.notebook_path.endswith(".py"):
                self.progress.emit("Running analytics script...")
                self._run_python_script()
            else:
                # Method 2: Jupyter notebook execution
                self.progress.emit("Running Jupyter notebook...")
                self._run_notebook()

        except Exception as e:
            self.error.emit(f"Analytics processing failed: {str(e)}")

    def _run_python_script(self):
        """Execute the analytics Python script"""
        try:
            # Import and run the analytics function
            sys.path.append(os.path.dirname(self.notebook_path))

            # Dynamic import of the analytics module
            spec = importlib.util.spec_from_file_location(
                "analytics", self.notebook_path
            )
            analytics_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(analytics_module)

            # Run analytics
            result = analytics_module.run_analytics(self.db_path)
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(f"Python script execution failed: {str(e)}")

    def _run_notebook(self):
        """Execute Jupyter notebook and extract results"""
        try:
            import nbformat
            from nbconvert.preprocessors import ExecutePreprocessor

            # Read notebook
            with open(self.notebook_path, "r") as f:
                nb = nbformat.read(f, as_version=4)

            # Execute notebook
            ep = ExecutePreprocessor(timeout=600, kernel_name="python3")
            ep.preprocess(
                nb, {"metadata": {"path": os.path.dirname(self.notebook_path)}}
            )

            # Extract results (this would need to be customized based on your notebook structure)
            # For now, assume results are saved to a JSON file
            json_path = "library_analytics.json"
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    result = json.load(f)
                self.finished.emit(result)
            else:
                self.error.emit("Analytics results not found")

        except Exception as e:
            self.error.emit(f"Notebook execution failed: {str(e)}")


class PlotlyWidget(QFrame):
    """Custom widget to display Plotly charts in PyQt5"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #1e1e1e;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """
        )

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Header with title and controls
        self.header_layout = QHBoxLayout()

        self.title_label = QLabel("Analytics")
        self.title_label.setStyleSheet(
            """
            color: #fff;
            font-size: 16px;
            font-weight: bold;
            margin-bottom: 10px;
        """
        )

        self.chart_selector = QComboBox()
        self.chart_selector.addItems(
            [
                "Gender Distribution",
                "Institution Distribution",
                "Borrowing Trends",
                "Category Performance",
                "Payment Status",
                "Daily Attendance",
                "Revenue Trends",
            ]
        )
        self.chart_selector.setStyleSheet(
            """
            QComboBox {
                background-color: #333;
                color: #fff;
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                border: none;
            }
        """
        )
        self.chart_selector.currentTextChanged.connect(self.on_chart_changed)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setStyleSheet(
            """
            QPushButton {
                background-color: #4ECDC4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45B7D1;
            }
        """
        )
        self.refresh_btn.clicked.connect(self.refresh_analytics)

        self.header_layout.addWidget(self.title_label)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.chart_selector)
        self.header_layout.addWidget(self.refresh_btn)

        self.layout.addLayout(self.header_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 1px solid #555;
                border-radius: 5px;
                text-align: center;
                color: #fff;
            }
            QProgressBar::chunk {
                background-color: #4ECDC4;
                border-radius: 5px;
            }
        """
        )
        self.progress_bar.setVisible(False)
        self.layout.addWidget(self.progress_bar)

        # Web view for Plotly
        self.web_view = QWebEngineView()
        self.web_view.setMinimumHeight(400)
        self.layout.addWidget(self.web_view)

        # Status label
        self.status_label = QLabel("No data loaded")
        self.status_label.setStyleSheet("color: #888; font-size: 12px;")
        self.layout.addWidget(self.status_label)

        # Data storage
        self.analytics_data = {}
        self.current_chart = "gender_distribution"

        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_analytics)
        self.refresh_timer.start(300000)  # Refresh every 5 minutes

    def set_database_path(self, db_path: str):
        """Set the database path for analytics"""
        self.db_path = db_path

    def refresh_analytics(self):
        """Refresh analytics data"""
        if not hasattr(self, "db_path"):
            self.status_label.setText("Database path not set")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.refresh_btn.setEnabled(False)
        self.status_label.setText("Loading analytics...")

        # Start worker thread
        self.worker = AnalyticsWorker(self.db_path)
        self.worker.finished.connect(self.on_analytics_finished)
        self.worker.error.connect(self.on_analytics_error)
        self.worker.progress.connect(self.on_analytics_progress)
        self.worker.start()

    def on_analytics_progress(self, message: str):
        """Handle progress updates"""
        self.status_label.setText(message)

    def on_analytics_finished(self, data: Dict[str, Any]):
        """Handle analytics completion"""
        self.analytics_data = data
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)

        if "error" in data:
            self.status_label.setText(f"Error: {data['error']}")
        else:
            self.status_label.setText(
                f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
            )
            self.render_current_chart()

    def on_analytics_error(self, error: str):
        """Handle analytics errors"""
        self.progress_bar.setVisible(False)
        self.refresh_btn.setEnabled(True)
        self.status_label.setText(f"Error: {error}")
        QMessageBox.warning(self, "Analytics Error", error)

    def on_chart_changed(self, chart_name: str):
        """Handle chart selection change"""
        chart_mapping = {
            "Gender Distribution": "gender_distribution",
            "Institution Distribution": "institution_distribution",
            "Borrowing Trends": "borrowing_trends",
            "Category Performance": "category_performance",
            "Payment Status": "payment_status",
            "Daily Attendance": "daily_attendance",
            "Revenue Trends": "revenue_trends",
        }

        self.current_chart = chart_mapping.get(chart_name, "gender_distribution")
        if self.analytics_data:
            self.render_current_chart()

    def render_current_chart(self):
        """Render the currently selected chart"""
        if not self.analytics_data or "charts" not in self.analytics_data:
            return

        chart_data = self.analytics_data["charts"].get(self.current_chart, {})
        if not chart_data:
            self.web_view.setHtml(
                "<html><body><h3>No data available for this chart</h3></body></html>"
            )
            return

        # Create Plotly figure based on chart type
        fig = self.create_plotly_figure(chart_data)

        # Convert to HTML
        html_str = plot(
            fig,
            output_type="div",
            include_plotlyjs=True,
            config={
                "displayModeBar": True,
                "displaylogo": False,
                "modeBarButtonsToRemove": ["pan2d", "lasso2d", "select2d"],
            },
        )

        # Apply dark theme styling
        full_html = f"""
        <html>
        <head>
            <style>
                body {{ 
                    background-color: #1e1e1e; 
                    margin: 0; 
                    padding: 10px;
                }}
                .plotly-graph-div {{ 
                    height: 100vh !important; 
                }}
            </style>
        </head>
        <body>
            {html_str}
        </body>
        </html>
        """

        self.web_view.setHtml(full_html)

    def create_plotly_figure(self, chart_data: Dict[str, Any]) -> go.Figure:
        """Create Plotly figure from chart data"""
        chart_type = chart_data.get("type", "bar")
        title = chart_data.get("title", "Chart")

        # Common layout settings for dark theme
        layout_settings = {
            "title": {
                "text": title,
                "font": {"color": "#ffffff", "size": 18},
                "x": 0.5,
            },
            "paper_bgcolor": "#1e1e1e",
            "plot_bgcolor": "#2d2d2d",
            "font": {"color": "#ffffff"},
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
                        line={"color": chart_data.get("color", "#4ECDC4"), "width": 3},
                        marker={"size": 6},
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

        elif chart_type == "grouped_bar":
            fig = go.Figure()
            series_data = chart_data.get("series", [])
            categories = chart_data.get("categories", [])

            for series in series_data:
                fig.add_trace(
                    go.Bar(
                        name=series.get("name", ""),
                        x=categories,
                        y=series.get("data", []),
                        marker_color=series.get("color", "#4ECDC4"),
                    )
                )

            fig.update_layout(barmode="group")

        else:
            # Default to bar chart
            fig = go.Figure(
                data=[
                    go.Bar(
                        x=chart_data.get("x", []),
                        y=chart_data.get("y", []),
                        marker_color="#4ECDC4",
                    )
                ]
            )

        fig.update_layout(**layout_settings)
        return fig


# Integration with your existing HomeView
class AnalyticsIntegratedHomeView(QWidget):
    """Enhanced HomeView with integrated analytics"""

    def __init__(self, container):
        super().__init__()
        self.container = container
        self.initUI()

    def initUI(self):
        # Your existing UI code here...
        # Just showing the analytics integration part
        pass

    def _build_bottom_layout_with_analytics(self):
        """Enhanced bottom layout with analytics integration"""
        try:
            bottom_layout = QHBoxLayout()
            bottom_layout.setSpacing(15)

            # Analytics section with Plotly integration
            self.analytics_widget = PlotlyWidget()
            self.analytics_widget.setSizePolicy(
                QSizePolicy.Expanding, QSizePolicy.Expanding
            )

            # Set database path (you'll need to provide the actual path)
            db_path = self.container.db_manager.database_url.replace("sqlite:///", "")
            self.analytics_widget.set_database_path(db_path)

            # Initial data load
            self.analytics_widget.refresh_analytics()

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

            bottom_layout.addWidget(
                self.analytics_widget, 2
            )  # Analytics takes more space
            bottom_layout.addWidget(activity_frame, 1)
            self.content_layout.addLayout(bottom_layout)

        except Exception as e:
            self._handle_error(f"Error building analytics section: {e}")


# Standalone Analytics Runner Script
class AnalyticsRunner:
    """Standalone script runner for analytics processing"""

    @staticmethod
    def create_analytics_script(output_path: str = "library_analytics_runner.py"):
        """Create a standalone analytics script"""

        script_content = '''#!/usr/bin/env python3
"""
Standalone Library Analytics Script
Generates analytics data and saves to JSON
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
import sqlite3
from sqlalchemy import create_engine
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('library_analytics.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_analytics(db_path, output_path='library_analytics.json'):
    """Main analytics function"""
    try:
        logger.info(f"Starting analytics for database: {db_path}")
        
        # Database connection
        engine = create_engine(f'sqlite:///{db_path}')
        
        # Load patrons data
        patrons_query = """
        SELECT 
            p.user_id, p.patron_id, p.first_name, p.last_name,
            (p.first_name || ' ' || p.last_name) as full_name,
            p.institution, p.grade_level, p.category, p.age, p.gender,
            p.membership_status, p.membership_start_date, p.membership_expiry_date
        FROM patrons p
        """
        patrons_df = pd.read_sql_query(patrons_query, engine)
        
        # Load borrowings data
        borrowings_query = """
        SELECT 
            bb.borrow_id, bb.user_id, bb.book_id, bb.borrow_date, 
            bb.due_date, bb.return_date, bb.returned, bb.fine_amount,
            p.category as patron_category, p.gender as patron_gender,
            p.institution as patron_institution
        FROM borrowed_books bb
        JOIN patrons p ON bb.user_id = p.user_id
        """
        borrowings_df = pd.read_sql_query(borrowings_query, engine)
        borrowings_df['borrow_date'] = pd.to_datetime(borrowings_df['borrow_date'])
        
        # Load payments data
        payments_query = """
        SELECT 
            py.payment_id, py.amount_paid, py.payment_date, py.status,
            p.category as patron_category, p.gender as patron_gender
        FROM payments py
        JOIN patrons p ON py.user_id = p.user_id
        """
        payments_df = pd.read_sql_query(payments_query, engine)
        payments_df['payment_date'] = pd.to_datetime(payments_df['payment_date'])
        
        # Generate analytics
        analytics_data = {
            'generated_at': datetime.now().isoformat(),
            'summary_stats': {
                'total_patrons': len(patrons_df),
                'total_borrowings': len(borrowings_df),
                'total_payments': len(payments_df)
            },
            'charts': {}
        }
        
        # Gender distribution
        gender_counts = patrons_df['gender'].fillna('Unknown').value_counts()
        analytics_data['charts']['gender_distribution'] = {
            'type': 'pie',
            'title': 'Patron Gender Distribution',
            'labels': gender_counts.index.tolist(),
            'values': gender_counts.values.tolist(),
            'colors': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']
        }
        
        # Institution distribution
        institution_counts = patrons_df['institution'].fillna('Unknown').value_counts().head(10)
        analytics_data['charts']['institution_distribution'] = {
            'type': 'bar',
            'title': 'Top Institutions',
            'x': institution_counts.index.tolist(),
            'y': institution_counts.values.tolist(),
            'color': '#4ECDC4'
        }
        
        # Monthly borrowing trends
        if not borrowings_df.empty:
            borrowings_df['month'] = borrowings_df['borrow_date'].dt.to_period('M')
            monthly_borrowings = borrowings_df.groupby('month').size()
            analytics_data['charts']['borrowing_trends'] = {
                'type': 'line',
                'title': 'Monthly Borrowing Trends',
                'x': [str(x) for x in monthly_borrowings.index],
                'y': monthly_borrowings.values.tolist(),
                'color': '#FF6B6B'
            }
        
        # Payment status distribution
        if not payments_df.empty:
            payment_status_counts = payments_df['status'].value_counts()
            analytics_data['charts']['payment_status'] = {
                'type': 'doughnut',
                'title': 'Payment Status Distribution',
                'labels': payment_status_counts.index.tolist(),
                'values': payment_status_counts.values.tolist(),
                'colors': ['#96CEB4', '#FFEAA7', '#FF6B6B', '#DDA0DD']
            }
        
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(analytics_data, f, indent=2, default=str)
        
        logger.info(f"Analytics completed successfully. Output saved to {output_path}")
        return analytics_data
        
    except Exception as e:
        logger.error(f"Analytics failed: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python library_analytics_runner.py <database_path> [output_path]")
        sys.exit(1)
    
    db_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else 'library_analytics.json'
    
    result = run_analytics(db_path, output_path)
    if 'error' in result:
        sys.exit(1)
    else:
        print("Analytics completed successfully!")
'''

        with open(output_path, "w") as f:
            f.write(script_content)

        # Make executable
        os.chmod(output_path, 0o755)

        return output_path


# Modified AnalyticsWorker for better error handling
class ImprovedAnalyticsWorker(QThread):
    """Improved analytics worker with better error handling"""

    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, db_path: str):
        super().__init__()
        self.db_path = db_path

    def run(self):
        try:
            self.progress.emit("Preparing analytics script...")

            # Create analytics runner script
            runner = AnalyticsRunner()
            script_path = runner.create_analytics_script()

            self.progress.emit("Running analytics...")

            # Execute the script
            result = subprocess.run(
                [sys.executable, script_path, self.db_path],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                # Load results
                if os.path.exists("library_analytics.json"):
                    with open("library_analytics.json", "r") as f:
                        data = json.load(f)
                    self.finished.emit(data)
                else:
                    self.error.emit("Analytics results file not found")
            else:
                self.error.emit(f"Analytics script failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.error.emit("Analytics processing timed out")
        except Exception as e:
            self.error.emit(f"Analytics processing failed: {str(e)}")


# Usage example for your HomeView
def integrate_analytics_to_home_view(home_view_instance):
    """Helper function to integrate analytics into existing HomeView"""

    # Replace the existing _build_bottom_layout method
    def enhanced_build_bottom_layout(self):
        try:
            bottom_layout = QHBoxLayout()
            bottom_layout.setSpacing(15)

            # Analytics widget
            analytics_widget = PlotlyWidget()
            analytics_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

            # Set database path
            if hasattr(self.container, "db_manager"):
                db_path = self.container.db_manager.database_url.replace(
                    "sqlite:///", ""
                )
                analytics_widget.set_database_path(db_path)
                analytics_widget.refresh_analytics()

            # Existing activity section
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

            bottom_layout.addWidget(analytics_widget, 2)
            bottom_layout.addWidget(activity_frame, 1)
            self.content_layout.addLayout(bottom_layout)

        except Exception as e:
            self._handle_error(f"Error building analytics section: {e}")

    # Replace the method
    import types

    home_view_instance._build_bottom_layout = types.MethodType(
        enhanced_build_bottom_layout, home_view_instance
    )
