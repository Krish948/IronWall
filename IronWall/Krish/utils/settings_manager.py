"""
IronWall Antivirus - Settings Manager
Handles all application configuration and settings
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import threading

class SettingsManager:
    """Manages all IronWall Antivirus settings with persistence"""
    
    def __init__(self, config_file: str = "ironwall_settings.json"):
        self.config_file = Path(config_file)
        self._lock = threading.Lock()
        self._settings = self._load_default_settings()
        self.load_settings()
    
    def _load_default_settings(self) -> Dict[str, Any]:
        """Load default settings for IronWall Antivirus"""
        return {
            # Protection Settings
            "protection": {
                "real_time_protection": True,
                "firewall_protection": True,
                "usb_protection": True,
                "heuristic_scanning": "Medium",  # Low, Medium, High
                "safe_browsing": True,
                "webcam_microphone_control": True
            },
            
            # Scan Control
            "scanning": {
                "default_scan_type": "Quick",  # Quick, Full, Deep, Custom
                "scan_compressed_files": True,
                "scan_startup_programs": True,
                "exclusions": {
                    "files": [],
                    "folders": [],
                    "extensions": []
                }
            },
            
            # Scan Scheduling
            "scheduling": {
                "enable_scheduled_scans": False,
                "scan_frequency": "Weekly",  # Daily, Weekly, Monthly
                "scan_time": "02:00",
                "auto_delete_threats": True
            },
            
            # Notifications
            "notifications": {
                "threat_alerts": True,
                "scan_results_summary": True,
                "silent_mode": False,
                "notification_sound": True
            },
            
            # Updates & Cloud
            "updates": {
                "auto_update_definitions": True,
                "auto_update_app": True,
                "cloud_threat_detection": True
            },
            
            # Performance
            "performance": {
                "cpu_usage_limit": 50,  # 10-100%
                "ram_optimization": True,
                "background_scan": True,
                "idle_scan_mode": True,
                "battery_saver_mode": False
            },
            
            # Quarantine & Threat Control
            "quarantine": {
                "auto_delete_after_days": 30,
                "quarantine_folder": "quarantine",
                "max_quarantine_size_mb": 1000,
                "enable_file_submission": False
            },
            
            # Privacy & Security
            "privacy": {
                "data_sharing": False,
                "log_retention_days": 30,
                "auto_log_clearing": True,
                "block_telemetry": True,
            },
            
            # Appearance & Interface
            "appearance": {
                "theme": "light",  # light, dark
                "ttkbootstrap_theme": "flatly",  # flatly, morph, cyborg, etc.
                "font_size": "normal",  # small, normal, large
                "high_contrast": False,
                "animations": True,
                "language": "en",
                "color_theme": "Light",  # Predefined or custom theme name
                "custom_colors": {
                    "primary_accent": "#1976D2",
                    "secondary_accent": "#42A5F5",
                    "background": "#F7F9FB",
                    "surface": "#FFFFFF",
                    "text_primary": "#222B45",
                    "text_secondary": "#6B778C",
                    "border": "#D1D9E6"
                },
                "sync_with_system": False,
                "use_custom_colors": False
            },
            
            # Advanced & Backup
            "advanced": {
                "admin_lock_enabled": False,
                "admin_password": "",
                "diagnostic_reporting": True,
                "debug_mode": False
            }
        }
    
    def load_settings(self) -> None:
        """Load settings from file"""
        try:
            if self.config_file.exists():
                with self._lock:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        loaded_settings = json.load(f)
                        # Merge with defaults to ensure all settings exist
                        self._merge_settings(loaded_settings)
            else:
                self.save_settings()  # Create default settings file
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def _merge_settings(self, loaded_settings: Dict[str, Any]) -> None:
        """Merge loaded settings with defaults"""
        def merge_dict(default: Dict, loaded: Dict) -> None:
            for key, value in default.items():
                if key in loaded:
                    if isinstance(value, dict) and isinstance(loaded[key], dict):
                        merge_dict(value, loaded[key])
                    else:
                        default[key] = loaded[key]
        
        merge_dict(self._settings, loaded_settings)
    
    def save_settings(self) -> None:
        """Save settings to file"""
        try:
            with self._lock:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self._settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get_setting(self, category: str, key: str, default: Any = None) -> Any:
        """Get a specific setting value"""
        try:
            return self._settings[category][key]
        except KeyError:
            return default
    
    def set_setting(self, category: str, key: str, value: Any) -> None:
        """Set a specific setting value"""
        if category not in self._settings:
            self._settings[category] = {}
        self._settings[category][key] = value
        self.save_settings()
    
    def get_category(self, category: str) -> Dict[str, Any]:
        """Get all settings for a category"""
        return self._settings.get(category, {})
    
    def set_category(self, category: str, settings: Dict[str, Any]) -> None:
        """Set all settings for a category"""
        self._settings[category] = settings
        self.save_settings()
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self._settings = self._load_default_settings()
        self.save_settings()
    
    def reset_all_settings(self) -> None:
        """Reset all settings to factory defaults"""
        self._settings = self._load_default_settings()
        self.save_settings()
    
    def get_all_settings(self, category: str = None) -> Dict[str, Any]:
        """Get all settings or settings for a specific category"""
        if category:
            return self._settings.get(category, {})
        return self._settings.copy()
    
    def apply_theme_settings(self, theme_name: str) -> None:
        """Apply theme settings to the application"""
        self.set_setting("appearance", "color_theme", theme_name)
        self.set_setting("appearance", "use_custom_colors", False)
        
        # Map theme names to ttkbootstrap themes
        theme_mapping = {
            "Light": "flatly",
            "Dark": "darkly", 
            "IronWall": "flatly",
            "Cyber": "cyborg",
            "Minimal Gray": "flatly",
            "High Contrast": "darkly"
        }
        
        ttkbootstrap_theme = theme_mapping.get(theme_name, "flatly")
        self.set_setting("appearance", "ttkbootstrap_theme", ttkbootstrap_theme)
    
    def apply_custom_colors(self, custom_colors: Dict[str, str]) -> None:
        """Apply custom color settings"""
        self.set_setting("appearance", "custom_colors", custom_colors)
        self.set_setting("appearance", "use_custom_colors", True)
    
    def export_settings(self, filepath: str) -> bool:
        """Export settings to a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error exporting settings: {e}")
            return False
    
    def import_settings(self, filepath: str) -> bool:
        """Import settings from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported_settings = json.load(f)
            self._merge_settings(imported_settings)
            self.save_settings()
            return True
        except Exception as e:
            print(f"Error importing settings: {e}")
            return False
    
    def validate_setting(self, category: str, key: str, value: Any) -> bool:
        """Validate a setting value"""
        # Add validation logic here
        if category == "performance" and key == "cpu_usage_limit":
            return isinstance(value, (int, float)) and 10 <= value <= 100
        elif category == "quarantine" and key == "max_quarantine_size_mb":
            return isinstance(value, (int, float)) and value > 0
        elif category == "privacy" and key == "log_retention_days":
            return isinstance(value, int) and value in [7, 30, 90]
        return True

# Global settings manager instance
_settings_manager = None

def get_settings_manager() -> SettingsManager:
    """Get the global settings manager instance"""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager 