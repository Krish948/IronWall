"""
Test script to verify settings panel display
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.settings_panel import SettingsPanel
from utils.settings_manager import get_settings_manager

def test_settings_panel():
    """Test the settings panel display"""
    # Create root window
    root = ttk.Window(themename='flatly')
    root.title("Settings Panel Test")
    root.geometry("1200x800")
    
    # Create settings panel
    settings_panel = SettingsPanel(root, None)
    
    # Add a close button
    close_btn = ttk.Button(root, text="Close", command=root.destroy, style="danger.TButton")
    close_btn.pack(pady=10)
    
    print("Settings panel created successfully!")
    print("If you can see the settings panel with tabs, it's working correctly.")
    
    root.mainloop()

if __name__ == "__main__":
    test_settings_panel() 