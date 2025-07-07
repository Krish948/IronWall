#!/usr/bin/env python3
"""
Test script for Analytics Panel Performance
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from ui.analytics_panel import AnalyticsPanel
from utils.system_monitor import SystemMonitor
from utils.threat_database import ThreatDatabase

def test_analytics_performance():
    """Test the analytics panel performance"""
    print("Starting Analytics Panel Performance Test...")
    
    # Create root window
    root = tk.Tk()
    root.title("Analytics Panel Performance Test")
    root.geometry("1000x700")
    
    # Initialize components
    system_monitor = SystemMonitor()
    threat_db = ThreatDatabase()
    
    # Create analytics panel
    print("Creating Analytics Panel...")
    start_time = time.time()
    
    analytics = AnalyticsPanel(root, system_monitor, threat_db)
    analytics.pack(fill='both', expand=True)
    
    end_time = time.time()
    print(f"Analytics Panel created in {end_time - start_time:.2f} seconds")
    
    # Add a test button
    def test_refresh():
        print("Testing refresh...")
        start = time.time()
        analytics._refresh_panel()
        end = time.time()
        print(f"Refresh completed in {end - start:.2f} seconds")
    
    test_btn = ttk.Button(root, text="Test Refresh", command=test_refresh)
    test_btn.pack(side='bottom', pady=10)
    
    # Run the application
    print("Starting main loop...")
    root.mainloop()

if __name__ == "__main__":
    test_analytics_performance() 