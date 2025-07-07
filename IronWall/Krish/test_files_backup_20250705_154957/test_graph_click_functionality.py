#!/usr/bin/env python3
"""
Test script for graph click functionality in analytics panel
"""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.analytics_panel import AnalyticsPanel
from utils.system_monitor import SystemMonitor
from utils.threat_database import ThreatDatabase

def test_graph_click_functionality():
    """Test the graph click functionality"""
    root = tk.Tk()
    root.title("Graph Click Functionality Test")
    root.geometry("800x600")
    
    # Create mock system monitor and threat database
    system_monitor = SystemMonitor()
    threat_db = ThreatDatabase()
    
    # Create analytics panel
    analytics_panel = AnalyticsPanel(root, system_monitor, threat_db)
    analytics_panel.pack(fill='both', expand=True)
    
    # Add instructions
    instructions = ttk.Label(root, text="Instructions:\n1. Click on any graph to expand it to full screen\n2. Click on the fullscreen graph to minimize it\n3. Press ESC to exit fullscreen\n4. Use the ⛶ button for alternative fullscreen access", 
                           font=('Segoe UI', 12), justify='left')
    instructions.pack(side='bottom', fill='x', padx=10, pady=10)
    
    print("Test application started!")
    print("Click on any graph in the Analytics tab to test the expand/minimize functionality.")
    
    root.mainloop()

if __name__ == "__main__":
    test_graph_click_functionality() 