"""
Test script for SchedulerPanel
"""

import tkinter as tk
from tkinter import ttk
from ui.scheduler_panel import SchedulerPanel

def test_scheduler_panel():
    """Test the SchedulerPanel in isolation"""
    root = tk.Tk()
    root.title("Scheduler Panel Test")
    root.geometry("1200x800")
    
    # Create the scheduler panel
    scheduler_panel = SchedulerPanel(root)
    scheduler_panel.pack(fill='both', expand=True)
    
    print("SchedulerPanel created successfully!")
    print("You should see the scheduler interface with:")
    print("- Header with title and Add Schedule button")
    print("- Left panel with scheduled scans table")
    print("- Right panel with statistics and upcoming scans")
    
    root.mainloop()

if __name__ == "__main__":
    test_scheduler_panel() 