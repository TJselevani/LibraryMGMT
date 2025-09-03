from enum import Enum
from typing import Optional
from dataclasses import dataclass

# =====================================================================
# CONFIGURATION AND ENUMS
# =====================================================================


class ViewType(Enum):
    """Enumeration of available view types"""

    HOME = "home"
    DASHBOARD = "dashboard"
    USERS = "users"
    PATRONS = "patrons"
    BOOKS = "books"
    BORROWED_BOOKS = "borrowed_books"
    PAYMENTS = "payments"
    ALL_TABLES = "all_tables"
    LIBRARY_DATA = "library_data"


@dataclass
class ViewConfig:
    """Configuration for each view type"""

    title: str
    subtitle: str
    view_class: Optional[type] = None
    requires_actions: bool = True
    action_buttons: Optional[list] = None


class AppConfig:
    """Application configuration"""

    SESSION_REFRESH_INTERVAL = 30 * 60 * 1000  # 30 minutes
    WINDOW_GEOMETRY = (200, 100, 1400, 900)

    VIEW_CONFIGS = {
        ViewType.HOME: ViewConfig(
            title=None,
            subtitle=None,
            action_buttons=None,
        ),
        ViewType.DASHBOARD: ViewConfig(
            title="Dashboard",
            subtitle="Welcome back! Here's what's happening in your library today.",
            requires_actions=False,
        ),
        ViewType.USERS: ViewConfig(
            title="Users Management",
            subtitle="Manage library members and their information.",
            action_buttons=["Add New User", "Import Data", "Export Data"],
        ),
        ViewType.ALL_TABLES: ViewConfig(
            title=None,
            subtitle=None,
            action_buttons=None,
        ),
        ViewType.LIBRARY_DATA: ViewConfig(
            title="Library Data Management",
            subtitle="Manage all core library data: users, patrons, books, and transactions.",
            action_buttons=["Add New", "Import Data", "Export Data"],
        ),
    }


# Material Design Color Palette
COLORS = {
    "primary": "#1976D2",  # Blue 700
    "primary_dark": "#1565C0",  # Blue 800
    "primary_light": "#42A5F5",  # Blue 400
    "secondary": "#03DAC6",  # Teal A400
    "background": "#FAFAFA",  # Grey 50
    "surface": "#FFFFFF",  # White
    "surface_variant": "#F5F5F5",  # Grey 100
    "on_surface": "#212121",  # Grey 900
    "on_surface_variant": "#757575",  # Grey 600
    "outline": "#E0E0E0",  # Grey 300
    "error": "#F44336",  # Red 500
    "success": "#4CAF50",  # Green 500
    "warning": "#FF9800",  # Orange 500,
    "info": "#42A5F5",
    "info_2": "#17a2b8",  # Blue
    "text": "#000000",  # Black
    # ✅ Contrast colors
    "on_primary": "#FFFFFF",  # White (for text/icons on blue primary)
    "on_secondary": "#000000",  # Black (teal is light, so dark text works)
    "on_background": "#000000",  # Black (background is light grey)
    "on_error": "#FFFFFF",  # White on red
    "on_success": "#FFFFFF",  # White on green
    "on_warning": "#000000",  # Black on orange (orange is bright)
}


# Material Design Colors (matching main window)
COLORS2 = {
    "primary": "#1976D2",
    "primary_light": "#42A5F5",
    "surface": "#FFFFFF",
    "surface_variant": "#F5F5F5",
    "on_surface": "#212121",
    "on_surface_variant": "#757575",
    "outline": "#E0E0E0",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "error": "#F44336",
}
