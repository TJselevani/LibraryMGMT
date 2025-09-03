import json
import os
from typing import Dict, Any  # , Optional


class AppSettings:
    """Application settings management"""

    def __init__(self, config_file: str = "app_config.json"):
        self.config_file = config_file
        self._settings = self._load_settings()

    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._get_default_settings()

    def _get_default_settings(self) -> Dict[str, Any]:
        """Get default application settings"""
        return {
            "window": {"width": 1400, "height": 900, "x": 200, "y": 100},
            "session": {
                "refresh_interval": 30,  # minutes
                "warning_threshold": 5,  # minutes
            },
            "ui": {"theme": "light", "font_size": 14, "language": "en"},
            "data": {"auto_refresh": True, "cache_timeout": 300},  # seconds
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key (supports dot notation)"""
        keys = key.split(".")
        value = self._settings

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any):
        """Set setting value by key (supports dot notation)"""
        keys = key.split(".")
        current = self._settings

        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]

        current[keys[-1]] = value
        self._save_settings()

    def _save_settings(self):
        """Save settings to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self._settings, f, indent=2)
        except IOError:
            pass  # Handle save error gracefully
