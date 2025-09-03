import sys
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
    QSizePolicy,
)
from PyQt5.QtGui import QPalette, QColor, QPainter, QPen
import random


class MetricCard(QFrame):
    def __init__(self, title, value, subtitle="", trend=None):
        super().__init__()
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #1e1e1e;
                border: 2px solid #333;
                border-radius: 8px;
                padding: 18px;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #888; font-size: 12px; font-weight: normal;")

        # Value
        value_label = QLabel(value)
        value_label.setStyleSheet(
            "color: #fff; font-size: 24px; font-weight: bold; margin: 5px 0px;"
        )

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        # Subtitle if provided
        if subtitle:
            subtitle_label = QLabel(subtitle)
            subtitle_label.setStyleSheet("color: #888; font-size: 11px;")
            layout.addWidget(subtitle_label)

        # Trend indicator if provided
        if trend:
            trend_label = QLabel(trend)
            if "+" in trend:
                trend_label.setStyleSheet("color: #4ade80; font-size: 11px;")
            else:
                trend_label.setStyleSheet("color: #f87171; font-size: 11px;")
            layout.addWidget(trend_label)

        layout.addStretch()
        self.setLayout(layout)


class ChartWidget(QFrame):
    def __init__(self, title, chart_type="line"):
        super().__init__()
        self.chart_type = chart_type
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

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet(
            "color: #fff; font-size: 14px; font-weight: bold; margin-bottom: 15px;"
        )
        layout.addWidget(title_label)

        # Chart area (placeholder)
        chart_area = QWidget()
        chart_area.setMinimumHeight(200)
        chart_area.setStyleSheet("background-color: #111; border-radius: 4px;")
        layout.addWidget(chart_area)

        self.setLayout(layout)

    def paintEvent(self, event):
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw simple chart visualization
        rect = self.rect()
        chart_rect = rect.adjusted(30, 60, -30, -30)

        if self.chart_type == "line":
            # Draw line chart
            painter.setPen(QPen(QColor("#3b82f6"), 2))
            points = []
            for i in range(10):
                x = chart_rect.left() + (i * chart_rect.width() // 9)
                y = chart_rect.bottom() - random.randint(20, chart_rect.height() - 40)
                points.append((x, y))

            for i in range(len(points) - 1):
                painter.drawLine(
                    points[i][0], points[i][1], points[i + 1][0], points[i + 1][1]
                )

        elif self.chart_type == "bar":
            # Draw bar chart
            painter.setPen(QPen(QColor("#10b981"), 1))
            painter.setBrush(QColor("#10b981"))

            bar_width = chart_rect.width() // 8
            for i in range(6):
                x = chart_rect.left() + (i * (bar_width + 10))
                height = random.randint(20, chart_rect.height() - 40)
                y = chart_rect.bottom() - height
                painter.drawRect(x, y, bar_width, height)


class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Dashboard")
        self.setGeometry(100, 100, 1400, 900)

        # Set dark theme
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #0f0f0f;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
        """
        )

        # --- Scroll Area wrapper ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)  # ✅ makes content resize with window
        self.setCentralWidget(scroll)

        # Container widget inside scroll area
        container = QWidget()
        scroll.setWidget(container)

        # Main layout
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header
        header_layout = QHBoxLayout()

        title = QLabel("Dashboard")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #fff;")

        # User info
        user_info = QLabel("Welcome back, User")
        user_info.setStyleSheet("font-size: 14px; color: #888;")

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(user_info)

        # Top metrics row
        metrics_layout = QHBoxLayout()
        metrics_layout.setSpacing(15)

        for card in [
            MetricCard("Total Revenue", "$45,231.89", "From previous month", "+20.1%"),
            MetricCard("Subscriptions", "+2350", "From last month", "+180.1%"),
            MetricCard("Sales", "+12,234", "From last month", "+19%"),
            MetricCard("Active Now", "+573", "From last hour", "+201"),
        ]:
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)  # ✅ flexible
            metrics_layout.addWidget(card)

        # Middle section - Charts
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)

        # Overview chart (larger)
        overview_chart = ChartWidget("Overview", "line")
        overview_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Recent sales (smaller)
        sales_chart = ChartWidget("Recent Sales", "bar")
        sales_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        charts_layout.addWidget(overview_chart, 2)
        charts_layout.addWidget(sales_chart, 1)

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

        # Add all sections to main layout
        main_layout.addLayout(header_layout)
        main_layout.addLayout(metrics_layout)
        main_layout.addLayout(charts_layout)
        main_layout.addLayout(bottom_layout)


def main():
    app = QApplication(sys.argv)

    # Set application style
    app.setStyle("Fusion")

    # Set dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(15, 15, 15))
    palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
    palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
    palette.setColor(QPalette.Text, QColor(255, 255, 255))
    palette.setColor(QPalette.Button, QColor(30, 30, 30))
    palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
    palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
    app.setPalette(palette)

    dashboard = Dashboard()
    dashboard.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
