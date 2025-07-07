#!/usr/bin/env python3
"""
Test script for IronWall Antivirus Time Tracking Features
Tests the enhanced scan panel with time tracking, ETA, and status features
"""

import tkinter as tk
from ttkbootstrap import ttk
import time
import threading
from datetime import datetime, timedelta
from ui.scan_panel import ScanPanel

def test_time_tracking():
    """Test the time tracking features of the scan panel"""
    
    # Create test window
    root = ttk.Window(themename='flatly')
    root.title("IronWall Time Tracking Test")
    root.geometry("800x600")
    
    # Create scan panel
    scan_panel = ScanPanel(root)
    scan_panel.pack(fill='both', expand=True, padx=10, pady=10)
    
    def simulate_scan():
        """Simulate a scan with progress updates"""
        print("Starting simulated scan...")
        
        # Start time tracking
        scan_panel.start_time_tracking()
        scan_panel.total_files_estimate = 100  # Simulate 100 files
        
        # Simulate scan progress
        for i in range(100):
            if i % 10 == 0:  # Update every 10 files
                progress = (i / 100) * 100
                current_file = f"test_file_{i}.exe"
                stats = {
                    'files_scanned': i,
                    'threats_found': i // 20  # Simulate some threats
                }
                
                # Update progress in main thread
                root.after(0, lambda p=progress, f=current_file, s=stats: 
                          scan_panel.update_scan_progress(f, p, s))
                
                time.sleep(0.1)  # Simulate processing time
        
        # Complete scan
        scan_duration = 10  # Simulate 10 second scan
        root.after(0, lambda: scan_panel.set_scan_complete(100, 5, scan_duration))
        print("Simulated scan completed!")
    
    # Add test button
    test_btn = ttk.Button(root, text="Start Test Scan", 
                         command=lambda: threading.Thread(target=simulate_scan, daemon=True).start())
    test_btn.pack(pady=10)
    
    # Add info label
    info_label = ttk.Label(root, text="Click 'Start Test Scan' to test time tracking features", 
                          font=('Segoe UI', 12))
    info_label.pack(pady=10)
    
    def on_closing():
        """Handle window closing"""
        if hasattr(scan_panel, 'stop_time_tracking'):
            scan_panel.stop_time_tracking()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    print("Time tracking test window opened.")
    print("Features to test:")
    print("1. Elapsed time display (updates every second)")
    print("2. ETA calculation based on scan speed")
    print("3. Scan speed display (files per second)")
    print("4. Scan phase and status updates")
    print("5. Current file display")
    print("6. Progress bar with percentage")
    print("7. Results table with timestamps")
    
    root.mainloop()

if __name__ == "__main__":
    test_time_tracking() 