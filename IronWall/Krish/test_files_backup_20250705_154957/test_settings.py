"""
Test script for IronWall Settings Panel
"""

import tkinter as tk
import ttkbootstrap as ttk
from ui.settings_panel import SettingsPanel
from utils.settings_manager import get_settings_manager

def test_settings_panel():
    """Test the settings panel in a standalone window"""
    root = ttk.Window(themename="flatly")
    root.title("IronWall Settings Panel Test")
    root.geometry("1200x800")
    
    # Create settings panel
    settings_panel = SettingsPanel(root, None)
    
    # Test settings manager
    sm = get_settings_manager()
    print("Current settings:", sm.get_all_settings())
    
    root.mainloop()

if __name__ == "__main__":
    test_settings_panel() 