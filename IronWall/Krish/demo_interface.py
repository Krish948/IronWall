#!/usr/bin/env python3
"""
IronWall Antivirus - Interface Options Demo
Demonstrates the fully functional settings panel interface
"""

import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ui.settings_panel import SettingsPanel

def demo_interface():
    """Demonstrate the settings panel interface"""
    
    # Create main window
    root = ttk.Window(themename="flatly")
    root.title("🛡️ IronWall Antivirus - Settings Panel Demo")
    root.geometry("1400x900")
    
    # Add a header
    header_frame = ttk.Frame(root)
    header_frame.pack(fill=X, padx=20, pady=10)
    
    ttk.Label(header_frame, text="IronWall Antivirus Settings Panel", 
             font=("Segoe UI", 24, "bold")).pack()
    ttk.Label(header_frame, text="Professional antivirus configuration interface", 
             font=("Segoe UI", 12)).pack()
    
    # Create settings panel
    settings_panel = SettingsPanel(root, None)
    
    # Add instructions
    instructions_frame = ttk.Frame(root)
    instructions_frame.pack(fill=X, padx=20, pady=10)
    
    ttk.Label(instructions_frame, text="💡 Interface Features:", 
             font=("Segoe UI", 14, "bold")).pack(anchor=W)
    
    features = [
        "🛡️ Protection: Real-time protection, firewall, USB protection",
        "🧪 Scan Control: Scan types, exclusions, compressed files",
        "📅 Scheduling: Automated scans, frequency, timing",
        "🔔 Notifications: Alerts, silent mode, sounds",
        "🌐 Updates: Auto-updates, cloud detection",
        "📊 Performance: CPU limits, RAM optimization, battery saver",
        "🚫 Quarantine: Auto-delete, folder management, file submission",
        "🔒 Privacy: Data sharing, log retention, telemetry",
        "🎨 Appearance: Themes, colors, fonts, animations",
    ]
    
    for feature in features:
        ttk.Label(instructions_frame, text=feature, 
                 font=("Segoe UI", 10)).pack(anchor=W, padx=20)
    
    def on_closing():
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    demo_interface() 