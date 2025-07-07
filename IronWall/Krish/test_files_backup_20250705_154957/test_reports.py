#!/usr/bin/env python3
"""
Test script for Reports Panel
"""

import tkinter as tk
import ttkbootstrap as ttk
from ui.reports_panel import ReportsPanel
from utils.system_monitor import SystemMonitor
from utils.threat_database import ThreatDatabase
from utils.quarantine import QuarantineManager

def test_reports_panel():
    """Test the reports panel functionality"""
    try:
        # Create root window
        root = ttk.Window(themename='darkly')
        root.title("Reports Panel Test")
        root.geometry("1200x800")
        
        # Initialize components
        system_monitor = SystemMonitor()
        threat_db = ThreatDatabase()
        quarantine_manager = QuarantineManager()
        
        # Create reports panel
        reports_panel = ReportsPanel(root, system_monitor, threat_db, quarantine_manager)
        reports_panel.pack(fill='both', expand=True)
        
        print("Reports Panel created successfully!")
        print("Features available:")
        print("- Security Reports tab")
        print("- Threats Blocked tab") 
        print("- Scan Reports tab")
        print("- Response Time tab")
        print("- Update Reports tab")
        print("- CSV Export functionality")
        print("- Filtering and search")
        
        # Run the application
        root.mainloop()
        
    except Exception as e:
        print(f"Error testing reports panel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_reports_panel() 