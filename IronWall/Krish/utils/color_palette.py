"""
IronWall Antivirus - Color Palette Manager
Manages predefined themes and custom color schemes
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from tkinter import colorchooser
import tkinter as tk

class ColorPalette:
    """Manages color themes and palettes for IronWall Antivirus"""
    
    def __init__(self, themes_file: str = "themes.json"):
        self.themes_file = Path(themes_file)
        self.predefined_themes = self._load_predefined_themes()
        self.custom_themes = self._load_custom_themes()
        
    def _load_predefined_themes(self) -> Dict[str, Dict[str, str]]:
        """Load predefined color themes"""
        return {
            "Light": {
                "name": "Light",
                "description": "Clean, modern light theme",
                "primary_accent": "#1976D2",
                "secondary_accent": "#42A5F5",
                "background": "#F7F9FB",
                "surface": "#FFFFFF",
                "text_primary": "#222B45",
                "text_secondary": "#6B778C",
                "border": "#D1D9E6",
                "success": "#43A047",
                "warning": "#FFA000",
                "danger": "#D32F2F",
                "info": "#1976D2"
            },
            "Dark": {
                "name": "Dark",
                "description": "Professional dark theme",
                "primary_accent": "#00D4FF",
                "secondary_accent": "#4FC3F7",
                "background": "#0A0A0F",
                "surface": "#1A1A2E",
                "text_primary": "#E8E8E8",
                "text_secondary": "#A0A0A0",
                "border": "#2A2A3E",
                "success": "#00FF88",
                "warning": "#FFB800",
                "danger": "#FF0055",
                "info": "#00D4FF"
            },
            "IronWall": {
                "name": "IronWall",
                "description": "Glassmorphic IronWall theme",
                "primary_accent": "#FF6B35",
                "secondary_accent": "#F7931E",
                "background": "#F7F9FB",
                "surface": "#FFFFFF",
                "text_primary": "#2C3E50",
                "text_secondary": "#7F8C8D",
                "border": "#D1D9E6",
                "success": "#27AE60",
                "warning": "#F39C12",
                "danger": "#E74C3C",
                "info": "#3498DB"
            },
            "Cyber": {
                "name": "Cyber",
                "description": "Futuristic cyberpunk theme",
                "primary_accent": "#00FF41",
                "secondary_accent": "#00D4FF",
                "background": "#0A0A0F",
                "surface": "#1A1A2E",
                "text_primary": "#00FF41",
                "text_secondary": "#00D4FF",
                "border": "#00FF41",
                "success": "#00FF41",
                "warning": "#FFB800",
                "danger": "#FF0055",
                "info": "#00D4FF"
            },
            "Minimal Gray": {
                "name": "Minimal Gray",
                "description": "Minimalist grayscale theme",
                "primary_accent": "#424242",
                "secondary_accent": "#757575",
                "background": "#FAFAFA",
                "surface": "#FFFFFF",
                "text_primary": "#212121",
                "text_secondary": "#757575",
                "border": "#E0E0E0",
                "success": "#4CAF50",
                "warning": "#FF9800",
                "danger": "#F44336",
                "info": "#2196F3"
            },
            "High Contrast": {
                "name": "High Contrast",
                "description": "Accessibility-focused high contrast theme",
                "primary_accent": "#FFFFFF",
                "secondary_accent": "#FFFF00",
                "background": "#000000",
                "surface": "#000000",
                "text_primary": "#FFFFFF",
                "text_secondary": "#FFFF00",
                "border": "#FFFFFF",
                "success": "#00FF00",
                "warning": "#FFFF00",
                "danger": "#FF0000",
                "info": "#00FFFF"
            },
            "Ocean Blue": {
                "name": "Ocean Blue",
                "description": "Cool blue and teal ocean-inspired theme",
                "primary_accent": "#0077B6",
                "secondary_accent": "#00B4D8",
                "background": "#CAF0F8",
                "surface": "#90E0EF",
                "text_primary": "#03045E",
                "text_secondary": "#0077B6",
                "border": "#00B4D8",
                "success": "#43A047",
                "warning": "#FFD166",
                "danger": "#EF476F",
                "info": "#118AB2"
            },
            "Solarized": {
                "name": "Solarized",
                "description": "Popular Solarized color scheme for coding",
                "primary_accent": "#268BD2",
                "secondary_accent": "#2AA198",
                "background": "#FDF6E3",
                "surface": "#EEE8D5",
                "text_primary": "#657B83",
                "text_secondary": "#93A1A1",
                "border": "#839496",
                "success": "#859900",
                "warning": "#B58900",
                "danger": "#DC322F",
                "info": "#268BD2"
            },
            "Forest Green": {
                "name": "Forest Green",
                "description": "Nature-inspired theme with deep greens and earthy browns",
                "primary_accent": "#388E3C",
                "secondary_accent": "#8D6E63",
                "background": "#E8F5E9",
                "surface": "#C8E6C9",
                "text_primary": "#1B5E20",
                "text_secondary": "#4E342E",
                "border": "#A5D6A7",
                "success": "#43A047",
                "warning": "#FBC02D",
                "danger": "#D84315",
                "info": "#388E3C"
            },
            "Purple Night": {
                "name": "Purple Night",
                "description": "Modern dark theme with purple and magenta highlights",
                "primary_accent": "#8E24AA",
                "secondary_accent": "#D500F9",
                "background": "#1A0033",
                "surface": "#311B92",
                "text_primary": "#F3E5F5",
                "text_secondary": "#B39DDB",
                "border": "#7C43BD",
                "success": "#00E676",
                "warning": "#FFD600",
                "danger": "#FF1744",
                "info": "#651FFF"
            },
            "Sunset Orange": {
                "name": "Sunset Orange",
                "description": "Warm, energetic theme with orange and red hues",
                "primary_accent": "#FF7043",
                "secondary_accent": "#FFB300",
                "background": "#FFF3E0",
                "surface": "#FFE0B2",
                "text_primary": "#BF360C",
                "text_secondary": "#FF8A65",
                "border": "#FFB74D",
                "success": "#43A047",
                "warning": "#FFA000",
                "danger": "#D32F2F",
                "info": "#FF7043"
            }
        }
    
    def _load_custom_themes(self) -> Dict[str, Dict[str, str]]:
        """Load custom themes from file"""
        try:
            if self.themes_file.exists():
                with open(self.themes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading custom themes: {e}")
        return {}
    
    def save_custom_themes(self) -> None:
        """Save custom themes to file"""
        try:
            with open(self.themes_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_themes, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving custom themes: {e}")
    
    def get_theme(self, theme_name: str) -> Optional[Dict[str, str]]:
        """Get a theme by name (predefined or custom)"""
        if theme_name in self.predefined_themes:
            return self.predefined_themes[theme_name]
        elif theme_name in self.custom_themes:
            return self.custom_themes[theme_name]
        return None
    
    def get_all_themes(self) -> Dict[str, Dict[str, str]]:
        """Get all available themes"""
        all_themes = {}
        all_themes.update(self.predefined_themes)
        all_themes.update(self.custom_themes)
        return all_themes
    
    def get_available_themes(self) -> List[str]:
        """Get list of available theme names (alias for get_theme_names)"""
        return self.get_theme_names()
    
    def get_theme_names(self) -> List[str]:
        """Get list of all theme names"""
        return list(self.get_all_themes().keys())
    
    def create_custom_theme(self, name: str, colors: Dict[str, str], description: str = "") -> bool:
        """Create a new custom theme"""
        try:
            theme = {
                "name": name,
                "description": description,
                **colors
            }
            self.custom_themes[name] = theme
            self.save_custom_themes()
            return True
        except Exception as e:
            print(f"Error creating custom theme: {e}")
            return False
    
    def update_custom_theme(self, name: str, colors: Dict[str, str], description: str = "") -> bool:
        """Update an existing custom theme"""
        if name in self.custom_themes:
            return self.create_custom_theme(name, colors, description)
        return False
    
    def delete_custom_theme(self, name: str) -> bool:
        """Delete a custom theme"""
        try:
            if name in self.custom_themes:
                del self.custom_themes[name]
                self.save_custom_themes()
                return True
        except Exception as e:
            print(f"Error deleting custom theme: {e}")
        return False
    
    def export_theme(self, theme_name: str, filepath: str) -> bool:
        """Export a theme to a file"""
        try:
            theme = self.get_theme(theme_name)
            if theme:
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(theme, f, indent=2, ensure_ascii=False)
                return True
        except Exception as e:
            print(f"Error exporting theme: {e}")
        return False
    
    def import_theme(self, filepath: str) -> bool:
        """Import a theme from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                theme = json.load(f)
            
            if "name" in theme:
                self.custom_themes[theme["name"]] = theme
                self.save_custom_themes()
                return True
        except Exception as e:
            print(f"Error importing theme: {e}")
        return False
    
    def get_color_picker(self, parent, title: str = "Choose Color", initial_color: str = "#000000") -> Optional[str]:
        """Open a color picker dialog"""
        try:
            color = colorchooser.askcolor(initial_color, title=title)
            if color[1]:  # color[1] contains the hex color
                return color[1]
        except Exception as e:
            print(f"Error opening color picker: {e}")
        return None
    
    def validate_color(self, color: str) -> bool:
        """Validate if a color string is valid"""
        if not color:
            return False
        
        # Check if it's a valid hex color
        if color.startswith('#'):
            if len(color) == 7 and all(c in '0123456789ABCDEFabcdef' for c in color[1:]):
                return True
        
        # Check if it's a valid rgba color
        if color.startswith('rgba(') and color.endswith(')'):
            try:
                parts = color[5:-1].split(',')
                if len(parts) == 4:
                    r, g, b, a = parts
                    if (0 <= float(r.strip()) <= 255 and 
                        0 <= float(g.strip()) <= 255 and 
                        0 <= float(b.strip()) <= 255 and 
                        0 <= float(a.strip()) <= 1):
                        return True
            except:
                pass
        
        return False
    
    def get_theme_preview_colors(self, theme_name: str) -> List[str]:
        """Get a list of colors for theme preview"""
        theme = self.get_theme(theme_name)
        if not theme:
            return []
        
        return [
            theme.get("primary_accent", "#000000"),
            theme.get("secondary_accent", "#000000"),
            theme.get("background", "#000000"),
            theme.get("surface", "#000000"),
            theme.get("text_primary", "#000000")
        ]
    
    def get_theme_colors(self, theme_name: str) -> Dict[str, str]:
        """Get all colors for a specific theme"""
        theme = self.get_theme(theme_name)
        if theme:
            return theme
        return {}

# Global instance
_color_palette = None

def get_color_palette() -> ColorPalette:
    """Get the global color palette instance"""
    global _color_palette
    if _color_palette is None:
        _color_palette = ColorPalette()
    return _color_palette 