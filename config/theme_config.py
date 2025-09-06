# config/theme_config.py

from enum import Enum
from typing import Dict, List, Callable
from dataclasses import dataclass
from PyQt5.QtCore import QObject, pyqtSignal


class ThemeType(Enum):
    LIGHT = "light"
    DARK = "dark"


@dataclass
class ThemeColors:
    """Theme color configuration"""

    # Primary colors
    primary: str
    primary_dark: str
    primary_light: str
    secondary: str

    # Background colors
    background: str
    surface: str
    surface_variant: str

    # Text colors
    on_surface: str
    on_surface_variant: str
    on_primary: str
    on_secondary: str
    on_background: str

    # Utility colors
    outline: str
    error: str
    success: str
    warning: str
    info: str
    text: str

    # Additional colors for specific use cases
    on_error: str
    on_success: str
    on_warning: str


class ThemeManager(QObject):
    """Centralized theme management with Qt signals"""

    # Signal emitted when theme changes
    theme_changed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._current_theme = ThemeType.LIGHT
        self._callbacks: List[Callable] = []

        # Define theme configurations
        self._themes = {
            ThemeType.LIGHT: ThemeColors(
                # Primary colors
                primary="#1976D2",
                primary_dark="#1565C0",
                primary_light="#42A5F5",
                secondary="#03DAC6",
                # Background colors
                background="#FAFAFA",
                surface="#FFFFFF",
                surface_variant="#F5F5F5",
                # Text colors
                on_surface="#212121",
                on_surface_variant="#757575",
                on_primary="#FFFFFF",
                on_secondary="#000000",
                on_background="#000000",
                # Utility colors
                outline="#E0E0E0",
                error="#F44336",
                success="#4CAF50",
                warning="#FF9800",
                info="#42A5F5",
                text="#000000",
                # Additional colors
                on_error="#FFFFFF",
                on_success="#FFFFFF",
                on_warning="#000000",
            ),
            ThemeType.DARK: ThemeColors(
                # Primary colors
                primary="#42A5F5",
                primary_dark="#1976D2",
                primary_light="#64B5F6",
                secondary="#03DAC6",
                # Background colors
                background="#121212",
                surface="#1E1E1E",
                surface_variant="#2D2D2D",
                # Text colors
                on_surface="#FFFFFF",
                on_surface_variant="#B0B0B0",
                on_primary="#000000",
                on_secondary="#000000",
                on_background="#FFFFFF",
                # Utility colors
                outline="#404040",
                error="#CF6679",
                success="#81C784",
                warning="#FFB74D",
                info="#64B5F6",
                text="#FFFFFF",
                # Additional colors
                on_error="#000000",
                on_success="#000000",
                on_warning="#000000",
            ),
        }

    @property
    def current_theme(self) -> ThemeType:
        """Get current theme type"""
        return self._current_theme

    @property
    def is_dark_theme(self) -> bool:
        """Check if current theme is dark"""
        return self._current_theme == ThemeType.DARK

    def get_colors(self) -> Dict[str, str]:
        """Get current theme colors as dictionary"""
        colors = self._themes[self._current_theme]
        return {
            "primary": colors.primary,
            "primary_dark": colors.primary_dark,
            "primary_light": colors.primary_light,
            "secondary": colors.secondary,
            "background": colors.background,
            "surface": colors.surface,
            "surface_variant": colors.surface_variant,
            "on_surface": colors.on_surface,
            "on_surface_variant": colors.on_surface_variant,
            "on_primary": colors.on_primary,
            "on_secondary": colors.on_secondary,
            "on_background": colors.on_background,
            "outline": colors.outline,
            "error": colors.error,
            "success": colors.success,
            "warning": colors.warning,
            "info": colors.info,
            "text": colors.text,
            "on_error": colors.on_error,
            "on_success": colors.on_success,
            "on_warning": colors.on_warning,
        }

    def get_theme_colors(self) -> ThemeColors:
        """Get current theme colors as ThemeColors object"""
        return self._themes[self._current_theme]

    def set_theme(self, theme: ThemeType):
        """Set theme explicitly"""
        if theme != self._current_theme:
            self._current_theme = theme
            self._notify_theme_change()

    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = (
            ThemeType.DARK
            if self._current_theme == ThemeType.LIGHT
            else ThemeType.LIGHT
        )
        self.set_theme(new_theme)

    def register_callback(self, callback: Callable):
        """Register callback for theme changes"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable):
        """Unregister callback for theme changes"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_theme_change(self):
        """Notify all registered callbacks and emit signal"""
        # Emit Qt signal
        self.theme_changed.emit()

        # Call registered callbacks
        for callback in self._callbacks[
            :
        ]:  # Create copy to avoid modification during iteration
            try:
                callback()
            except Exception as e:
                print(f"Error in theme callback: {e}")

    def get_stylesheet_for_widget(self, widget_type: str) -> str:
        """Get pre-defined stylesheet for common widget types"""
        colors = self.get_colors()

        stylesheets = {
            "main_window": f"""
                QMainWindow {{
                    background-color: {colors['background']};
                    color: {colors['on_background']};
                }}
            """,
            "button_primary": f"""
                QPushButton {{
                    background-color: {colors['primary']};
                    color: {colors['on_primary']};
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary_light']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['primary_dark']};
                }}
                QPushButton:disabled {{
                    background-color: {colors['outline']};
                    color: {colors['on_surface_variant']};
                }}
            """,
            "button_secondary": f"""
                QPushButton {{
                    background-color: transparent;
                    color: {colors['primary']};
                    border: 2px solid {colors['primary']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {colors['primary']};
                    color: {colors['on_primary']};
                }}
                QPushButton:pressed {{
                    background-color: {colors['primary_dark']};
                    color: {colors['on_primary']};
                }}
            """,
            "card": f"""
                QFrame {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['outline']};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """,
            "table": f"""
                QTableWidget {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['outline']};
                    gridline-color: {colors['outline']};
                    color: {colors['on_surface']};
                    selection-background-color: {colors['primary_light']};
                }}
                QHeaderView::section {{
                    background-color: {colors['surface_variant']};
                    color: {colors['on_surface']};
                    border: 1px solid {colors['outline']};
                    padding: 8px;
                    font-weight: bold;
                }}
                QTableWidget::item {{
                    padding: 8px;
                    border-bottom: 1px solid {colors['outline']};
                }}
                QTableWidget::item:selected {{
                    background-color: {colors['primary_light']};
                    color: {colors['on_primary']};
                }}
            """,
            "combobox": f"""
                QComboBox {{
                    background-color: {colors['surface']};
                    color: {colors['on_surface']};
                    border: 2px solid {colors['outline']};
                    border-radius: 6px;
                    padding: 6px 12px;
                    min-height: 20px;
                }}
                QComboBox:hover {{
                    border-color: {colors['primary']};
                }}
                QComboBox:focus {{
                    border-color: {colors['primary']};
                }}
                QComboBox::drop-down {{
                    border: none;
                    width: 20px;
                }}
                QComboBox::down-arrow {{
                    image: none;
                    border: 2px solid {colors['on_surface']};
                    width: 6px;
                    height: 6px;
                    border-top: none;
                    border-right: none;
                    transform: rotate(-45deg);
                }}
                QComboBox QAbstractItemView {{
                    background-color: {colors['surface']};
                    color: {colors['on_surface']};
                    border: 1px solid {colors['outline']};
                    selection-background-color: {colors['primary']};
                    selection-color: {colors['on_primary']};
                }}
            """,
            "line_edit": f"""
                QLineEdit {{
                    background-color: {colors['surface']};
                    color: {colors['on_surface']};
                    border: 2px solid {colors['outline']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 14px;
                }}
                QLineEdit:hover {{
                    border-color: {colors['primary_light']};
                }}
                QLineEdit:focus {{
                    border-color: {colors['primary']};
                }}
            """,
            "checkbox": f"""
                QCheckBox {{
                    color: {colors['on_surface']};
                    font-size: 14px;
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border: 2px solid {colors['outline']};
                    border-radius: 3px;
                    background-color: {colors['surface']};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {colors['primary']};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {colors['primary']};
                    border-color: {colors['primary']};
                }}
                QCheckBox::indicator:checked:hover {{
                    background-color: {colors['primary_light']};
                }}
            """,
            "sidebar": f"""
                QFrame {{
                    background-color: {colors['surface']};
                    border-right: 1px solid {colors['outline']};
                }}
                QLabel {{
                    color: {colors['on_surface']};
                }}
            """,
        }

        return stylesheets.get(widget_type, "")


# Global theme manager instance
theme_manager = ThemeManager()


# Convenience functions for easy access
def get_current_colors() -> Dict[str, str]:
    """Get current theme colors"""
    return theme_manager.get_colors()


def get_stylesheet(widget_type: str) -> str:
    """Get stylesheet for widget type"""
    return theme_manager.get_stylesheet_for_widget(widget_type)


def toggle_theme():
    """Toggle theme"""
    theme_manager.toggle_theme()


def is_dark_theme() -> bool:
    """Check if dark theme is active"""
    return theme_manager.is_dark_theme
